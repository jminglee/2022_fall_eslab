STM32 IoT part:
- Import ```BLE_GattServer_AddService``` project
- Put ```ButtonServer.h```, ```main.cpp```, ```pretty_printer.h``` into ```source``` directory
- Modify ```mbed_app.json``` if neccesary. Specifically, you may need to add neccessary information about the STM32 IoT node
- Compile & Run

Rpi part:
- After the STM32 IoT node start service, run ```HW4.py``` by ```sudo python HW4.py```
- Select the device to connect through the device number that matchs the device MAC address
- Connect the HeartRate service (enter uuid 180d), and the characteristics (enter uuid 2a37)
- You should see the simulated heart rate on the terminal, after the heart rate printed 30 times, the service will be disconnected
- Repeat the above operations for button service (service uuid a000, characteristic uuid a001)
- Press the user button, and you should see the notifications on the screen
- After 20s not receiving any notifications, the service will be disconnected.
