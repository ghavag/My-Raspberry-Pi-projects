#include <stdio.h>

#define DATA_ARRAY_LENGTH 5
unsigned int data[DATA_ARRAY_LENGTH];

int main() {
	unsigned int tmp, i, j;

	data[0] = 9159;
	data[1] = 555;
	data[2] = 11417;
	data[3] = 9077;
	data[4] = 10385;

	for (i = 0; i < (DATA_ARRAY_LENGTH - 1); i++) {
		for (j = (i+1); j < DATA_ARRAY_LENGTH; j++) {
			if (data[i] > data[j]) {
				tmp = data[i];
				data[i] = data[j];
				data[j] = tmp;
			}
		}
	}

	printf("Sorted array is:");
	for (i = 0; i < DATA_ARRAY_LENGTH; i++) {
		printf(" %i", data[i]);
	}
	printf("\n\n");

	printf("Median is: %i\n", data[DATA_ARRAY_LENGTH / 2]);
	
	return 0;
}
