"""
cs_model.py — center-surround readout variants used across §2.3 experiments.

CSReadoutCNN: fixed antagonism parameter b (can be swept).
LearnableBCNN: b is a free learnable scalar (tests whether behaving selects antagonism).
FreeSpatialCNN: fully learnable spatial weight map (measures emergent antagonism post-hoc).
"""
import numpy as np
import torch
import torch.nn as nn

from src.model import PATCH, CENTER


class CSReadoutCNN(nn.Module):
    """Shared conv body with an antagonistic center-surround readout:
    z = center_pool − b × surround_ring_pool.

    b=0 : pure center pool (assimilation regime)
    b>0 : increasing antagonism → contrast regime
    """
    def __init__(self, b=1.0, k1=8, bottleneck=4):
        super().__init__()
        self.conv1 = nn.Conv2d(3, k1, 3, padding=1, bias=True)
        self.act = nn.ReLU()
        self.bottleneck = nn.Conv2d(k1, bottleneck, 1, bias=True)
        self.head = nn.Sequential(nn.Linear(bottleneck, 16), nn.ReLU(), nn.Linear(16, 2))
        self.center = CENTER
        self.b = b
        msk = np.ones((PATCH, PATCH), np.float32); msk[CENTER, CENTER] = 0.0
        self.register_buffer("ring", torch.tensor(msk))

    def features(self, x):
        return self.act(self.bottleneck(self.act(self.conv1(x))))

    def _readout(self, h):
        c = self.center
        center = h[:, :, c, c].mean(dim=(2, 3))
        ring = (h * self.ring).sum(dim=(2, 3)) / self.ring.sum()
        return center - self.b * ring

    def forward(self, x):
        return self.head(self._readout(self.features(x)))


class LearnableBCNN(nn.Module):
    """Like CSReadoutCNN but b is a free nn.Parameter, initialised at b_init."""
    def __init__(self, k1=8, bottleneck=4, b_init=0.0):
        super().__init__()
        self.conv1 = nn.Conv2d(3, k1, 3, padding=1); self.act = nn.ReLU()
        self.bottleneck = nn.Conv2d(k1, bottleneck, 1)
        self.head = nn.Sequential(nn.Linear(bottleneck, 16), nn.ReLU(), nn.Linear(16, 2))
        self.b = nn.Parameter(torch.tensor(float(b_init)))
        msk = np.ones((PATCH, PATCH), np.float32); msk[CENTER, CENTER] = 0.0
        self.register_buffer("ring", torch.tensor(msk))

    def features(self, x):
        return self.act(self.bottleneck(self.act(self.conv1(x))))

    def forward(self, x):
        h = self.features(x)
        c = CENTER
        center = h[:, :, c, c].mean(dim=(2, 3))
        ring = (h * self.ring).sum(dim=(2, 3)) / self.ring.sum()
        return self.head(center - self.b * ring)


class FreeSpatialCNN(nn.Module):
    """Fully learnable spatial readout weight map. Emergent antagonism is measured
    as (mean center weight) − (mean surround weight) post-hoc."""
    def __init__(self, k1=8, bottleneck=4):
        super().__init__()
        self.conv1 = nn.Conv2d(3, k1, 3, padding=1); self.act = nn.ReLU()
        self.bottleneck = nn.Conv2d(k1, bottleneck, 1)
        self.spatial = nn.Parameter(torch.randn(1, 1, PATCH, PATCH) * 0.01)
        self.head = nn.Sequential(nn.Linear(bottleneck, 16), nn.ReLU(), nn.Linear(16, 2))

    def features(self, x):
        return self.act(self.bottleneck(self.act(self.conv1(x))))

    def forward(self, x):
        h = self.features(x)
        z = (h * self.spatial).sum(dim=(2, 3))
        return self.head(z)

    def emergent_antagonism(self):
        w = self.spatial.detach().cpu().numpy()[0, 0]
        c = CENTER
        center_w = w[c, c].mean()
        ring_mask = np.ones((PATCH, PATCH), bool); ring_mask[c, c] = False
        surround_w = w[ring_mask].mean()
        return float(center_w - surround_w), float(center_w), float(surround_w)


def train_cs(net, X, y, dev, seed, epochs=80):
    """Standard Adam/CrossEntropy training for CS-readout networks."""
    import torch.nn as nn
    torch.manual_seed(seed)
    opt = torch.optim.Adam(net.parameters(), lr=2e-3)
    lossf = nn.CrossEntropyLoss()
    Xt = torch.as_tensor(X, device=dev)
    yt = torch.as_tensor(y, device=dev)
    for _ in range(epochs):
        perm = torch.randperm(len(Xt), device=dev)
        for i in range(0, len(Xt), 256):
            idx = perm[i:i + 256]
            opt.zero_grad(); lossf(net(Xt[idx]), yt[idx]).backward(); opt.step()
    return net


@torch.no_grad()
def cs_repr(net, X, dev):
    net.eval()
    Xt = torch.as_tensor(X, device=dev)
    return net._readout(net.features(Xt)).cpu().numpy()
