#!/usr/bin/env bash
# Helper to run turbopy_base_node as root with the right ROS 2 env.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source system ROS 2 Humble
source /opt/ros/humble/setup.bash

# Source this workspace
source "$SCRIPT_DIR/install/setup.bash"

# Run the node
exec ros2 run turbopy_base_driver turbopy_base_node "$@"
