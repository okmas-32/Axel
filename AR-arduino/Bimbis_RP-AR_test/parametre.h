#ifndef PARAMETERS_H
#define PARAMETERS_H

#define debugb false
#define justdbg false
#define ARMservo true

#define serStart "Axel,Bimbis:),"
#define space ","
#define SERIAL_BAUD 115200

// v milimetroch
#define _base "52"
#define _waist "65"
#define _arm1 "150"
#define _arm2 "115"
#define _hook "100"

// keby bolo treba prekontrolovať matematiku na Arduine samotnom
#define i_base 42
#define i_waist 69
#define i_arm1 143
#define i_arm2 96
#define i_hak 75

// piny na servá
#define sr1 3
#define sr2 5   // "twins" angry twin
#define sr3 6   // "twins" normal twin
#define sr4 9
#define sr5 10
#define sr6 11  // tool: 140-180°

// maximum a minimum pre posledné servo
// note je to pre kontrolu seriových dát takže "twins" sa sem nepočítajú
#define ser1max 180
#define ser1min 1

#define ser2max 180
#define ser2min 1

#define ser3max 180
#define ser3min 1

#define ser4max 180
#define ser4min 1

// chnapaky
#define ser5max 180
#define ser5min 140

#endif
