from bluepy.btle import Peripheral, UUID
from bluepy.btle import Scanner
import bluepy.btle as btle

scanner = Scanner()
print("Scanning for 3 seconds: ")
devices = list(scanner.scan(3.0))

class MyDelegate(btle.DefaultDelegate):
    def __init__(self):
        btle.DefaultDelegate.__init__(self)

    def handleNotification(self, cHandle, data):
        print("A notification was received")

for i, device in enumerate(devices):
    print(f"{i}: {device.addr} {device.addrType} {device.rssi}")
    for (adtype, desc, value) in device.getScanData():
        if desc=="Complete Local Name":
            print(f"{desc} = {value}")

num = int(input('Enter your device number: '))
print(f"Connecting to device {num}: {devices[num].addr}")
dev = Peripheral(devices[num].addr, devices[num].addrType)
dev.withDelegate(MyDelegate())

try:
    ch = dev.getCharacteristics(uuid=UUID(0xfff4))[0]
    write_data = input("Test of writing data: ")
    ch.write(write_data.encode('utf-8'), withResponse=True)
    cccd = ch.getHandle() + 1
    dev.writeCharacteristic(cccd, b"\x01\x00")
    print("Test of receiving notify....")
    while True:
        if dev.waitForNotifications(5.0):
            print("Get notified!")
            break
finally:
    dev.disconnect()
