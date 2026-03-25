# rover_energy

Tracks the exact exam energy categories by subscribing to `/motion_event`.

This avoids the over-counting problem that happens when energy is computed from raw `/cmd_vel` traffic.
