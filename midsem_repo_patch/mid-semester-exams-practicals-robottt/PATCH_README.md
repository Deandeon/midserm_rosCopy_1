This patch is tailored to your current repository tree.

What it changes:
- keeps rover_description as the robot model + launch package
- upgrades maze_energy to use discrete motion events
- adds maze_navigation for the maze solver
- adds maze_perception for the optional gem challenge
- adds config, RViz, tests, and package readmes

What you still must calibrate:
- wheel_separation
- wheel_diameter
- goal_x / goal_y or goal_cell_x / goal_cell_y
- cell_size
- lidar thresholds
- verify height <= 0.25 m

Minimal run sequence after merging into your repo:
1. colcon build --symlink-install
2. source install/setup.bash
3. ros2 launch rover_description gazebo.launch.py

Extra challenge run:
ros2 launch rover_description gazebo.launch.py world_file:=maze_gems.world enable_camera:=true use_gems:=true
