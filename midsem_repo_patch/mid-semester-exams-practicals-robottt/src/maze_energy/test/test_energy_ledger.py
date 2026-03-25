from maze_energy.ledger import EnergyLedger


def test_energy_ledger_counts_and_totals():
    ledger = EnergyLedger()
    assert ledger.apply("start_moving")
    assert ledger.apply("move_forward")
    assert ledger.apply("stop_moving")
    assert ledger.energy_used == 6.5
    assert ledger.remaining_energy == 993.5
    assert ledger.action_counts["move_forward"] == 1
