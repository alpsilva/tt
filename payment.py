from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from user import User


class Payment:

    def __init__(self, amount: float, actor: User, target: User, note: str):
        self.id = str(uuid.uuid4())
        self.amount = float(amount)
        self.actor = actor
        self.target = target
        self.note = note

    def __str__(self):
        return f"{self.actor.username} paid {self.target.username} ${round(self.amount, 2)} for {self.note}"
