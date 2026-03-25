# rover_bringup

Contains the Gazebo launch file and tunable runtime parameters.

## Main launch

```bash
ros2 launch rover_bringup sim_maze.launch.py
```

## Key arguments

- `world_file`: `maze.world` or `maze_gems.world`
- `enable_camera`: set `true` for the gem challenge
- `use_gems`: start the gem detector node
- `use_rviz`: optionally start RViz alongside Gazebo
