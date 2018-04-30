#!/usr/bin/python -u

import smbus
import time
import RPi.GPIO as IO
import signal


# Konfigurationsparameter.
VREF = 3.3
Rmea = 4
R2 = 2

Umin = 3 # Entlade-Schlussspannung.

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

# Vorher einmal schreiben sorgt dafuer, dass das
# erste Byte beim ersten Auslesen zurueckgegeben wird.
#am8.write_byte(1, 0)

#val1 = am8.read_byte(1)
#val2 = am8.read_byte(1)

#Vmea = VREF / 1023 * (val1 + 256*val2)
#Vsrc =  (Vmea * (Rmea + R2)) / Rmea

#print "Voltage drop on Rmea is:", Vmea
#print "VSource is:", Vsrc

IO.setmode(IO.BCM) # Benutze GPIO-Nummerierung.
IO.setup(21, IO.OUT) #  GPIO21 zur Steuerung des Entladevorganges.

IO.output(21, IO.HIGH) # Entladevorgang starten.
time.sleep(0.05) # Das Relais braucht ein Weilchen um zu schalten.

start_time = time.time()
elapsed_time = 0
Umin_cnt = 0
capacity = 0
first_run = False
#start_voltage = 0

print "Time(s) URmea(V) IRmea(A) VSource(V)"

while Running:
 # Byte senden damit wir beim naechsten Lesen das erste Byte empfangen.
 am8.write_byte(1, 0)

 # Low- und High-Byte des Messwertes empfangen.
 val1 = am8.read_byte(1)
 val2 = am8.read_byte(1)

 # Berechnungen.
 URmea = VREF / 1023 * (val1 + 256*val2)
 IRmea = URmea / Rmea
 Usrc =  (URmea * (Rmea + R2)) / Rmea

 cur_time = time.time()
 elapsed_time_last = elapsed_time
 elapsed_time = cur_time - start_time

 if first_run:
  capacity = capacity + (IRmea / 3600 * (elapsed_time - elapsed_time_last))
 else:
  first_run = True
  start_voltage = Usrc

 print round(elapsed_time, 2), URmea, IRmea, Usrc

 if Usrc <= Umin:
  Umin_cnt = Umin_cnt + 1
 else:
  Umin_cnt = 0

 if Umin_cnt >= 3:
  print "Umin wurde erreicht. Programm abgebrochen."
  break

 time.sleep(5)

print
print "Laufzeit: ", round(elapsed_time / 3600, 2), "h"
print "Kapazitaet: ", capacity * 1000, "mAh"
print "Start-Spannung: ", start_voltage, "V"
print "End-Spannung: ", Usrc, "V"

IO.cleanup()

