#include "mbed.h"
#include "wifi_helper.h"
#include "mbed-trace/mbed_trace.h"
#include "EthernetInterface.h" 
#include "stm32l4s5i_iot01_accelero.h"
#include "stm32l4s5i_iot01_gyro.h"
#include "stm32l4s5i_iot01.h"
#include <cstdint>
#include <string>
#if MBED_CONF_APP_USE_TLS_SOCKET
#include "root_ca_cert.h"
#ifndef DEVICE_TRNG
#error "mbed-os-example-tls-socket requires a device which supports TRNG"
#endif
#endif


#define SCALE_MULTIPLIER    0.004

#define SEND_INT    5
#define SAMPLE_RATE 2
#define PLAYER      1
#define SAMPLE_PERIOD 2ms
#define Rotation_threshold 1.0

InterruptIn button(BUTTON1);

double acc = 0;
double score = 0;
uint8_t counter = 0;
uint8_t counter_act = 0;
//uint8_t counter_continue = 0;
volatile uint8_t shot = 0;
volatile uint8_t last_operation = 0;
volatile uint8_t operation = 0;
class Sensor{
#define TimeStep  (float)SAMPLE_RATE / 1000
public:
    uint8_t right = 0, left = 0, up = 0, down = 0;
    Sensor(events::EventQueue &event_queue):_event_queue(event_queue){
        BSP_ACCELERO_Init();    
        BSP_GYRO_Init();
        Calibrate();
        _event_queue.call_every(2ms, this, &Sensor::update);
    }
    void Calibrate(){
        printf("Calibrating Sensors.....\n");
        int n = 0;
        _AccOffset[0] = 0;
        _GyroOffset[0] = 0;
        _AccOffset[1] = 0;
        _GyroOffset[1] = 0;
        _AccOffset[2] = 0;
        _GyroOffset[2] = 0;
        while(n < 2000){
            BSP_ACCELERO_AccGetXYZ(_pAccDataXYZ);
            BSP_GYRO_GetXYZ(_pGyroDataXYZ);
            _AccOffset[0] += _pAccDataXYZ[0];
            _GyroOffset[0] += _pGyroDataXYZ[0];
            _AccOffset[1] += _pAccDataXYZ[1];
            _GyroOffset[1] += _pGyroDataXYZ[1];
            _AccOffset[2] += _pAccDataXYZ[2];
            _GyroOffset[2] += _pGyroDataXYZ[2];
            ThisThread::sleep_for(SAMPLE_PERIOD);
            ++n;
        }
        
        // loop unrolling
        _AccOffset[0] /= n;
        _GyroOffset[0] /= n;
        _AccOffset[1] /= n;
        _GyroOffset[1] /= n;
        _AccOffset[2] /= n;
        _GyroOffset[2] /= n;
        printf("Done calibration\n");
        
    }

    void update(){
        BSP_GYRO_GetXYZ(_pGyroDataXYZ);
        rotation_distance += ((_pGyroDataXYZ[0] - _GyroOffset[0]) * SCALE_MULTIPLIER)*TimeStep; 
        rotation_right_left += ((_pGyroDataXYZ[1] - _GyroOffset[1]) * SCALE_MULTIPLIER)*TimeStep;
        ThisThread::sleep_for(SAMPLE_PERIOD);
    }

    void check_left_right(uint8_t& right, uint8_t& left) {
        BSP_ACCELERO_AccGetXYZ(_pAccDataXYZ);
        if((_pAccDataXYZ[0] - _AccOffset[0])*SCALE_MULTIPLIER > 0.7){
            left = 1;
            score = (_pAccDataXYZ[0] - _AccOffset[0])*SCALE_MULTIPLIER;
            acc = _pAccDataXYZ[0] - _AccOffset[0];
        }
        else
            left = 0;
        if((_pAccDataXYZ[0] - _AccOffset[0])*SCALE_MULTIPLIER < -0.7){
            right = 1;
            score = (_pAccDataXYZ[0] - _AccOffset[0])*SCALE_MULTIPLIER;
            acc = _pAccDataXYZ[0] - _AccOffset[0];
        }
        else
            right = 0;
        rotation_right_left = 0;
    }
    
