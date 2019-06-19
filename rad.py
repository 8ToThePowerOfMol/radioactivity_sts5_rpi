#!/usr/bin/python
# -*- encoding: utf-8 -*-

import RPi.GPIO as GPIO
import time

# Constants

PIN_LED = 4
PIN_BUTTON = 17
CALIBRATION = 0.0066
MEASURE_ERR = 1.1

# GPIO Settings

# pin 7 --> GPIO 4
# pin 17 --> GPIO 11

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIN_LED, GPIO.OUT)
GPIO.setup(PIN_BUTTON, GPIO.IN)

# Program

x = float(input('Input measurement time (in minutes): '))
process_filename = input('Input file name for measurement results (without suffix): ')
process = open("%s.csv" % process_filename, 'a')
process.write("Impuls; Pulse/Sec; uSv/h; Pulse/Min; Measurement second; % up to the end\n")

timeout = time.time() + x * 60
t_start = time.time()
p_count = int(0)
is_recorded = False

while (time.time() < timeout):
    if(GPIO.input(PIN_BUTTON) == False):
        GPIO.output(PIN_LED, GPIO.HIGH)
        if(not is_recorded):
            p_count = p_count + 1
            curr_ps = round(p_count / (time.time() - t_start), 2)
            curr_ps_min = round((p_count / (time.time() - t_start) * 60), 2)
            curr_dose = round((p_count/(time.time() - t_start) * 60) * CALIBRATION * MEASURE_ERR , 4)
            est_time = round(time.time() - t_start, 1)
            print("Pulse: %s; %s pulses/sec; %s uSv/h; %s pulses/min; t: %s/%ss"\
                % (p_count, curr_ps, curr_dose, curr_ps_min, est_time, round(x*60, 0)))
            diff_time = round((time.time() - t_start) / (x * 60), 3)
            process.write("%s; %s; %s; %s; %s; %s\r\n"\
                % (p_count, curr_ps, curr_dose, curr_ps_min, est_time, diff_time))
            is_recorded = True
    else:
        GPIO.output(PIN_LED, GPIO.LOW)
        is_recorded = False
                  
ps_per_sec = p_count / (x * 60)
ps_per_min = p_count / x                  
dose = (p_count/x) * CALIBRATION * MEASURE_ERR
print("Sum:", p_count, "pulses in", x, "min.")
print("Pulses:", round(ps_per_sec, 5), "pulse/sec,", round(ps_per_min, 5), "pulse/min")
print("Dose:", round(dose, 7), "uSv/h")
print("Measurement process written into %s.csv file" % process_filename)
                  
results = open("results.txt", 'a')
results.write(" %s: %s pulse/min %s pulse/sec (%s uSv/h) with total %s pulses in %s mins.\r\n"\
    % (process_filename, round(ps_per_min, 5), round(ps_per_sec, 5), round(dose, 7), p_count, x))
print("Result written into results.txt")
print("Values: Name; Pulses/sec; Pulses/min; Dose; Total pulses; Measurement time in minutes")

process.close()
results.close()
GPIO.cleanup()
