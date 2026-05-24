"""PyTorch two-tower encoders for user and item retrieval."""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class ItemTower(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 128, output_dim: int = 64) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return F.normalize(self.net(features), p=2, dim=-1)


class UserTower(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int = 128, output_dim: int = 64) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim),
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return F.normalize(self.net(features), p=2, dim=-1)


class TwoTowerModel(nn.Module):
    def __init__(
        self,
        item_input_dim: int,
        user_input_dim: int,
        hidden_dim: int = 128,
        output_dim: int = 64,
    ) -> None:
        super().__init__()
        self.item_tower = ItemTower(item_input_dim, hidden_dim, output_dim)
        self.user_tower = UserTower(user_input_dim, hidden_dim, output_dim)

    def forward(
        self,
        user_features: torch.Tensor,
        item_features: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        return self.user_tower(user_features), self.item_tower(item_features)


def infonce_loss(
    user_embeddings: torch.Tensor,
    item_embeddings: torch.Tensor,
    temperature: float = 0.07,
) -> torch.Tensor:
    logits = user_embeddings @ item_embeddings.T
    logits = logits / temperature
    labels = torch.arange(logits.size(0), device=logits.device)
    return F.cross_entropy(logits, labels)
