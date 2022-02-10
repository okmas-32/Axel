#ifndef PARAMETERS_H
#define PARAMETERS_H

#define debugb true

#define serStart "Axel,joy,"
#define sspace ","
#define SERIAL_BAUD 115200

#define _maxj "1024"  // maximum joisticku v každej osi
#define _off "20"     // +- 20 center (dead zone of joystick)

// Joystick 1:
#define _VRx1 0       // X analogovy Pin 0
#define _VRy1 1       // Y analogovy Pin 1
#define _SW1 2        // switch Jozsticku 1 na porte 4


// Joystick 2:
#define _VRx2 2       // X analogovy Pin 2
#define _VRy2 3       // Y analogovy Pin 3
#define _SW2 3        // switch Jozsticku 2 na porte 5

// tlačítka na joystik obale
#define _SW3 4    // digital pin 4
#define _SW4 5    // digital pin 5
#define _SW5 6    // digital pin 6
#define _SW6 7    // digital pin 7
#define _SW7 8    // digital pin 8

#endif
