from dataclasses import dataclass, field
from typing import Dict

ENERGY_COSTS = {
    "move_forward": 5.0,
    "move_backward": 8.0,
    "turn_left": 3.0,
    "turn_right": 3.0,
    "rotate_180": 6.0,
    "start_moving": 1.0,
    "stop_moving": 0.5,
}


@dataclass
class EnergyLedger:
    total_budget: float = 1000.0
    energy_used: float = 0.0
    action_counts: Dict[str, int] = field(
        default_factory=lambda: {name: 0 for name in ENERGY_COSTS}
    )

    @property
    def remaining_energy(self) -> float:
        return self.total_budget - self.energy_used

    def can_apply(self, action: str) -> bool:
        return self.remaining_energy >= ENERGY_COSTS[action]

    def apply(self, action: str) -> bool:
        if action not in ENERGY_COSTS:
            raise KeyError(f"Unknown action '{action}'")
        if not self.can_apply(action):
            return False
        self.energy_used += ENERGY_COSTS[action]
        self.action_counts[action] += 1
        return True

    def to_dict(self) -> Dict[str, object]:
        return {
            "total_budget": self.total_budget,
            "energy_used": self.energy_used,
            "energy_remaining": self.remaining_energy,
            "action_counts": dict(self.action_counts),
        }
