"""heatset_insert_m2x4: brass heat-set insert, M2 thread, 4 mm nominal length.

From the lyceum's box, measured 2026-09-18. The vendor labels this
"M2 x 4 x 3.5mm", i.e. thread x length x BODY diameter.

OD HERE IS OVER THE KNURL, which is what a boss has to be sized to, and the knurl
stands proud of the body figure on the label - about 0.42 mm on M3, M4 and M5, but only 0.03 on M2, so the M2 label is effectively the knurl already.
Sizing a boss from the label rather than from OD is what bowed the first test posts
outward and pushed melt up through the thread.

A boss wants 0.30-0.50 mm of DIAMETRAL interference against OD, measured on the hole
as it comes off the machine, not as modelled.
"""
UNIT = "mm"
OD = 3.531  # CALIPER 2026-09-18 JR
LENGTH = 3.937  # CALIPER 2026-09-18 JR
