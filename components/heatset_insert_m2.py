"""heatset_insert_m2: SUPERSEDED. Do not import.

Created when this box was thought to hold one M2 insert. It holds four lengths, and
they differ by more than 6 mm - so a single M2 module can only ever be right about
diameter and wrong about length for three callers out of four.

Use the sized module instead: heatset_insert_m2x4, heatset_insert_m2x6, heatset_insert_m2x8, heatset_insert_m2x10.

This module deliberately exports nothing. A stale import fails at the point of use with
this message rather than quietly handing back the wrong length.
"""


def __getattr__(name):
    raise AttributeError(
        "heatset_insert_m2 is superseded: the box holds four M2 lengths. "
        "Import one of heatset_insert_m2x4, heatset_insert_m2x6, heatset_insert_m2x8, heatset_insert_m2x10 instead."
    )
