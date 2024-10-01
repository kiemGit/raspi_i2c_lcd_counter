# raspi_i2c_lcd_counter
counting vehicle using button and rasberry pi and i2c LCD prototype only


# "1": "wiring i2c LCD to rasberry"

	"1": "(i2c) VCC  - (raspi) 5V (pin 2 or 4)",
	"2": "(i2c) GND  - (raspi) GND (pin 6)",
	"3": "(i2c) SDA  - (raspi) SDA (pin 3 - GPIO 2)",
	"4": "(i2c) SCL  - (raspi) SCL (pin 5 - GPIO 3)"

"3": "wiring button for counting to rasberry"

	"1": "(button) button 1 (counter) add 1: COM (pin 19 - GPIO 10) + GND(PIN 14)",
	"2": "(button) button 2 (reset): COM (pin 16 - GPIO 23) + GND(PIN 14)",
	"3": "check address i2c lcd [ i2cdetect -y 1 ]"

	

