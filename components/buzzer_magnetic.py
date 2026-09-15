"""Passive magnetic buzzer, through-hole, driven by a PWM pin.

BODY_H is the can alone; TERMINAL_H is how far the pins project beyond it, so the
clearance a board or enclosure must allow is BODY_H + TERMINAL_H.

Contains a coil and a ferromagnetic diaphragm, so it counts as metal for the
purposes of any nearby 13.56 MHz reader antenna keep-out.

Measured 2026-09-15 (node-platform).
"""
UNIT = "mm"
DIA = 11.938  # CALIPER 2026-09-15 JR
BODY_H = 8.484  # CALIPER 2026-09-15 JR
TERMINAL_H = 5.283  # CALIPER 2026-09-15 JR
