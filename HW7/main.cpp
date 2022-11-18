/* ----------------------------------------------------------------------
** Include Files
** ------------------------------------------------------------------- */
#include "mbed.h"
#include "arm_math.h"
#include "math_helper.h"
#include "stm32l4s5i_iot01_gyro.h"

#define SEMIHOSTING
#if defined(SEMIHOSTING)
#include <stdio.h>
#endif
/* ----------------------------------------------------------------------
** Macro Defines
** ------------------------------------------------------------------- */
#define GYRO_SAMPLES 128
#define SNR_THRESHOLD_F32 100.0f
#define BLOCK_SIZE 32
#if defined(ARM_MATH_MVEF) && !defined(ARM_MATH_AUTOVECTORIZE)
#define NUM_TAPS_ARRAY_SIZE 32
#else
#define NUM_TAPS_ARRAY_SIZE 29
#endif
#define NUM_TAPS 29
/* -------------------------------------------------------------------
 * Declare Ref and Test output buffer
 * ------------------------------------------------------------------- */
static float32_t refOutput[GYRO_SAMPLES];
/* -------------------------------------------------------------------
 * Declare State buffer of size (numTaps + blockSize - 1)
 * ------------------------------------------------------------------- */
#if defined(ARM_MATH_MVEF) && !defined(ARM_MATH_AUTOVECTORIZE)
static float32_t firStateF32[2 * BLOCK_SIZE + NUM_TAPS - 1];
#else
static float32_t firStateF32[BLOCK_SIZE + NUM_TAPS - 1];
#endif 
/* ----------------------------------------------------------------------
** FIR Coefficients buffer generated using fir1() MATLAB function.
** fir1(28, 6/24)
** ------------------------------------------------------------------- */
#if defined(ARM_MATH_MVEF) && !defined(ARM_MATH_AUTOVECTORIZE)
const float32_t firCoeffs32[NUM_TAPS_ARRAY_SIZE] = 
{
    -0.0018225230f, -0.0015879294f, +0.0000000000f, +0.0036977508f, +0.0080754303f, +0.0085302217f, -0.0000000000f, -0.0173976984f,
    -0.0341458607f, -0.0333591565f, +0.0000000000f, +0.0676308395f, +0.1522061835f, +0.2229246956f, +0.2504960933f, +0.2229246956f,
    +0.1522061835f, +0.0676308395f, +0.0000000000f, -0.0333591565f, -0.0341458607f, -0.0173976984f, -0.0000000000f, +0.0085302217f,
    +0.0080754303f, +0.0036977508f, +0.0000000000f, -0.0015879294f, -0.0018225230f, 0.0f,0.0f,0.0f
};
#else
const float32_t firCoeffs32[NUM_TAPS_ARRAY_SIZE] = 
{
    -0.0018225230f, -0.0015879294f, +0.0000000000f, +0.0036977508f, +0.0080754303f, +0.0085302217f, -0.0000000000f, -0.0173976984f,
    -0.0341458607f, -0.0333591565f, +0.0000000000f, +0.0676308395f, +0.1522061835f, +0.2229246956f, +0.2504960933f, +0.2229246956f,
    +0.1522061835f, +0.0676308395f, +0.0000000000f, -0.0333591565f, -0.0341458607f, -0.0173976984f, -0.0000000000f, +0.0085302217f,
    +0.0080754303f, +0.0036977508f, +0.0000000000f, -0.0015879294f, -0.0018225230f
};
#endif
/* ------------------------------------------------------------------
 * Global variables for FIR LPF Example
 * ------------------------------------------------------------------- */
uint32_t blockSize = BLOCK_SIZE;
uint32_t numBlocks = GYRO_SAMPLES/BLOCK_SIZE;
float32_t snr;

int32_t main(void)
{
    int i;
    arm_fir_instance_f32 S;

    float GyroDataX[GYRO_SAMPLES];
    float GyroOutputX[GYRO_SAMPLES];
    float pGyroDataXYZ[3];
    float sum = 0;

    printf("\nStart process\n");

    BSP_GYRO_Init();
    printf("Input = [");
    for(i = 0; i < GYRO_SAMPLES; i++) 
    {
        BSP_GYRO_GetXYZ(pGyroDataXYZ);
        GyroDataX[i] = (float)((int)(pGyroDataXYZ[0]*10000)/10000);
        printf("%f, ", GyroDataX[i]);
        ThisThread::sleep_for(100ms);
    }
   
    arm_fir_init_f32(&S, NUM_TAPS, (float32_t *)&firCoeffs32[0], &firStateF32[0], blockSize);
    for(i = 0; i < numBlocks; i++)
    {
        arm_fir_f32(&S, &GyroDataX[0] + (i * blockSize), &GyroOutputX[0] + (i * blockSize), blockSize);
    }
    
    printf("]\nOutput = [");
    for(i = 0; i < GYRO_SAMPLES; i++) printf("%f, ", GyroOutputX[i]);
    
    for(i = 0; i < GYRO_SAMPLES; i++) sum += GyroDataX[i];
    for(i = 0; i < GYRO_SAMPLES; i++) refOutput[i] = sum/GYRO_SAMPLES;
    snr = arm_snr_f32(&refOutput[0], &GyroOutputX[0], GYRO_SAMPLES);
    printf("\nSNR = %f\n", snr);

    printf("]\n\nEnd process\n");
}