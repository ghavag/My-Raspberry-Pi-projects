CC=avr-gcc
CFLAGS=-mmcu=atmega8 -Os
PROJNAME=i2cadc
IFILE=$(PROJNAME).c
OFILE=$(PROJNAME).bin

all:
	$(CC) $(CFLAGS) -o $(OFILE) $(IFILE)

clean:
	rm $(OFILE)

flash:
	avrdude -p m8 -P /dev/ttyUSB0 -c stk500 -U flash:w:$(OFILE)

readfuses:
	avrdude -p m8 -P /dev/ttyUSB0 -c stk500 -n -v


