/*
* Team Id: eYRC-LM#448
* Author List: Mohan Krishna, Sai Gopal
* Filename: LM_448.c
* Theme: Launch a Module
* Functions: s_portc, buzzer_init, buzzer_on, buzzer_off, write_cmd, write_char, lcd_init, write_string, Write_val,
*            servo_init, servo1, servo2, servo3, open_arm, close_arm, lift_up_arm, lower_down_arm, motor_init, velocity,
*            forward, back, left, right, left2, right2, stop, sharp_left, sharp_right, forward_mm, angle_rotate, sharp_angle_left, 
*            sharp_angle_right, angle_left, angle_right, uart0_init, init_devices, main
* Global Variables: right_motor_count, left_motor_count, kpr,
*                   data, a, calib_flag
*
*/
#define F_CPU 14745600// CPU  frequency provided in Hz
#include <avr/io.h>
#include <util/delay.h>
#include <avr/interrupt.h>
#include <math.h>
volatile unsigned long int right_encoder_count=0;//stores the count of pulses generated by position encoder of right motor
volatile unsigned long int left_encoder_count=0;//stores the count of pulses generated by position encoder of left motor
volatile int kpr = 16;//multiplication factor for right motor error correction
volatile unsigned char data; //to store received data from UDR0
volatile unsigned int k;//a variable used in ISR as an index of the array a[]
volatile unsigned char a[]=" ";//array to store data used for rotation, speed and movement through UART
volatile int calib_flag = 0;//enables or disables the error correction for straight line movement of the robot
#define rs 0//to specify command or data through RS pin of LCD
#define rw 1//read,write enabling for LCD
#define en 2// sets or resets enable pin of LCD
#define buzzer 3 // pin 3 of PORTC is declared as buzzer
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/*
* Function Name: s_portc
* Input:  first argument b is pin or bit number of PORTC and 
*         second argument n takes two values viz. 0 or 1
* Output: sets or clears the respective bit of PORTC
* Logic:  shifts the input to right by the value of b and assigns it to PORTC through bitwise AND or OR operations
* Example Call: s_bitc(5,1);  sets the pin5 of PORTC
*
*/

void s_portc(int b,int n)
{  
      if(n<1)
     {
       PORTC= PORTC&(~(1<<b));
     }
     else
      PORTC= PORTC|( 1<<b);
}
///////////////////////////////////////////////////// BUZZER FUNCTIONS ///////////////////////////////////////////////////////////////////

/*
* Function Name: buzzer_init
* Input:  NONE
* Output: declares the buzzer pin i.e. pin3 of PORTC as output
* Example Call: buzzer_init();
*
*/
void buzzer_init()
{
	DDRC |= 0x80; //setting pin3 of PORTC as output pin
}

/*
* Function Name: buzzer_on
* Input:  NONE
* Output: sets the buzzer pin of PORTC, buzzer tuns on
* Logic:  buzzer pin is set
* Example Call: buzzer_on();
*
*/
void buzzer_on()
{
	s_portc(buzzer,1);//setting buzzer pin of PORTC
}

/*
* Function Name: buzzer_off
* Input:  NONE
* Output: clears the buzzer pin of PORTC, buzzer tuns off
* Logic:  buzzer pin is cleared
* Example Call: buzzer_off();
*
*/
void buzzer_off()
{
	s_portc(buzzer,0);//clearing the buzzer pin of PORTC
}

///////////////////////////////////////////////////// LCD FUNCTIONS /////////////////////////////////////////////////////////////////////

