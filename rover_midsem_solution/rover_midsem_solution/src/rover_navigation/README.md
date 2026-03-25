# rover_navigation

Implements a practical maze solver for the exam.

## Implemented behavior

- waits for the `S` key before doing anything
- reads `/scan` and `/odom`
- uses a **left-hand wall follower**
- moves in **discrete primitives**
- publishes motion events:
  - `start_moving`
  - `move_forward`
  - `move_backward`
  - `turn_left`
  - `turn_right`
  - `rotate_180`
  - `stop_moving`
- detects the goal, logs success, and keeps spinning

## Why this matches the rubric

The exam energy table is written in terms of **completed actions**, not continuous velocity messages, so the node is built around exact primitive actions.

## Mecanum extra objective

The exam awards extra marks for a mecanum drive.  
Do **not** convert to mecanum until the base solution works.

If you later attempt mecanum:

1. replace the cylindrical wheels with mecanum wheels
2. switch to a 4-wheel controller
3. map chassis twist `(vx, vy, wz)` to wheel angular velocities
4. retune collision/friction and odometry

That is a second-phase upgrade, not the fastest base-mark path.
