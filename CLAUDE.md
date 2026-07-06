# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a small collection of standalone Python scripts prototyping a bridge between ROS 2 and industrial SCADA protocols (OPC UA and Modbus). There is no ROS 2 package structure here (no `package.xml`, `setup.py`, or `CMakeLists.txt`) — scripts are run directly with `python3`, not via `ros2 run` or `colcon`.

The environment is ROS 2 Humble, sourced via `/opt/ros/humble`. Dependencies (`rclpy`, `asyncua`, `pymodbus`) are already available in the system Python — there is no virtualenv or requirements file in this repo.

## Running the scripts

Each script is independent and run directly, e.g.:

```bash
source /opt/ros/humble/setup.bash
python3 ros2_opcua_bridge.py
```

- `ros2_opcua_bridge.py` — the main bridge. Subscribes to `/odom` (`nav_msgs/Odometry`) via `rclpy` and forwards `position.x`/`position.y` into OPC UA variables (`RobotPosX`, `RobotPosY`) under an `asyncua` server exposed at `opc.tcp://0.0.0.0:4840/freeopcua/server/`. ROS spins on a background thread; OPC UA writes from the ROS callback are marshalled onto the asyncio event loop with `asyncio.run_coroutine_threadsafe`.
- `fake_battery_publisher.py` — a ROS 2 node with no bridge involvement. Publishes a decaying/resetting `Float64` on `/battery_state` once per second. Used to simulate a topic for bridging work without needing real robot hardware.
- `opcua_server_test.py` — a standalone `asyncua` server (no ROS) that self-drives a `BatteryLevel` variable down from 100 on a timer. Useful for testing an OPC UA client (e.g. a SCADA HMI) independent of ROS.
- `modbus_test.py` — a standalone Modbus TCP client (`pymodbus`) that writes then reads back a holding register against a hardcoded IP (`172.27.112.1:502`). Update the IP/port inline to point at whatever Modbus server/gateway you're testing against.

## Architecture notes

- The bridge pattern used in `ros2_opcua_bridge.py` — ROS callback thread pushes into the asyncio loop via `run_coroutine_threadsafe` — is the template to follow when adding more topics or a Modbus-side bridge: ROS 2 and the SCADA server library (`asyncua`/`pymodbus`) run on different concurrency models (callback-based `rclpy.spin` vs. `asyncio`), and they must be bridged explicitly rather than mixed.
- `fake_battery_publisher.py` and `opcua_server_test.py` are test/simulation fixtures, not part of the bridge itself — when adding a real battery bridge, model it on `ros2_opcua_bridge.py`'s pattern (subscribe in `rclpy`, write into an `asyncua` variable) rather than on `opcua_server_test.py`'s self-driving loop.
- `modbus_test.py` is a scratch script for exercising a Modbus endpoint directly; it is not wired into the OPC UA bridge. If Modbus becomes an actual bridge target, the ROS→Modbus write path still needs the same cross-loop handoff as the OPC UA path (pymodbus's sync client is blocking, so calls from an async context or a ROS callback need care to avoid blocking the event loop / spin thread).