/*
* Function Name: write_cmd
* Input:  this function takes LCD commands as argument
* Output: given command is applied to LCD 
* Logic:  upper nibble of command is fed followed by lower nibble of data to the upper nibble of LCD
* Example Call: write_cmd(0x01);
*
*/
void write_cmd(unsigned char c)
{
	s_portc(rs,0); //clears the rs pin, LCD is set in command mode
	// feeding upper nibble of argument data to upper nibble of the LCD
	PORTC &=0x0f;// clearing the upper nibble of LCD using bitwise and operations
	PORTC|= c&0xf0;// feeding upper nibble of argument data to upper nibble of the LCD
	s_portc(en,1);// puts logic high on enable pin of LCD
	_delay_ms(2);
	s_portc(en,0);// puts logic low on enable pin of LCD completing high to low pulse
	_delay_ms(2);
	// feeding lower nibble of argument data to upper nibble of the LCD
	PORTC &=0x0f; // clearing the upper nibble of LCD using bitwise and operations
	PORTC |=(c<<4)&0xf0;// feeding lower nibble of argument data to upper nibble of the LCD after shifting right by four bits
	s_portc(en,1);// puts logic high on enable pin of LCD
	_delay_ms(2);
	s_portc(en,0);// puts logic low on enable pin of LCD completing high to low pulse
		
}

/*
* Function Name: write_char
* Input:  this function takes data to be printed on LCD as arguments
* Output: given data is displayed on LCD
* Logic:  upper nibble of data is fed followed by lower nibble of data to the upper nibble of LCD
* Example Call: write_data('c');
*
*/
void write_char(unsigned char c)
{
	s_portc(rs,1); //sets the rs pin, LCD is set in data mode
	// feeding upper nibble of argument data to upper nibble of the LCD
	PORTC &= 0x0f;// clearing the upper nibble of LCD using bitwise and operations
	PORTC |= c & 0xf0;// feeding upper nibble of argument data to upper nibble of the LCD
	s_portc(en, 1);// puts logic high on enable pin of LCD
	_delay_ms(2);
	s_portc(en, 0);// puts logic low on enable pin of LCD completing high to low pulse
	_delay_ms(2);
	// feeding lower nibble of argument data to upper nibble of the LCD
	PORTC &=0x0f; // clearing the upper nibble of LCD using bitwise and operations
	PORTC |= (c << 4) & 0xf0;// feeding lower nibble of argument data to upper nibble of the LCD after shifting right by four bits
	s_portc(en, 1);// puts logic high on enable pin of LCD
	_delay_ms(2);
	s_portc(en, 0);// puts logic low on enable pin of LCD completing high to low pulse
}

/*
* Function Name: lcd_init()
* Input:  NONE
* Output: initializes the LCD of PORTC
* Example Call: lcd_init();  
*
*/
void lcd_init()
{   
	DDRC |= 0xf7;// LCD is initialized by setting LCD related pins as outputs 
	// LCD is initialized in 4-bit mode
	write_cmd(0x33);
	write_cmd(0x32);
	write_cmd(0x28);
	write_cmd(0x06);
	write_cmd(0x01);// command to clear the LCD display
	write_cmd(0x0E);// command to turn on LCD display with no cursor 
	write_cmd(0x80);// command to position the cursor at first row first column
	s_portc(rw, 0);// LCD set to write mode
}

/*
* Function Name: lcd_cursor
* Input:  first argument x is row number, 0 for 1st row and 1 for 2nd row
*         second argument y is column number, takes the values 0 to 15
* Output: takes the cursor to specified position on LCD
* Example Call: lcd_cursor(0,4);
*
*/

void lcd_cursor(int x, int y)
{   // x=0 for row1 and x=1 for row2
	if(x == 0)
	write_cmd(0x80 + y);// increments the value by y for moving to the respective column of row1
	else
	write_cmd(0xc0 + y);// increments the value by y for moving to the respective column of row2
}

/*
* Function Name: write_string
* Input:  input is a string or a character array that is to be printed
* Output: prints the message on LCD
* Logic:  prints the character elements of the array arr[] one by one 
          until it finds the null character '\0'
* Example Call: write_string("HELLO"); or write_string(a); 
*
*/
void write_string(char arr[])
{
	for(int i = 0 ; arr[i] != '\0' ; i++)
	{
		write_char(arr[i]);// a character on LCD 
	}
}

