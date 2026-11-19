"""
training.py — device detection, training loops, and evaluation helpers.

Device selection prefers CUDA > MPS > CPU. Override by setting
the DEVICE environment variable (e.g. DEVICE=cpu, DEVICE=cuda:1, DEVICE=mps).
"""
import os
import time
import torch
import torch.nn as nn
import numpy as np


def get_device():
    """Return the best available torch device, respecting DEVICE env var."""
    override = os.environ.get("DEVICE", "").strip()
    if override:
        return torch.device(override)
    if torch.cuda.is_available():
        return torch.device("cuda")
    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")


def train_classifier(net, X, y, dev, epochs=80, lr=2e-3, bs=256, seed=0):
    """Cross-entropy training for the behaving-objective network."""
    torch.manual_seed(seed)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    lossf = nn.CrossEntropyLoss()
    Xt = torch.as_tensor(X, device=dev)
    yt = torch.as_tensor(y, device=dev)
    net.train()
    for _ in range(epochs):
        perm = torch.randperm(len(Xt), device=dev)
        for i in range(0, len(Xt), bs):
            idx = perm[i:i + bs]
            opt.zero_grad()
            lossf(net(Xt[idx]), yt[idx]).backward()
            opt.step()
    return net


def train_world_recovery(net, X, cct, dev, epochs=80, lr=2e-3, bs=256, seed=0):
    """MSE training for the world-recovery-objective network (regresses CCT)."""
    torch.manual_seed(seed)
    opt = torch.optim.Adam(net.parameters(), lr=lr)
    lossf = nn.MSELoss()
    Xt = torch.as_tensor(X, device=dev)
    # normalise CCT to roughly [-1, 1]
    t = torch.as_tensor((cct - 14000.0) / 7000.0, dtype=torch.float32, device=dev)[:, None]
    net.train()
    for _ in range(epochs):
        perm = torch.randperm(len(Xt), device=dev)
        for i in range(0, len(Xt), bs):
            idx = perm[i:i + bs]
            opt.zero_grad()
            lossf(net(Xt[idx]), t[idx]).backward()
            opt.step()
    return net


@torch.no_grad()
def accuracy(net, X, y, dev):
    net.eval()
    Xt = torch.as_tensor(X, device=dev)
    yt = torch.as_tensor(y, device=dev)
    return (net(Xt).argmax(1) == yt).float().mean().item()


class Budget:
    """Wall-clock time budget. Experiment loops call .ok() before each unit of work."""
    def __init__(self, seconds):
        self.seconds = float(seconds)
        self._t0 = time.time()

    def elapsed(self):
        return time.time() - self._t0

    def remaining(self):
        return max(0.0, self.seconds - self.elapsed())

    def ok(self, margin=0.0):
        return self.remaining() > margin

    def frac(self):
        return min(1.0, self.elapsed() / self.seconds) if self.seconds > 0 else 1.0
