# ROS2 SCADA Bridge

Bridges live robot data from a ROS 2 simulation into standard industrial automation protocols (OPC UA and Modbus TCP), so that SCADA/HMI tools and OPC UA clients can read simulated robot telemetry the same way they'd read data from real plant-floor equipment.

## What this demonstrates

Robotics and industrial automation usually speak different languages: ROS 2 for robot software, OPC UA / Modbus for SCADA, PLCs, and HMIs. This project is a working proof of concept for connecting the two — pulling live odometry out of a ROS 2 simulation and exposing it as OPC UA variables that any industrial client can subscribe to.

## Architecture

```
Isaac Sim  --/odom (ROS 2)-->  ros2_opcua_bridge.py  --OPC UA-->  UAExpert / Ignition / any OPC UA client
```

- **Isaac Sim** simulates a robot and publishes its odometry (`nav_msgs/Odometry`) on the ROS 2 topic `/odom`.
- **`ros2_opcua_bridge.py`** subscribes to `/odom` via `rclpy`, and republishes `position.x` / `position.y` as writable OPC UA variables (`RobotPosX`, `RobotPosY`) under an `asyncua`-based OPC UA server. Since ROS 2's callback-based spin loop and `asyncua`'s asyncio event loop are different concurrency models, the bridge hands writes from the ROS callback thread to the asyncio loop with `asyncio.run_coroutine_threadsafe`.
- **Any OPC UA client** (UAExpert, Ignition, etc.) can then connect to `opc.tcp://<host>:4840/freeopcua/server/` and read the live position data as it updates.

Supporting scripts:
- `fake_battery_publisher.py` — simulates a `/battery_state` ROS 2 topic for testing, independent of Isaac Sim.
- `opcua_server_test.py` — a standalone OPC UA server that self-drives a battery variable, for testing OPC UA clients without needing ROS 2 running at all.
- `modbus_test.py` — a standalone Modbus TCP client used to validate read/write against a Modbus endpoint. Not yet wired into the live bridge (see Status below).

## Running it

Requires ROS 2 Humble, `asyncua`, and (for the Modbus test) `pymodbus`.

```bash
source /opt/ros/humble/setup.bash
python3 ros2_opcua_bridge.py
```

This starts the OPC UA server at `opc.tcp://0.0.0.0:4840/freeopcua/server/` and subscribes to `/odom`. Point Isaac Sim (or any `/odom` publisher) and an OPC UA client like UAExpert at it to see live position data flow through.

## Status

- **OPC UA pipeline: working end-to-end.** Isaac Sim → ROS 2 `/odom` → this bridge → OPC UA server → UAExpert, confirmed with live odometry data.
- **Modbus TCP: standalone test only.** `modbus_test.py` validates read/write against a Modbus endpoint directly, but is not yet integrated into the live bridge.
- **CODESYS (soft PLC): descoped.** The original plan was to have a CODESYS soft PLC consume robot data over Modbus TCP, acting as the PLC layer between the robot and SCADA (SCADA reading through a PLC rather than OPC UA directly). This was descoped after hitting documented platform bugs in CODESYS Control Win V3 that made reliable integration impractical within scope. Rather than ship a fragile workaround, this is documented here as a known limitation.
- **Next step, if picked back up:** wire Modbus into the live bridge alongside OPC UA, and revisit a soft-PLC layer on a more stable platform.
