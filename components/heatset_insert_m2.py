"""heatset_insert_m2: brass heat-set insert, M2 internal thread.

On the shelf at the lyceum beside the M3s as of 2026-09-18. Nothing here is measured
yet - the rows exist so the calipers have somewhere to go. Confirm the thread by running
a screw into one rather than trusting the bag, the way the M3 was confirmed: these are
sold in assortments and the markings are not reliable.

Wanted by grow-lab's canopy sensor case, which is choosing between these and the M3s for
its plate closure. That case's corner bosses are already Ø7, and the choice turns entirely
on OD:

    M3 at 5.461  ->  0.77 mm of wall, ratio 1.28, boss must grow to Ø8.2
    M2 at 3.6    ->  1.70 mm of wall, ratio 1.94, boss unchanged
    M2 at 3.2    ->  1.90 mm of wall, ratio 2.19, boss unchanged

So the M2 very likely wins there on geometry alone, with no change to a case whose
envelope is already settled. "Very likely" is not a measurement, which is why this file
is empty.

LENGTH matters as much as OD. The boss is bored deeper than the insert is long, and in
that case an insert standing proud lands on the one face that has to seat flat against
the base plate - which is the objection that got inserts removed from that design in the
first place.

Same interference note as the M3, and it bites harder at this size: the bore wants
0.30-0.50 mm of DIAMETRAL interference against OD, measured on the hole as it comes off
the machine rather than as modelled. On a printed boss the hole comes out under nominal,
so sizing against the modelled diameter hands the insert more interference than intended
- and there is less wall here to absorb it than on a machined part.
"""
UNIT = "mm"
OD = None  # CALIPER needed
LENGTH = None  # CALIPER needed