/*
* Function Name: write_val
* Input:  first argument x is for selecting the row of LCD, takes values 0 or 1
*         second argument y is for selecting the column of LCD, takes values 0 to 15
          third argument a is any integer value of at most 3 digits that is to be printed
* Output: prints the value up to 3 digits at a given position on the LCD
* Logic:  separates the digits of hundreds place, tens place and ones place using math operations 
          and prints them one after the other on consecutive positions
* Example Call: write_val(1,4,398); or write_val(1,4,a);
*
*/

void write_val(int x, int y, int a)
{
	lcd_cursor(x, y);// positioning the cursor on LCD
	write_char(a / 100 + 48);// separating the digit in hundreds place and converting 
	                       // it to respective character and then printing it on LCD
	write_char(10 * (a / 100.0 - a / 100) + 48);// separating the digit in tens place and converting 
	                                   // it to respective character and then printing it on LCD
	write_char(10 * (a / 10.0 - a / 10 ) + 48);// separating the digit in ones place and converting 
	                                 // it to respective character and then printing it on LCD
}

///////////////////////////////////////////////////// SERVO FUNCTIONS //////////////////////////////////////////////////////////////////
/*
* Function Name: servo_init
* Input:  NONE
* Output: initializes the timer for PWM generation required for servo operations
* Logic:  NONE
* Example Call: servo_init();
*
*/
void servo_init()
{   DDRB  = DDRB | 0xE0;  //making PORTB 7,6,5, pins as output
	PORTB = PORTB | 0xE0;
    TCCR1B = 0x00; //stops Timer1
    TCNT1H = 0xFC; //Counter high value to which OCR1xH value is to be compared with
    TCNT1L = 0x01;	//Counter low value to which OCR1xH value is to be compared with
    OCR1AH = 0x03;	//Output compare Register high value for servo 1
    OCR1AL = 0xFF;	//Output Compare Register low Value For servo 1
    OCR1BH = 0x03;	//Output compare Register high value for servo 2
    OCR1BL = 0xFF;	//Output Compare Register low Value For servo 2
    OCR1CH = 0x03;	//Output compare Register high value for servo 3
    OCR1CL = 0xFF;	//Output Compare Register low Value For servo 3
    ICR1H  = 0x03;	
    ICR1L  = 0xFF;
    TCCR1A = 0xAB; /*{COM1A1=1, COM1A0=0; COM1B1=1, COM1B0=0; COM1C1=1 COM1C0=0}
 					For Overriding normal port functionality to OCRnA outputs.
				  {WGM11=1, WGM10=1} Along With WGM12 in TCCR1B for Selecting FAST PWM Mode*/
 	TCCR1C = 0x00;
 	TCCR1B = 0x0C; //WGM12=1; CS12=1, CS11=0, CS10=0 (Prescaler=256)
	
}

/*
* Function Name: servo1
* Input:  deg-> takes the angle for servo rotation in degrees, takes the vaues from 0 to 180
* Output: rotates the servo through deg degrees
* Logic:  the angle in the range 0 to 180 degrees is mapped to 0 to 255
*         and the PWM signal is generated accordingly 
* Example Call: servo1(90);
*
*/
void servo1(unsigned char deg)
{
	float servoPosition = 0;
	servoPosition = ((float)deg / 1.86) + 35.0;//angle required is mapped to the range 0 to 255
	OCR1AH = 0x00;
	OCR1AL = (unsigned char) servoPosition;//mapped value is assigned to output compare register
}

/*
* Function Name: servo2
* Input:  deg-> takes the angle for servo rotation in degrees, takes the vaues from 0 to 180
* Output: rotates the servo through deg degrees
* Logic:  the angle in the range 0 to 180 degrees is mapped to 0 to 255
*         and the PWM signal is generated accordingly
* Example Call: servo2(90);
*
*/
void servo2(unsigned char deg)
{
	float servoPosition = 0;
	servoPosition = ((float)deg / 1.86) + 35.0; //angle required is mapped to the range 0 to 255
	OCR1BH = 0x00;
	OCR1BL = (unsigned char) servoPosition;//mapped value is assigned to output compare register
}

