/*
 * Misst eine Spannung und überträgt sie bei anfrage zu einem TWI-Master.
*/

#define F_CPU 2000000UL

#define MY_TWI_ADDRESS (0x01)

#include <avr/io.h>
#include <avr/interrupt.h>
//#include <util/delay.h>

// Header-Dateien für I²C/TWI-spezifische Sachen.
#include <util/twi.h>

uint16_t result;

#define DATA_ARRAY_LENGTH 5
uint16_t data[DATA_ARRAY_LENGTH];

/*
 * Interrupt-Routine, welche die Nachrichten
 * von der TWI-Hardware-Schnittstelle handhaben.
 */
ISR(TWI_vect) {
	static int data_index = 0;

	// react on TWI status and handle different cases
	uint8_t status = TWSR & 0xFC; // mask-out the prescaler bits

	switch(status) {
		case TW_SR_DATA_ACK: // Daten empfangen, ACK gesendet. Setzt den Index zurück.
			PORTB ^= _BV(PB0); // LED toggeln.
			data_index = 0;
			TWCR = (1<<TWEN)|(1<<TWIE)|(1<<TWINT)|(1<<TWEA)|(0<<TWSTA)|(0<<TWSTO)|(0<<TWWC);

			break;

		case TW_ST_SLA_ACK: // own SLA+R received, acknoledge sent
		case TW_ST_DATA_ACK:
			if (data_index == 0) TWDR = result & 0xFF;
			else TWDR = (result >> 8) & 0xFF;
			//TWDR = data[data_index];
			data_index = (data_index + 1) % 2;
			TWCR &= ~((1<<TWSTO) | (1<<TWEA));

			break;

		case TW_ST_DATA_NACK: // Byte gesendet, kein ACK erhalten.
		case TW_ST_LAST_DATA: // last byte transmitted ACK received     
			TWCR |= (1<<TWEA); // set TWEA to enter slave mode
			break;
	}

	TWCR |= (1<<TWINT);  // set TWINT -> activate TWI hardware
}

void main(void) {
	// TWI-Schnittstelle initiieren.
    sei(); // Sämtliche Interrupts aktivieren.

	TWAR = (MY_TWI_ADDRESS << 1) | 0x00; // Adresse setzten, "Broadcast-Adresse" 0 ignorieren.

	TWCR |= (1<<TWEA) | (1<<TWEN) | (1<<TWIE); // Auf eigene Adresse reagieren (TWEA), TWI-Schnittstelle aktivieren (TWEN) und Interrupt-Benachrichtigungen aktivieren (TWIE)

	// Out-Pin-Setup.
	DDRB |= _BV(DDB0);

	// ADC-Setup
	ADCSRA |= (1<<ADEN); // ADC einschalten.
	//ADMUX  |= ( (1<<REFS1) | (1<<REFS0) ); // select internal reference
	ADMUX |= (1<<REFS0); // Interne Referenz Avcc benutzen.
	ADMUX |= 0;   // Pin 23 (ADC0) als Eingang auswählen.

	// Hauptteil.

	data[0]=0;
	data[1]=0;
	int i, j;
	uint16_t tmp;

	while (1) {
		// Messungen durchführen.
		for (i = 0; i < DATA_ARRAY_LENGTH; i++) {
			ADCSRA |= (1<<ADSC); // Beginnen der Messung.
			while(ADCSRA & (1<<ADSC)); // Warten bis Messung erfolgt ist.
			data[i] = ADCL;
			data[i] += (ADCH << 8);
		}

		// Messwerte nach Größe sortieren.
		for (i = 0; i < (DATA_ARRAY_LENGTH - 1); i++) {
			for (j = (i+1); j < DATA_ARRAY_LENGTH; j++) {
				if (data[i] > data[j]) {
					tmp = data[i];
					data[i] = data[j];
					data[j] = tmp;
				}
			}
		}

		// Median als Ergebnis wählen.
		result = data[DATA_ARRAY_LENGTH / 2];
	}
}
