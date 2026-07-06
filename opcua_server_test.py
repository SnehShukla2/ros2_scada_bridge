import asyncio
from asyncua import Server, ua

async def main():
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")

    uri = "http://ros2-scada-bridge"
    idx = await server.register_namespace(uri)

    # Create a folder + one variable node
    objects = server.get_objects_node()
    robot = await objects.add_object(idx, "Robot")
    battery = await robot.add_variable(idx, "BatteryLevel", 100.0)
    await battery.set_writable()

    print("OPC UA server running at opc.tcp://0.0.0.0:4840/freeopcua/server/")

    async with server:
        val = 100.0
        while True:
            val -= 1
            if val < 0:
                val = 100.0
            await battery.write_value(val)
            await asyncio.sleep(2)

if __name__ == "__main__":
    asyncio.run(main())