/*
* Function Name: servo3
* Input:  deg-> takes the angle for servo rotation in degrees, takes the vaues from 0 to 180
* Output: rotates the servo through deg degrees
* Logic:  the angle in the range 0 to 180 degrees is mapped to 0 to 255
*         and the PWM signal is generated accordingly
* Example Call: servo3(90);
*
*/
void servo3(unsigned char degrees)
{
	float servoPosition = 0;
	servoPosition = ((float)degrees / 1.86) + 35.0;//angle required is mapped to the range 0 to 255
	OCR1CH = 0x00;
	OCR1CL = (unsigned char) servoPosition;//mapped value is assigned to output compare register
}

/*
* Function Name: open_arm
* Input:  NONE
* Output: opens the grip of the arm 
* Logic:  NONE
* Example Call: open_arm();
*
*/
void open_arm(void)
{
	servo2(180);
	_delay_ms(2);
	servo3(5);
	return;
}


/*
* Function Name: close_arm
* Input:  NONE
* Output: closes the grip of the arm, captures the object
* Logic: NONE
* Example Call: close_arm();
*
*/
void close_arm(void)
{
	servo2(5);
	_delay_ms(2);
	servo3(180);
	return;
}


/*
* Function Name: lift_up_arm
* Input:  NONE
* Output: lifts the arm up
* Logic:  NONE
* Example Call: lift_up_arm();
*
*/
void lift_up_arm(void)
{
	servo1(30);
	return;
}


/*
* Function Name: lower_down_arm
* Input:  NONE
* Output: lowers down the arm
* Logic:  NONE
* Example Call: lower_down_arm();
*
*/
void lower_down_arm(void)
{
	servo1(155);
	return;
}

/////////////////////////////////////////////////////// MOTOR FUNCTIONS ////////////////////////////////////////////////////////////////
/*
* Function Name: motor_init
* Input:  NONE
* Output: initializes the motor pins as output 
*         initializes the Timer5 for PWM generation for motor speed, required for motor operations
* Logic:  NONE
* Example Call: motor_init();
*
*/

void motor_init() 
{
	DDRA |= 0x0f;//initializing PORTA lower nibble as output for motors
    PORTA = PORTA & 0xF0;
	DDRL |= 0x18;//initializing PORTL3 and PORTL4 pins as output for PWM generation
	DDRE &= 0xCF;// initializing PORTE 4 and 5 pins as inputs
	PORTE |= 0x30;//Enable internal pull-up for PORTE 4 pin
    TCCR5B = 0x00;	//Stops the timer
	TCNT5H = 0xFF;	//Counter higher 8-bit value to which OCR5xH value is compared with
	TCNT5L = 0x01;	//Counter lower 8-bit value to which OCR5xH value is compared with
	OCR5AH = 0x00;	//Output compare register high value for Left Motor
	OCR5AL = 0xFF;	//Output compare register low value for Left Motor
	OCR5BH = 0x00;	//Output compare register high value for Right Motor
	OCR5BL = 0xFF;	//Output compare register low value for Right Motor
	OCR5CH = 0x00;	//Output compare register high value for Motor C1
	OCR5CL = 0xFF;	//Output compare register low value for Motor C1
	TCCR5A = 0xA9;	/*{COM5A1=1, COM5A0=0; COM5B1=1, COM5B0=0; COM5C1=1 COM5C0=0}
 					  For Overriding normal port functionality to OCRnA outputs.
				  	  {WGM51=0, WGM50=1} Along With WGM52 in TCCR5B for Selecting FAST PWM 8-bit Mode*/
	
	TCCR5B = 0x0B;	//WGM12=1; CS12=0, CS11=1, CS10=1 (Prescaler=64)
	EICRB |= 0x0a;// INT5,4 are set to trigger with falling edge
	EIMSK |= 0x30;// Enable Interrupt INT5,4 for right and left position encoders respectively
}

