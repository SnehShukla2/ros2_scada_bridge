from pymodbus.client import ModbusTcpClient

client = ModbusTcpClient('172.27.112.1', port=502)
client.connect()

result = client.write_register(address=0, value=1234)
print("Write result:", result)

read = client.read_holding_registers(address=0, count=2)
print("Read back:", read.registers)

client.close()
