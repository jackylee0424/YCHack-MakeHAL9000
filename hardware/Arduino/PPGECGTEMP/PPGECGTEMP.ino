/******************************************************************************
Temperature pins: yellow to SCL, black to SDA (Pro Micro SDA-Pin2, SCL-Pin 3)
PPG: white to pin 5
ECG: yellow to A0
******************************************************************************/
#include <i2cmaster.h>
#include <FreqCounter.h>

unsigned long frq;
int cnt;
int max_c;
int min_c;
float celcius;
float fahrenheit;

void setup() {
  // initialize the serial communication:
  Serial.begin(115200);
  
  // ecg
  pinMode(10, INPUT); // Setup for leads off detection LO +
  pinMode(11, INPUT); // Setup for leads off detection LO -
  
  // temperature
  i2c_init(); //Initialise the i2c bus
  PORTC = (1 << PORTC4) | (1 << PORTC5);//enable pullups
}

void resetCounter(){
  cnt=0;
  min_c=max_c;
  max_c=0;
}

void getFreq(){
  // wait if any serial is going on
  FreqCounter::f_comp=10;   // Cal Value / Calibrate with professional Freq Counter
  FreqCounter::start(7);  // 100 ms Gate Time

  while (FreqCounter::f_ready == 0) 

  frq=FreqCounter::f_freq;
  
  cnt++;
  
  if (frq>max_c){
    max_c=frq;
  }
  
  if (frq<min_c){
    min_c=frq;
  }
}

void getTemperature(){
    int dev = 0x50<<1;
    int data_low = 0;
    int data_high = 0;
    int pec = 0;
    
    i2c_start_wait(dev+I2C_WRITE);
    i2c_write(0x07);
    
    // read
    i2c_rep_start(dev+I2C_READ);
    data_low = i2c_readAck(); //Read 1 byte and then send ack
    data_high = i2c_readAck(); //Read 1 byte and then send ack
    pec = i2c_readNak();
    i2c_stop();
    
    //This converts high and low bytes together and processes temperature, MSB is a error bit and is ignored for temps
    double tempFactor = 0.02; // 0.02 degrees per LSB (measurement resolution of the MLX90614)
    double tempData = 0x0000; // zero out the data
    int frac; // data past the decimal point
    
    // This masks off the error bit of the high byte, then moves it left 8 bits and adds the low byte.
    tempData = (double)(((data_high & 0x007F) << 8) + data_low);
    tempData = (tempData * tempFactor)-0.01;
    
    celcius = tempData - 273.15;
    fahrenheit = (celcius*1.8) + 32;
}

void loop() {
  getFreq();
  getTemperature();
  Serial.print(millis());
  Serial.print(" ");
  Serial.print(celcius);
  Serial.print(" ");
  Serial.print(fahrenheit);
  Serial.print(" ");
  Serial.print(frq);
  Serial.print(" ");
  if((digitalRead(10) == 1)||(digitalRead(11) == 1)){
    Serial.println('0');
  }
  else{
    // send the value of analog input 0:
    
    Serial.println(analogRead(A0));
  }
  //Wait for a bit to keep serial data from saturating
  delay(15);
}