/*
* Function Name: velocity
* Input:  first argument x indicates speed of the left motor, takes values from 0 to 255
*         second argument y indicates speed of the right motor, takes values from 0 to 255
* Output: initializes the timer for PWM generation for motor speed, required for servo operations
* Logic:  speed value is assigned to output compare registers and the pwm is generated accordingly
* Example Call: velocity(255,255);
*
*/
void velocity(unsigned int x, unsigned int y)
{
	OCR5AL = x;
	OCR5BL = y;
}

/*
* Function Name: forward
* Input:  NONE
* Output: moves the robot forward
* Logic:  one terminal of the motor is given high input and the other terminal is given low input
*         to rotate the motor in required direction. both motors are driven in forward to move the robot forward
* Example Call: forward();
*
*/
void forward() 
{  
   PORTA = 0x06;
}

/*
* Function Name: back
* Input:  NONE
* Output: moves the robot in backward direction
* Logic:  one terminal of the motor is given high input and the other terminal is given low input
*         to rotate the motor in required direction. both motors are driven in backward direction 
*         to move the robot forward
* Example Call: back();
*
*/
void back()    
{  
   PORTA = 0x09;
}

/*
* Function Name: left
* Input:  NONE
* Output: turns the robot to left 
* Logic:  one terminal of the motor is given high input and the other terminal is given low input
*         to rotate the motor in required direction. right motor is rotated in forward direction 
*         and the other motor is kept still to turn the robot to left
* Example Call: left();
*
*/
void left()   
{  
   PORTA = 0x04;
}

/*
* Function Name: right
* Input:  NONE
* Output: turns the robot to right 
* Logic:  one terminal of the motor is given high input and the other terminal is given low input
*         to rotate the motor in required direction. left motor is rotated in forward direction
*         and the other motor is kept still to turn the robot to right
* Example Call: right();
*
*/
void right()   
{  
   PORTA = 0x02;
}

/*
* Function Name: left2
* Input:  NONE
* Output: turns the robot to left 
* Logic:  one terminal of the motor is given high input and the other terminal is given low input
*         to rotate the motor in required direction. left motor is rotated in backward direction
*         and the other motor is kept still to turn the robot to left
* Example Call: left2();
*
*/
void left2()   
{  
   PORTA = 0x01;
}

/*
* Function Name: right2
* Input:  NONE
* Output: turns the robot to right
* Logic:  one terminal of the motor is given high input and the other terminal is given low input
*         to rotate the motor in required direction. right motor is rotated in backward direction
*         and the other motor is kept still to turn the robot to right
* Example Call: right2();
*
*/
void right2() 
{  
   PORTA = 0x08;
}

/*
* Function Name: stop
* Input:  NONE
* Output: turns the robot to left
* Logic:  one terminal of the motor is given high input and the other terminal is given low input
*         to rotate the motor in required direction. left motor is rotated in backward direction
*         and the other motor is kept still to turn the robot to left
* Example Call: stop();
*
*/
void stop()    
{  
   PORTA = 0x00;
}

/*
* Function Name: sharp_left
* Input:  NONE
* Output: turns the robot to right
* Logic:  one terminal of the motor is given high input and the other terminal is given low input
*         to rotate the motor in required direction. left motor is rotated in backward direction
*         and the other motor is rotated in other direction to turn the robot to left
* Example Call: sharp_left();
*
*/
void sharp_left()  
{  
   PORTA = 0x5;
}

/*
* Function Name: sharp_right
* Input:  NONE
* Output: turns the robot to right
* Logic:  one terminal of the motor is given high input and the other terminal is given low input
*         to rotate the motor in required direction. left motor is rotated in forward direction
*         and the other motor is kept still to turn the robot to right
* Example Call: sharp_right();
*
*/
void sharp_right() 
{  
   PORTA = 0x0a;
}


