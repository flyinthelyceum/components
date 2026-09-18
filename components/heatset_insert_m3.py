"""heatset_insert_m3: SUPERSEDED. Do not import.

Created when this box was thought to hold one M3 insert. It holds four lengths, and
they differ by more than 6 mm - so a single M3 module can only ever be right about
diameter and wrong about length for three callers out of four.

Use the sized module instead: heatset_insert_m3x4, heatset_insert_m3x6, heatset_insert_m3x8, heatset_insert_m3x10.

This module deliberately exports nothing. A stale import fails at the point of use with
this message rather than quietly handing back the wrong length.
"""


def __getattr__(name):
    raise AttributeError(
        "heatset_insert_m3 is superseded: the box holds four M3 lengths. "
        "Import one of heatset_insert_m3x4, heatset_insert_m3x6, heatset_insert_m3x8, heatset_insert_m3x10 instead."
    )
