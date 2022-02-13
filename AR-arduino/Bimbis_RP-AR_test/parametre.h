#ifndef PARAMETERS_H
#define PARAMETERS_H

#define debugb true

#define serStart "Axel,Bimbis:),"
#define space ","
#define SERIAL_BAUD 115200

// in milimeters
#define _base "52"
#define _waist "65"
#define _arm1 "150"
#define _arm2 "115"
#define _hook "100"

// if i would ever need double check of mathematic in Arduino
#define i_base 42
#define i_waist 69
#define i_arm1 143
#define i_arm2 96
#define i_hak 75

// pins for servos
#define sr1 3
#define sr2 5   // "twins" angry twin
#define sr3 6   // "twins" normal twin
#define sr4 9
#define sr5 11  // tool: 140-180°

// maximum a minimum pre posledné servo
#define sr5mx 180
#define sr5mi 140

#endif
