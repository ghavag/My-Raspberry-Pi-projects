#!/usr/bin/python -u

import smbus
import time
import RPi.GPIO as IO
import signal


# Konfigurationsparameter.
VREF = 3.3
R = 2

# Globale Variablen.
Running = True

# Routine, um SIGTERM abzufangen.
def signal_handler(signum, frame):
 global Running
 Running = False
 IO.cleanup()
 print "Programm wurde abgebrochen."

# SIGINT (CTRL+C) abfangen.
signal.signal(signal.SIGINT, signal_handler)

# Erzeugen einer I2C-Instanz und oeffnen des Busses.
am8 = smbus.SMBus(1)

IO.setmode(IO.BCM) # Benutze GPIO-Nummerierung.
IO.setup(21, IO.OUT) #  GPIO21 zur Steuerung des Entladevorganges.

IO.output(21, IO.HIGH) # Entladevorgang starten.
time.sleep(0.05) # Der Relai braucht ein Weilchen um zu schalten.

start_time = time.time()
elapsed_time = 0
Umin_cnt = 0
ah = 0
first_run = False

print "Time(s) UR(V) IR(A)"

while Running:
 # Byte senden damit wir beim naechsten Lesen das erste Byte empfangen.
 am8.write_byte(1, 0)

 # Low- und High-Byte des Messwertes empfangen.
 val1 = am8.read_byte(1)
 val2 = am8.read_byte(1)

 # Berechnungen.
 UR = VREF / 1023 * (val1 + 256*val2)
 IR = UR / R

 cur_time = time.time()
 elapsed_time_last = elapsed_time
 elapsed_time = cur_time - start_time

 if first_run:
  ah = ah + (IR / 3600 * (elapsed_time - elapsed_time_last))
 else:
  first_run = True

 print round(elapsed_time, 2), UR, IR

 time.sleep(1)

print
print "Laufzeit: ", round(elapsed_time / 3600, 2), "h"
print "Kapazitaet: ", ah * 1000, "mAh"

IO.cleanup()