/*
* Interrupt Service Routine
* Input:        NONE
* Output:       Increments left wheel ShaftCount i.e. left_encoder_count
* Logic:        Whenever shaft rotates pulse is generated by the position encoder
*               which thereby generates an interrupt and shaft count gets incremented.
* Example Call: NONE
*/
ISR(INT4_vect)
{
	left_encoder_count++;
}

/*
* Interrupt Service Routine
* Input:        NONE
* Output:       Increments right wheel ShaftCount i.e. right_encoder_count
* Logic:        Whenever shaft rotates pulse is generated by the position encoder
*               which thereby generates an interrupt and shaft count gets incremented.
* Example Call: NONE
*/
ISR(INT5_vect)
{
	right_encoder_count++;
}

/*
* Function Name: forward_mm
* Input:  distance in mm
* Output: moves the robot through specified distance (in mm)
* Logic:  number of pulses needed to be generated is calculated and the robot is moved forward
*         until required number of pulses are generated by position encoders  
* Example Call: forward_mm(900);
*
*/
void forward_mm(unsigned int DistanceInMM)
{
	float ReqdShaftCount = 0;
	unsigned long int ReqdShaftCountInt = 0;
	ReqdShaftCount = DistanceInMM / 5.338; // division by resolution to get shaft count
	ReqdShaftCountInt = (unsigned long int) ReqdShaftCount;
	right_encoder_count = 0;
	left_encoder_count = 0;
	forward();
	while(1) //error correction for the robot to move in a straight path
	{   // difference in the number of pulses generated by the position encoders is taken as error
		int error = right_encoder_count - left_encoder_count ;
		
		if((right_encoder_count > ReqdShaftCountInt) | (left_encoder_count > ReqdShaftCountInt))
		{
			break;
		}
		
		else if(error < 0)
		{
			velocity(255, 255);//_delay_ms(10);
		}
		else if(error > 0)
		{    //rv stores the speed value of the right motor after correcting error
			unsigned char rv = 255 - (error * kpr); // kpr is an error correction factor for right motor
			velocity(255,rv); 						//_delay_ms(10);
		}		
		
	}
	stop(); //Stop robot
}

/*
* Function Name: angle_rotate
* Input:         angle by which the bot must rotate
* Output:        Rotates the robot through specified angle in any direction specified in previous statement
* Logic:         
* Example Call:  angle_rotate(120);
*/
void angle_rotate(unsigned int Degrees)
{
	float ReqdShaftCount = 0;
	unsigned long int ReqdShaftCountInt = 0;

	ReqdShaftCount = (float) Degrees / 4.090; // division by resolution to get shaft count
	ReqdShaftCountInt = (unsigned int)ReqdShaftCount;
	right_encoder_count = 0;
	left_encoder_count = 0;
	while (1)
	{   //if the either one of right_encoder_count or left_encoder_count exceeds the required shaft count the loop breaks. 
		if((right_encoder_count >= (ReqdShaftCountInt)) | (left_encoder_count >= (ReqdShaftCountInt)))
		break;
	}
	stop(); //Stop robot
}


/*
* Function Name: sharp_angle_right
* Input:         angle by which the bot must rotate
* Output:        Rotates the bot through specified angle in anticlockwise direction (sharp)
* Logic:         same as above (angle_rotate)
* Example Call:  left_degrees(90);
*/
void sharp_angle_right(unsigned int Degrees)
{
	// 88 pulses for 360 degrees rotation 4.090 degrees per count
	sharp_right(); //Turn right
	angle_rotate(Degrees);
}


/*
* Function Name: sharp_angle_left
* Input:         angle by which the bot must rotate
* Output:        Rotates the bot through specified angle in clockwise direction (sharp)
* Logic:         same as above (angle_rotate)
* Example Call:  right_degrees(90);
*/
void sharp_angle_left(unsigned int Degrees)
{
	// 88 pulses for 360 degrees rotation 4.090 degrees per count
	sharp_left(); //Turn left
	angle_rotate(Degrees);
}


