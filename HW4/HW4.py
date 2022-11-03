from bluepy.btle import Peripheral, UUID
from bluepy.btle import Scanner, DefaultDelegate
import time

class NotificationDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)
    def handleNotification(self, cHandle, data):
        print(f"Received {int.from_bytes(data, 'big')}")

def f():
    scanner = Scanner()
    print("Scanning for 5 seconds...")
    devices = list(scanner.scan(5.0))
    
    for i,dev in enumerate(devices):
        print("#%d: %s (%s), RSSI=%d dB" % (i, dev.addr, dev.addrType, dev.rssi))
        for (adtype, desc, value) in dev.getScanData():
            if desc=="Complete Local Name":
                print( "  %s = %s" % (desc, value))
    
    number = int(input('Enter your device number: '))
    print(f'Connecting to #{number}: {devices[number].addr}')
    
    dev = Peripheral(devices[number].addr, devices[number].addrType)
    dev.setDelegate(NotificationDelegate())
    
    print("Available Services:")
    for svc in dev.services:
        print("Service", str(svc))
        print("Service UUID: ", str(svc.uuid))
        
    try:
        target_svc = int("0x"+str(input("Which service to connect? ")), 16)
        testService= dev.getServiceByUUID(UUID(target_svc))
        
        print("Available Characteristics:")
        for ch in testService.getCharacteristics():
            print(str(ch))
            print("UUID: ", str(ch.uuid))
        target_char = int("0x"+str(input("Which characteristic to connect? ")), 16)
        ch = dev.getCharacteristics(uuid=UUID(target_char))[0]
        
        print("Handle of selected char is:", ch.valHandle)
        dev.writeCharacteristic(ch.valHandle+1, b"\x01\x00") # this line enables notifications
        
        if target_svc == 0xa000:
            print("Start wait for notifications...")
            
            while True:
                if (ch.supportsRead()):
                    if dev.waitForNotifications(20.0):
                        continue
                    else:
                        print("No notifications received in the last 100s...")
                        return 
        elif target_svc == 0x180d:
            count = 0
            while True:
                if dev.waitForNotifications(20.0):
                    count += 1
                    if count>=30:
                        print("Finishing the test of HeartRate Service, break")
                        return 
                    continue
                else:
                    print("No notifications received in the last 100s...")
                    return 
                
    finally:
        dev.disconnect()

f()
f()
