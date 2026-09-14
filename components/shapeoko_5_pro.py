"""Carbide3D Shapeoko 5 Pro, the machine itself (fabrication cnc_shapeoko).

Only what a caliper has touched. The leg-hole block and wall thickness in
fabrication's params.py are also calipered (2026-09-03) and remain there for
now; move them here with `components measure` when that file is next opened.
"""
UNIT = "mm"
GUSSET_PLATE_T = 6.35  # CALIPER 2026-09-02 JR