/*
* Function Name: angle_left
* Input:         angle by which the bot must rotate
* Output:        Rotates the bot through specified angle in anticlockwise direction (soft, forward)
* Logic:         same as above (angle_rotate)
* Example Call:  soft_left_degrees(90);
*/
void angle_left(unsigned int Degrees)
{
	// 176 pulses for 360 degrees rotation 2.045 degrees per count
	left(); //Turn soft left
	Degrees *= 2;
	angle_rotate(Degrees);
}


/*
* Function Name: angle_right
* Input:         angle by which the bot must rotate
* Output:        Rotates the bot through specified angle in clockwise direction (soft, forward)
* Logic:         same as above (angle_rotate)
* Example Call:  soft_right_degrees(90);
*/
void angle_right(unsigned int Degrees)
{
	// 176 pulses for 360 degrees rotation 2.045 degrees per count
	right();  //Turn soft right
	Degrees =* 2;
	angle_rotate(Degrees);
}

/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/*
* Function Name: uart0_init
* Input:         NONE
* Output:        initializes UART0 for xbee communication
* Logic:         NONE
* Example Call:  uart0_init();
*/
void uart0_init()
{
	UCSR0B = 0x00; //disable while setting baud rate
	UCSR0A = 0x00;
	UCSR0C = 0x06;
	UBRR0L = 0x5F; //set baud rate lo
	UBRR0H = 0x00; //set baud rate hi
	UCSR0B = 0x98;

}

/*
* Function Name: init_devices
* Input:         NONE
* Output:        initializes all the devices required
* Logic:         NONE
* Example Call:  init_devices();
*/
void init_devices()// initializes all the devices
{ 
  cli();
  uart0_init();
  buzzer_init();
  lcd_init();
  motor_init();
  servo_init();
  sei();
}


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

