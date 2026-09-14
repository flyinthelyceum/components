# components

Measured physical dimensions of the parts the Innovation Commons builds with.
One writer, provenance on every number.

When you design an enclosure around a sensor board, an LED ring or a panel
meter, you need its real dimensions. The vendor's listing is often wrong (a
ring listed at 6.7 mm thick measured 2.84), two boards sold under one name
differ, and a number copied from one project to the next loses the record of
who measured it and when. This repo is where those numbers live, so every
project reads the same measurement and nobody restates it.

## Reading a constant

One module per part, in `components/`. Open `components/ws2812_ring12.py`:

```python
UNIT = "mm"
OUTER_DIA = 37.06  # CALIPER 2026-09-14 JR
INNER_DIA = 25.25  # CALIPER 2026-09-14 JR
THICKNESS = 2.84  # CALIPER 2026-09-14 JR
LED_COUNT = 12  # CALIPER 2026-09-14 JR
```

Each line is a name, a value, and a provenance comment. The comment is the
part that matters. It answers "how do we know?", and it is one of exactly two
words:

- `CALIPER YYYY-MM-DD XX`: someone (initials XX) measured the part in hand on
  that date.
- `DATASHEET <url>`: the number was read from the maker's own drawing or table,
  at that link.

A value nobody has measured is `None` with the comment `CALIPER needed`. That
is a to-do, and it is honest: the file says what is unknown instead of
carrying a guess.

`UNIT` is millimetres unless the module says `UNIT = "in"`. A part measured
in inches stays in inches, so the reading in the file is the reading on the
caliper. A converted copy would be a rounded one.

## Why CHOICE and DERIVED never appear here

A design carries three kinds of number. A measurement (the board is 59.54
wide). A choice (leave 4 mm around it). A derivation (so the pocket is 67.54).
Only the first kind belongs in this repo. Choices and derivations belong in
the project that makes them, next to the reasoning, because they change when
the design changes. A measurement changes only when someone measures again.

## Using it in a project

Install the package, pinned to the moving `components-v1` tag:

```
pip install "components @ git+https://github.com/flyinthelyceum/components.git@components-v1"
```

Then import the part and use its constants. Never type the number:

```python
from components import ws2812_ring12 as RING

pocket_dia = RING.OUTER_DIA + 2 * CLEARANCE   # CLEARANCE is your CHOICE
```

Stamp the version into anything you cut or print, so the numbers it came
from can be found again:

```python
import components
print(components.version())   # components-v1.3+a1b2c3d4e5f6
```

`components-v1` moves forward as measurements land. Each measurement also
gets an immutable tag, `components-v1.N`. A cut file, a print, or a cut list
should record the resolved `v1.N` (what `version()` prints), so that "the panel
was cut from v1.7" means one exact set of numbers. The moving name cannot say that.

## Adding a measurement

You need a clone of this repo (`git clone
https://github.com/flyinthelyceum/components.git ~/projects/components`) and
the package installed from it (`pip install -e ~/projects/components`). Then,
with the part on the bench and the caliper in your hand:

```
python -m components measure ws2812_ring12 THICKNESS 2.84 --by JR
```

That edits (or creates) the module, writes the provenance line with today's
date and your initials, commits with a message that says exactly what
changed, tags it `components-v1.N`, moves `components-v1`, and pushes. For a
number read from a drawing, give the link instead of initials:

```
python -m components measure esp32_s3_devkitc1 PCB_L 62.74 --by JR --datasheet https://dl.espressif.com/dl/schematics/esp_idf/DXF_ESP32-S3-DevKitC-1_V1.1_20220429.dxf
```

The command refuses to run if your clone has uncommitted changes or is behind
`origin`, and it tells you what to do. If the push fails it says so and
leaves your commit in place; it never claims a push it did not make.

Do not edit the modules by hand. The command exists so that every number
arrives with its provenance and its own commit.

## The one-writer rule

Measured dimensions are written in exactly one place, this repo, by exactly
one command, `components measure`. Every project that needs a dimension
imports it from here, and a pre-commit lint in those projects refuses a
number typed in beside a caliper or datasheet comment.

## For a consumer repo's maintainer

`scripts/install-hooks.sh` installs the lint as a pre-commit hook (it lints
the index, so only what you are committing is checked). `python -m components
lint <path>` runs it by hand. Put `# lint: not-a-measurement` on the rare line
that mentions a caliper without being a measurement. `python -m components
render-sheet` writes every constant to the `COMPONENTS (generated)` tab of the
bench master sheet. That tab is a generated view; rerun the command instead of
editing it.
