from bluepy.btle import Peripheral, UUID
from bluepy.btle import Scanner

scanner = Scanner()
print("Scanning for 3 seconds: ")
devices = list(scanner.scan(3.0))

for i, device in enumerate(devices):
    print(f"{i}: {device.addr} {device.addrType} {device.rssi}")
    for (adtype, desc, value) in device.getScanData():
        if desc=="Complete Local Name":
            print(f"{desc} = {value}")

num = int(input('Enter your device number: '))
print(f'Connecting to device {num}: {devices[num].addr}')
dev = Peripheral(devices[num].addr, devices[num].addrType)

for service in dev.services:
    print(str(service))
    
try:
    testService= dev.getServiceByUUID(UUID(0xfff0))
    for ch in testService.getCharacteristics():
        print("ch: " + str(ch))

    ch= dev.getCharacteristics(uuid=UUID(0xfff4))[0]
    if (ch.supportsRead()):
        print("Data in channel:", ch.read())
    if input("Write? [Y/N]: " == "Y"):
        write_data = input("To Write: ")
        ch.write(write_data.encode('utf-8'))

finally:
    dev.disconnect()
