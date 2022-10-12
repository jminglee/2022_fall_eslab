/* Sockets Example
 * Copyright (c) 2016-2020 ARM Limited
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "mbed.h"
#include "wifi_helper.h"
#include "mbed-trace/mbed_trace.h"
#include "EthernetInterface.h" 
#include "stm32l4s5i_iot01.h"
#include "stm32l4s5i_iot01_gyro.h"
#include "stm32l4s5i_iot01_accelero.h"
#include <cstdint>

#if MBED_CONF_APP_USE_TLS_SOCKET
#include "root_ca_cert.h"

#ifndef DEVICE_TRNG
#error "mbed-os-example-tls-socket requires a device which supports TRNG"
#endif
#endif // MBED_CONF_APP_USE_TLS_SOCKET

class SocketDemo {
    static constexpr size_t MAX_NUMBER_OF_ACCESS_POINTS = 10;
    static constexpr size_t MAX_MESSAGE_RECEIVED_LENGTH = 1000;

#if MBED_CONF_APP_USE_TLS_SOCKET
    static constexpr size_t REMOTE_PORT = 443; // tls port
#else
    static constexpr size_t REMOTE_PORT = 6543;
#endif // MBED_CONF_APP_USE_TLS_SOCKET

public:
    SocketDemo() : _net(NetworkInterface::get_default_instance())
    {
    }

    ~SocketDemo()
    {
        if (_net)
            _net->disconnect();
    }

    void run()
    {
        if (!_net) 
        {
            printf("Error! No network interface found.\r\n");
            return;
        }

        WiFiInterface *wifi = _net->wifiInterface();
        printf("Connecting to the network...\r\n");

        nsapi_size_or_error_t result = _net->connect();
        if (result != 0) 
        {
            printf("Error! _net->connect() returned: %d\r\n", result);
            return;
        }

        /* opening the socket only allocates resources */
        result = _socket.open(_net);
        if (result != 0) 
        {
            printf("Error! _socket.open() returned: %d\r\n", result);
            return;
        }

        SocketAddress address;
        const char *hostname = "192.168.108.35";
        _net->gethostbyname(hostname, &address);

        const uint16_t port = 8080;
        address.set_port(port);

        result = _socket.connect(address);
        if (result != 0) 
        {
            printf("Error! _socket.connect() returned: %d\r\n", result);
            return;
        }
        else 
        {
            printf("Socket connect to %s : %d\r\n", address.get_ip_address(), REMOTE_PORT);
        }

        int sample_num = 0, len, response;
        int16_t pDataXYZ[3] = {0};
        float pGyroDataXYZ[3] = {0};
        char acc_json[MAX_MESSAGE_RECEIVED_LENGTH];

        BSP_ACCELERO_Init();
        BSP_GYRO_Init();

        while(sample_num < 30)
        {
            ++sample_num;
            BSP_GYRO_GetXYZ(pGyroDataXYZ);
            BSP_ACCELERO_AccGetXYZ(pDataXYZ);
            
            len = sprintf(acc_json, "%f %f %f %f %f %f %d",
                        (float)((int)(pGyroDataXYZ[0]*10000))/10000,
                        (float)((int)(pGyroDataXYZ[1]*10000))/10000, 
                        (float)((int)(pGyroDataXYZ[2]*10000))/10000, 
                        (float)((int)(pDataXYZ[0]*10000))/10000,
                        (float)((int)(pDataXYZ[1]*10000))/10000, 
                        (float)((int)(pDataXYZ[2]*10000))/10000,
                        sample_num);

            printf("%s\n",acc_json);

            response = _socket.send(acc_json,len);
            if(response <= 0)
                printf("Error sending:%d\n",response);
            
            ThisThread::sleep_for(1s);
        }

        _socket.close();
        printf("Complete from sensor\r\n");
        _net->disconnect();
    }

private:
    NetworkInterface *_net;

#if MBED_CONF_APP_USE_TLS_SOCKET
    TLSSocket _socket;
#else
    TCPSocket _socket;
#endif // MBED_CONF_APP_USE_TLS_SOCKET
};

int main() 
{
    printf("\r\nStarting socket demo\r\n\r\n");

#ifdef MBED_CONF_MBED_TRACE_ENABLE
    mbed_trace_init();
#endif

    SocketDemo *example = new SocketDemo();
    MBED_ASSERT(example);
    example->run();

    return 0;
}
