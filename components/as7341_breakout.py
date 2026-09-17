"""AS7341 spectral sensor breakout, the Adafruit STEMMA QT board (#4698).

Every row is calipered now. Two of them contradicted Adafruit's published
figures and changed grow-lab's canopy case: the STEMMA QT sockets stand 4.7,
not the 2.9 a bench photo suggested, and the mounting holes are 2.29, not the
2.5 the product page states -- an M2.5 does not pass its own board.

The outline is 25.68 x 17.78: a shade over the published 25.4 in length and
exactly 0.700 in across. The sensor window is NOT centred in Y, which the
length overrun had made it tempting to infer -- it sits 8.76 from the LED edge
against 9.02 from the header edge.

Constant names below are the caliper sheet's rows.
"""
UNIT = "mm"
PCB_L = 25.68  # CALIPER 2026-09-15 JR
PCB_W = 17.78  # CALIPER 2026-09-17 JR
HOLE_PITCH_X = 20.17  # CALIPER 2026-09-15 JR
HOLE_PITCH_Y = 12.62  # CALIPER 2026-09-15 JR
HOLE_DIA = 2.29  # CALIPER 2026-09-15 JR
LED_Y_FROM_LED_EDGE = 2.24  # CALIPER 2026-09-15 JR
QT_SOCKET_H = 4.7  # CALIPER 2026-09-15 JR
SENSOR_X_FROM_EDGE = 12.93  # CALIPER 2026-09-15 JR
SENSOR_Y_FROM_LED_EDGE = 8.76  # CALIPER 2026-09-15 JR
PKG_H = 1.42  # CALIPER 2026-09-15 JR
THICKNESS = 1.6  # CALIPER 2026-09-15 JR
