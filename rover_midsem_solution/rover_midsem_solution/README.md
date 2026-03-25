# Rover Mid-Sem Exam Solution Scaffold

This workspace is a practical, exam-focused scaffold for the CS353 maze challenge.

It is built around the exam requirements:

- differential-drive base robot
- launch files for RViz and Gazebo
- maze finder that waits for the `S` key
- energy accounting with the exact rubric actions
- optional lidar for wall sensing
- optional camera pipeline for the gem challenge
- testing, documentation, `.gitignore`, and a devcontainer

## Workspace layout

```text
rover_midsem_solution/
├── .devcontainer/
├── .gitignore
├── README.md
└── src/
    ├── rover_bringup/
    ├── rover_description/
    ├── rover_energy/
    ├── rover_navigation/
    └── rover_perception/
```

## What is already implemented

### Base-mark path
- `rover_description`: cleaned Xacro with optional lidar and camera mounts
- `rover_bringup`: Gazebo maze launch file that loads `ashbot_world`
- `rover_navigation`: wall-following maze finder with:
  - `S`-key start gate
  - discrete motion primitives
  - odom + lidar based control
  - goal logging + keep-alive
- `rover_energy`: tracks **discrete movement events**, not raw `cmd_vel`
- `rover_perception`: optional gem detector using a camera and HSV color masks
- simple Python tests

### Extra objectives
- **Gem challenge scaffold** is included
- **Mecanum notes** are included in `rover_navigation/README.md`, but the live simulation here stays differential-drive because that is the fastest route to a reliable base submission

## Important calibration items

You still need to tune these for your lab world:

1. **wheel diameter**
2. **wheel separation**
3. **cell size**
4. **goal position or goal cell**
5. **wall threshold**
6. **camera enable flag** only if you attempt the gem task
7. verify robot **height <= 25 cm**

The body mesh came from your CAD export, so the mast / top sensor block may still need a manual measurement check.

## Assumed dependency

The exam sheet says to add the `ashbot_world` submodule on the `eclipse` branch.  
This scaffold assumes the world package exposes the maze world files under:

```text
ashbot_world/worlds/maze.world
ashbot_world/worlds/maze_gems.world
```

If your submodule installs them under a different path, update `rover_bringup/launch/sim_maze.launch.py`.

## Build

From the workspace root:

```bash
cd rover_midsem_solution
source /opt/ros/$ROS_DISTRO/setup.bash
colcon build --symlink-install
source install/setup.bash
```

## Run RViz-only model check

```bash
ros2 launch rover_description display.launch.py
```

## Run maze simulation

Base maze:

```bash
ros2 launch rover_bringup sim_maze.launch.py world_file:=maze.world
```

Gem world:

```bash
ros2 launch rover_bringup sim_maze.launch.py world_file:=maze_gems.world enable_camera:=true use_gems:=true
```

## Suggested tuning order

1. Spawn robot in Gazebo
2. Confirm `/scan` exists
3. Confirm `/odom` exists
4. Test `cmd_vel`
5. Tune wheel diameter / separation
6. Tune turn speed and forward speed
7. Tune `cell_size` and `wall_threshold`
8. Set the correct goal parameters in `rover_bringup/config/maze_params.yaml`
9. Record demo video

## Exam checklist

- [ ] repository contains only source files, not `build/ install/ log/`
- [ ] root README present
- [ ] each package has a README
- [ ] devcontainer present
- [ ] Gazebo demo video recorded
- [ ] RViz demo recorded
- [ ] energy report visible in terminal
- [ ] maze node waits for `S`
- [ ] robot logs success and stays alive at the end
- [ ] GitHub commit history shows both team members contributed
