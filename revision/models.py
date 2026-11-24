"""Geometry-aware versions of the published networks, with CPU-only training."""
from dataclasses import dataclass
import copy
import numpy as np
import torch
from torch import nn


@dataclass(frozen=True)
class Geometry:
    patch_size: int = 9
    target_size: int = 3

    def __post_init__(self):
        if (self.patch_size < 9 or self.patch_size % 2 != 1
                or self.target_size % 2 != 1 or self.target_size < 3
                or self.target_size >= self.patch_size
                or (self.patch_size - self.target_size) % 2):
            raise ValueError('Geometry requires centered odd patch and target sizes.')

    @property
    def center(self):
        start = (self.patch_size - self.target_size) // 2
        return slice(start, start + self.target_size)

    def ring(self):
        mask = np.ones((self.patch_size, self.patch_size), dtype=bool)
        mask[self.center, self.center] = False
        return mask


class RevisionCNN(nn.Module):
    def __init__(self, geometry=Geometry(), k1=8, bottleneck=4,
                 objective='classify', readout='base', b=1., dilation=1):
        super().__init__()
        self.geometry, self.center = geometry, geometry.center
        self.dilation, self.readout, self.objective = int(dilation), readout, objective
        self.conv1 = nn.Conv2d(3, k1, 3, padding=dilation, dilation=dilation)
        self.bottleneck = nn.Conv2d(k1, bottleneck, 1)
        self.act = nn.ReLU()
        if readout == 'learned_b':
            self.b = nn.Parameter(torch.tensor(0.))  # unconstrained, as in released code
        elif readout == 'fixed_b':
            self.register_buffer('b', torch.tensor(float(b)))
        elif readout in ('spatial', 'spatial_coarse'):
            side = geometry.patch_size if readout == 'spatial' else 9
            self.spatial = nn.Parameter(torch.randn(1, 1, side, side) * .01)
        elif readout not in ('base', 'center_only'):
            raise ValueError(f'Unknown readout: {readout}')
        dim = 2 * bottleneck if readout == 'base' else bottleneck
        self.head = nn.Sequential(nn.Linear(dim, 16), nn.ReLU(),
                                  nn.Linear(16, 1 if objective == 'regress' else 2))

    def features(self, x):
        return self.act(self.bottleneck(self.act(self.conv1(x))))

    def representation(self, x):
        h = self.features(x)
        side = h.shape[-1]
        target = round(side * self.geometry.target_size / self.geometry.patch_size)
        if target % 2 == 0:
            target += 1
        start = (side - target) // 2
        c = slice(start, start + target)
        center = h[:, :, c, c].mean((2, 3))
        if self.readout == 'base':
            return torch.cat((center, h.mean((2, 3))), 1)
        if self.readout == 'center_only':
            return center
        if self.readout in ('fixed_b', 'learned_b'):
            surround = (h.sum((2, 3)) - h[:, :, c, c].sum((2, 3))) / (side**2-target**2)
            return center - self.b * surround
        spatial = self.spatial
        if spatial.shape[-1] != side:
            spatial = torch.nn.functional.interpolate(spatial, size=(side, side), mode='nearest')
            # Preserve total readout weight for a fixed coarse map.
            spatial = spatial * (self.spatial.shape[-1] / side)**2
        return (h * spatial).sum((2, 3))

    def forward(self, x):
        return self.head(self.representation(x))


def make_model(config, seed, objective='classify', readout=None):
    torch.manual_seed(int(seed))
    net = RevisionCNN(Geometry(config['patch_size'], config['patch_size']//3),
                      config.get('k1', 8), config.get('bottleneck', 4),
                      objective, readout or config.get('readout', 'base'),
                      config.get('b', 1.), config.get('dilation', 1))
    assert all(p.device.type == 'cpu' for p in net.parameters())
    return net


def train(net, X, y, cct, seed, epochs=80, lr=.002, batch_size=256,
          loss_weights=None, sampling_weights=None):
    """Fixed-update training; sampling/loss manipulations are explicit."""
    torch.manual_seed(int(seed))
    generator = torch.Generator(device='cpu').manual_seed(int(seed))
    X = torch.as_tensor(X, dtype=torch.float32, device='cpu')
    target = (torch.as_tensor((cct-14000.)/7000., dtype=torch.float32)[:, None]
              if net.objective == 'regress' else torch.as_tensor(y, dtype=torch.long))
    weights = None if loss_weights is None else torch.as_tensor(loss_weights, dtype=torch.float32)
    if weights is not None:
        weights = weights / weights.mean()
    sample = None if sampling_weights is None else torch.as_tensor(sampling_weights, dtype=torch.float32)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    net.train()
    curve = []
    for epoch in range(epochs):
        order = (torch.randperm(len(X), generator=generator) if sample is None else
                 torch.multinomial(sample, len(X), replacement=True, generator=generator))
        total, correct = 0., 0
        for ix in order.split(batch_size):
            opt.zero_grad(set_to_none=True)
            pred = net(X[ix])
            losses = ((pred-target[ix]).square().mean(1) if net.objective == 'regress' else
                      nn.functional.cross_entropy(pred, target[ix], reduction='none'))
            loss = losses.mean() if weights is None else (losses*weights[ix]).mean()
            if not torch.isfinite(loss):
                raise FloatingPointError('Non-finite training loss')
            loss.backward()
            opt.step()
            total += float(loss.detach()) * len(ix)
            if net.objective != 'regress':
                correct += int((pred.argmax(1) == target[ix]).sum())
        curve.append({'epoch': epoch+1, 'loss': total/len(X),
                      'sampled_class_counts': None if net.objective == 'regress' else torch.bincount(target[order], minlength=2).tolist(),
                      'sampled_train_accuracy': None if net.objective == 'regress' else correct/len(X)})
    return curve


@torch.no_grad()
def evaluate(net, X, y, cct, batch_size=128):
    net.eval()
    pred = torch.cat([net(torch.as_tensor(X[i:i+batch_size], dtype=torch.float32))
                      for i in range(0, len(X), batch_size)]).numpy()
    if net.objective == 'regress':
        kelvin = pred[:, 0]*7000. + 14000.
        sse = np.sum((kelvin-cct)**2)
        return {'rmse_kelvin': float(np.sqrt(np.mean((kelvin-cct)**2))),
                'r2': float(1.-sse/np.sum((cct-cct.mean())**2))}
    labels = pred.argmax(1)
    recalls = [float(np.mean(labels[y == c] == c)) for c in (0, 1)]
    return {'accuracy': float(np.mean(labels == y)), 'balanced_accuracy': float(np.mean(recalls)),
            'class_recall': recalls, 'n': len(y)}
