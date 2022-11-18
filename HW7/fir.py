from scipy import signal
import numpy as np
from Data import Input, Output, firCoeffs32
import matplotlib.pyplot as plt

t = np.arange(len(Input))/10

tmp = signal.lfilter(b = firCoeffs32, a = 1, x = Input)

plt.figure(figsize=(12,8))

plt.subplot(211)
plt.plot(t,Input,label="Input")
plt.plot(t,Output,label="STM32 Output")
plt.plot(t,tmp,label="Python Output")
plt.ylabel('Gyro-x (dps)', fontsize=16)
plt.grid()
plt.legend(fontsize=10)

plt.subplot(212)
plt.plot(t,(tmp-Output)/Output)
plt.xlabel('Time (sec)', fontsize=16)
plt.ylabel('Relative error', fontsize=16)
plt.grid()
plt.savefig('tmp.png', dpi=300)



