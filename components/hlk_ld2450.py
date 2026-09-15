"""hlk_ld2450: Hi-Link HLK-LD2450 24 GHz mmWave radar module.

Connector is a 4-pin JST ZH (1.5 mm pitch): 0.172 in outside-to-outside over 3 gaps
reads 1.46 mm. A single-pitch caliper read came in at 0.068 in and was an edge
reading; trust the row span. Not GH 1.25 mm, not SH 1.0 mm.
"""
UNIT = "mm"
CONN_PITCH = 1.5  # CALIPER 2026-09-15 JR
CONN_PINS = 4  # CALIPER 2026-09-15 JR
CONN_ROW_SPAN = 4.37  # CALIPER 2026-09-15 JR
