
#include "mbed.h"

#define M_PI           3.14159265358979323846
#define SINE_STEPS     32
#define SINE_OUT_FREQ  1000
#define SINE_STEPS_RAD (2.0f * M_PI / (float)SINE_STEPS)
#define PWM_FREQ       200000 

float sine_duty[SINE_STEPS];

PwmOut led(PA_15);

void pwm_duty_update() 
{
    static int idx = 0;
    led.write(sine_duty[idx++]);   
    if(idx == SINE_STEPS) idx = 0;                   
}

int main()
{
    for(int i = 0; i < SINE_STEPS; i++) sine_duty[i] = ( sin(i * SINE_STEPS_RAD) + 1.0f ) / 2.0f; 

    led.period( 1.0f / (float) PWM_FREQ);   
    
    Ticker pwm_ticker;
    pwm_ticker.attach(&pwm_duty_update, 1.0f / (float)(SINE_STEPS * SINE_OUT_FREQ));
    
    while(1);
}
