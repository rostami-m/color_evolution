"""
model.py — retinal-bottleneck CNN and world-recovery variant.

conv1 (the "retinal" layer): 3 LMS channels → K feature maps, 3×3.
This is the layer whose filters we analyse for single-/double-opponent structure.
A narrow 1×1 bottleneck mimics the optic-nerve bandwidth constraint.
"""
import torch
import torch.nn as nn

PATCH = 9        # spatial patch side length
CENTER = slice(3, 6)  # central 3×3 target region within the 9×9 patch


class RetinalCNN(nn.Module):
    """Behaving-objective network: classifies the central surface into two material
    categories while the illuminant varies freely across trials."""
    def __init__(self, k1=8, bottleneck=4, n_classes=2):
        super().__init__()
        self.conv1 = nn.Conv2d(3, k1, kernel_size=3, padding=1, bias=True)
        self.act = nn.ReLU()
        self.bottleneck = nn.Conv2d(k1, bottleneck, kernel_size=1, bias=True)
        self.head = nn.Sequential(
            nn.Linear(2 * bottleneck, 16), nn.ReLU(),
            nn.Linear(16, n_classes),
        )
        self.center = CENTER

    def features(self, x):
        h = self.act(self.conv1(x))
        return self.act(self.bottleneck(h))

    def _pool(self, h):
        c = self.center
        center_feat = h[:, :, c, c].mean(dim=(2, 3))
        total = h.mean(dim=(2, 3))
        return torch.cat([center_feat, total], dim=1)

    def forward(self, x):
        return self.head(self._pool(self.features(x)))


class WorldRecoveryCNN(RetinalCNN):
    """World-recovery-objective network: identical body, regresses illuminant CCT."""
    def __init__(self, k1=8, bottleneck=4):
        super().__init__(k1=k1, bottleneck=bottleneck, n_classes=2)
        self.reg_head = nn.Sequential(
            nn.Linear(2 * bottleneck, 16), nn.ReLU(), nn.Linear(16, 1),
        )

    def forward(self, x):
        return self.reg_head(self._pool(self.features(x)))