ISR(USART0_RX_vect) 		// ISR for receive complete interrupt
{
	data = UDR0;  	// stores the data in the received buffer into variable data
	if(data == 'C') //turns the buzzer off
	{
		buzzer_off();return;
	}
	else if(data == 'o') // opens the grip of the arm
	{
		servo2(180);
		_delay_ms(2);
		servo3(5);
		_delay_ms(2);return;
	}
	else if(data == 'c') // closes the grip of the arm
	{   servo3(180);
		_delay_ms(2);
		servo2(5);
		_delay_ms(2);return;
	}
	else if(data=='x')  // lowers down the arm
	{
		servo1(155);
		_delay_ms(5);return;
	}
	else if(data=='i') // lifts the arm up
	{
		servo1(30);
		_delay_ms(5);return;
	}
	else if(data == 'I')
	{
		lower_down_arm();// lowers down the arm
		_delay_ms(700);
		open_arm();      // releases the object
		_delay_ms(500);
		lift_up_arm();   // lifts the arm up
		return;
	}
	else if(data == 'X')
	{
		lower_down_arm();// lowers down the arm
		_delay_ms(700);
		close_arm();     // captures the object
		_delay_ms(500);
		lift_up_arm();   // lifts up the arm
		return;
	}
	else if(data == 'O') // turns the buzzer on
	{
		buzzer_on();return;
	}
	else if(data == '<') // initializes the array to store the upcoming data until '>' if received
	{
		k=0;
		return;
	}
	// used to determine if the received data is for angle, distance or velocity
	else if(data == 'a' || data == 'k' || data == 'q' || data == 'w' || data == 'd')
	{
		a[k++]=data;
		return;
	}
    
	else if(data== '>') // stops storing the received values into array a and further manipulation of received data is started
	{
		sei();
		k--;
		unsigned int b[3];
		int j = 0;
		while(k  >0){
			// a[] stores the received angle or distance values until '>' is received .
			// so their order is reversed and converted to integer digits before storing them in b[]
			b[j] = a[k] - 48; //converts the numerical characters received into integers
			k--;
			j++;
		}
		j--;
		unsigned int calc_value = 0;
		while(j >= 0){
			calc_value = calc_value + b[j] * pow(10, j);// the three individual integer elements or digits 
			                                       //in the array b are combined to form a three digit number
			j--;
		}
		if(a[0] == 'a')      //when 'a' is received, the data stored in calc_value is taken as angle for turning left
		{
			sharp_angle_left(calc_value);
			k=0;
			return;
		}
		else if(a[0] == 'k') //when 'k' is received, the data stored in calc_value is taken as angle for turning right
		{
			sharp_angle_right(calc_value);
			k=0;
			return;
		}
		else if(a[0] == 'q')  //when 'q' is received, the data stored in calc_value is taken as angle for turning left
		{
			angle_left(calc_value);
			k = 0;
			return;
		}
		else if(a[0] == 'w')  //when 'w' is received, the data stored in calc_value is taken as angle for turning right
		{
			angle_right(calc_value);
			k = 0;
			return;
		}
		else if(a[0] == 'd') // takes the received value as distance to move forward
		{
			forward_mm(calc_value);
			k = 0;
			return;
		}
	}
	else if(k > 0)
	{
		a[k++] = data;
		return ;
	}
	else if(data == '8')  //when received robot moves forward and calib_flag is set and the error correction turns on  
	{
		forward();
		right_encoder_count = 0;
		left_encoder_count = 0;
		calib_flag = 1;
		return;
	}
	else if(data == '2')  //when received robot moves backward and calib_flag is cleared and the error correction turns off
	{
		back();
		right_encoder_count = 0;
		left_encoder_count = 0;
		calib_flag = 0;
		return;
	}
	else if(data == '4') //when received robot turns left and calib_flag is cleared and the error correction turns off
	{
		calib_flag = 0;
		sharp_left();
		return;
	}
	else if(data == '6') //when received robot turns right and calib_flag is cleared and the error correction turns off
	{
		calib_flag = 0;
		sharp_right();
		return;
	}
	else if(data == '5') //when received robot stops and calib_flag is cleared and the error correction turns off
	{
		calib_flag = 0;
		stop();
		return;
	}
	else if(data == '1') //when received robot turns left and calib_flag is cleared and the error correction turns off
	{
		calib_flag = 0;
		left2();
		return;
	}
	else if(data == '3') //when received robot turns right and calib_flag is cleared and the error correction turns off
	{
		calib_flag = 0;
		right2();
		return;
	}
	else if(data == '7') //when received robot turns left and calib_flag is cleared and the error correction turns off
	{
		calib_flag = 0;
		left();
		return;
	}
	else if(data == '9') //when received robot turns right and calib_flag is cleared and the error correction turns off
	{
		calib_flag = 0;
		right();
		return;
	}
	
}
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

/*
* Function Name: main
* Input:  NONE
* Output: Initializes all the devices used and if calib_flag is set error correction will be done to move the bot in a straight line
* Logic:  error = (right_encoder_count - left_encoder_count), depending upon the error velocity of right motor is controlled
          (we have observed that right motor is moving faster than the left motor , so if error is positive right motor velocity is reduced 
		   or else the velocity will be 255)
* Example Call: called automatically by operating system;
*
*/
int main(void)
{    
	init_devices();// initializing the robot's peripherals
	lcd_cursor(1, 6); // positions the cursor on LCD
	write_string("LM-448");// prints the string "LM-448" on LCD
	//initial velocity of the motors is set as maximum
	velocity(255, 255);
	//initially the arm is lifted up and grip is opened
	servo1(30);
	servo2(180);
	servo3(15);
	
	while(1)
	{   // error correction for the straight line movement of the robot
		if(calib_flag == 1)
		{
			// difference in the number of pulses generated by the position encoders is taken as error
			int error = right_encoder_count - left_encoder_count ;
			if(error < 0)
			{
				velocity(255, 255);
				_delay_ms(5);
			}
			else if(error > 0)
			{   //rv stores the speed value of the right motor after correcting error
				unsigned char rv = 255 - (error * kpr);// kpr is an error correction factor for right motor
				velocity(255, rv);
				_delay_ms(5);
			}
		}
	}
}