    void check_up_down(uint8_t& up, uint8_t& down) {
        if(rotation_distance > Rotation_threshold || (_pAccDataXYZ[2] - _AccOffset[2])*SCALE_MULTIPLIER > 0.6){
            up = 1;
            score = rotation_distance;
        }

        else{
            up = 0;
        }
        if(rotation_distance < -Rotation_threshold-0.05 || (_pAccDataXYZ[2] - _AccOffset[2])*SCALE_MULTIPLIER < -0.7){
            down = 1;
            score = rotation_distance;
        }
            
        else
            down = 0;
        rotation_distance = 0;
    }
    
    void Action(uint8_t& right, uint8_t& left, uint8_t& up, uint8_t& down, volatile uint8_t& shot){
        check_left_right(right, left);
        check_up_down(up, down);
    }
    void getAction(){
        Action(right, left, up, down, shot);
    }
private:
    events::EventQueue &_event_queue;
    int16_t _pAccDataXYZ[3] = {0};
    float _pGyroDataXYZ[3] = {0};
    float rotation_right_left = 0;
    float rotation_distance = 0;
    int   _AccOffset[3] = {};
    float _GyroOffset[3] = {};
    
    uint8_t last_action;
};

class SocketDemo {
    static constexpr size_t MAX_NUMBER_OF_ACCESS_POINTS = 10;
    static constexpr size_t MAX_MESSAGE_RECEIVED_LENGTH = 1000;

#if MBED_CONF_APP_USE_TLS_SOCKET
    static constexpr size_t REMOTE_PORT = 443; // tls port
#else
    static constexpr size_t REMOTE_PORT = 8080;
#endif // MBED_CONF_APP_USE_TLS_SOCKET

public:
    SocketDemo(Sensor * sensor, events::EventQueue &event_queue) : _net(NetworkInterface::get_default_instance()), _sensor(sensor), 
        _event_queue(event_queue)
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
        const char *hostname = "192.168.43.233";
        _net->gethostbyname(hostname, &address);

        const uint16_t port = REMOTE_PORT;
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
        _event_queue.call_every(10ms, this, &SocketDemo::send_data);
    }

    ~SocketDemo()
    {
        if (_net)
            _net->disconnect();
    }

    void send_data(){
        char data[64];
        nsapi_error_t response;
        _sensor->getAction();
        if(shot==1){
            operation = 5;
        }
        else if (_sensor->left==1){
            operation = 1;
        }
        else if(_sensor->right==1){
            operation = 2;
        }
        else if(_sensor->up==1){
            operation = 3;
        }
        else if(_sensor->down==1){
            operation = 4;
        }
        //uint8_t table[6] = {0, 2, 1, 4, 3, 0};
        /*
        if(operation==last_operation){
            counter_continue++;
        }
        */
        if(operation!=last_operation){
            /*
            if(operation==table[last_operation] && counter_continue>=10){
                int len = sprintf(data,"%d\n", operation);
                response = _socket.send(data,len);
                if(response <= 0)
                    printf("Error sending:%d\n",response);
            
                last_operation = operation; 
                return;
            }
            */
            
            int len = sprintf(data,"%d\n", operation);
            response = _socket.send(data,len);
            if(response <= 0)
                printf("Error sending:%d\n",response);
            
            last_operation = operation;
            
        }

    }


private:
    NetworkInterface *_net;

#if MBED_CONF_APP_USE_TLS_SOCKET
    TLSSocket _socket;
#else
    TCPSocket _socket;
#endif // MBED_CONF_APP_USE_TLS_SOCKET

    Sensor* _sensor;
    events::EventQueue &_event_queue;

};

void button_pressed(){
    shot = 1;
}
void button_released(){
    shot = 0;
}
int main()
{
   printf("===============================================\n");
   printf("==Tank Battle (Author: B08202033 & B08202054)== \n");
   printf("===============================================\n");
   printf("\n================Starting Soon==================\n");
   ThisThread::sleep_for(1s);
   static EventQueue event_queue(16 * EVENTS_EVENT_SIZE);
   Sensor _sensor(event_queue);
   SocketDemo socket(&_sensor, event_queue);
   button.fall(&button_pressed);
   button.rise(&button_released);
   event_queue.dispatch_forever();
   printf("\nDone\n");
}
