# rover_perception

Optional helper for the **Gem Collector’s Dilemma**.

## What it does

- subscribes to `/front_camera/image_raw`
- classifies the dominant colored blob in the image
- estimates the current cell from odometry
- publishes one ordered detection per new cell on `/gem_detection`

## Practical note

This is a scaffold, not a finished competition vision system.  
You still need to tune HSV thresholds and camera placement in the gem world.
