import asyncio
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from asyncua import Server
import threading

class BridgeNode(Node):
    def __init__(self, pos_x_var, pos_y_var, loop):
        super().__init__('ros2_opcua_bridge')
        self.pos_x_var = pos_x_var
        self.pos_y_var = pos_y_var
        self.loop = loop
        self.subscription = self.create_subscription(
            Odometry, '/odom', self.listener_callback, 10)

    def listener_callback(self, msg):
        x = float(msg.pose.pose.position.x)
        y = float(msg.pose.pose.position.y)
        asyncio.run_coroutine_threadsafe(
            self.pos_x_var.write_value(x), self.loop
        )
        asyncio.run_coroutine_threadsafe(
            self.pos_y_var.write_value(y), self.loop
        )
        self.get_logger().info(f'Bridged position: x={x:.2f}, y={y:.2f}')


async def main():
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    uri = "http://ros2-scada-bridge"
    idx = await server.register_namespace(uri)

    objects = server.get_objects_node()
    robot = await objects.add_object(idx, "Robot")
    pos_x = await robot.add_variable(idx, "RobotPosX", 0.0)
    pos_y = await robot.add_variable(idx, "RobotPosY", 0.0)
    await pos_x.set_writable()
    await pos_y.set_writable()

    print("OPC UA server running at opc.tcp://0.0.0.0:4840/freeopcua/server/")

    loop = asyncio.get_event_loop()

    rclpy.init()
    node = BridgeNode(pos_x, pos_y, loop)
    ros_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    ros_thread.start()

    async with server:
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
