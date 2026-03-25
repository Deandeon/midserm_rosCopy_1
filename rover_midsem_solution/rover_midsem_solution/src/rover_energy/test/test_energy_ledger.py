from rover_energy.ledger import EnergyLedger


def test_energy_ledger_counts_discrete_actions():
    ledger = EnergyLedger()

    assert ledger.apply("start_moving")
    assert ledger.apply("move_forward")
    assert ledger.apply("stop_moving")

    assert ledger.energy_used == 6.5
    assert ledger.remaining_energy == 993.5
    assert ledger.action_counts["start_moving"] == 1
    assert ledger.action_counts["move_forward"] == 1
    assert ledger.action_counts["stop_moving"] == 1


def test_energy_ledger_rejects_when_budget_is_exhausted():
    ledger = EnergyLedger(total_budget=4.0)
    ok = ledger.apply("move_forward")
    assert ok is False
    assert ledger.energy_used == 0.0
