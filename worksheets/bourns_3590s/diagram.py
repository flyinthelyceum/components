"""Measurement worksheet for the Bourns 3590S ten-turn pot and its turns-counting dial (the small ~25 mm one, H-22 family; confirm the model number stamped underneath).

Renders diagram.png (every dimension lettered) and sheet.csv (one row per letter:
part, constant, what to measure, how, datasheet nominal for a sanity check, a
blank `measured` column). Fill `measured`, then `python worksheets/apply.py
worksheets/bourns_3590s/sheet.csv --by JR` runs `components measure` per row.

Nominals marked DATASHEET come from bourns.com/pdfs/3590.pdf (3590S, -2 metal
bushing). Dial nominals are None until the model is confirmed; measure them.
"""
from __future__ import annotations
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

HERE = Path(__file__).parent
ROWS = [
    # letter, part, const, what, how, nominal_mm
    ("A", "bourns_3590s", "BODY_DIA",        "body diameter",                       "outside jaws across the round body",              22.22),
    ("B", "bourns_3590s", "BODY_LEN",        "body length, rear face to bushing shoulder", "outside jaws, terminals excluded",         18.59),
    ("C", "bourns_3590s", "BUSHING_DIA",     "bushing thread major diameter",       "outside jaws on the 3/8-32 thread",               9.525),
    ("D", "bourns_3590s", "BUSHING_LEN",     "bushing length, shoulder to end",     "depth rod from shoulder",                          7.94),
    ("E", "bourns_3590s", "SHAFT_DIA",       "shaft diameter",                      "outside jaws, away from the flat if any",          6.34),
    ("F", "bourns_3590s", "SHAFT_LEN",       "shaft length beyond bushing end",     "depth rod, bushing end to shaft tip",              None),
    ("G", "bourns_3590s", "TERMINAL_REACH",  "solder lugs, rear face to lug tip",   "outside jaws, one lug",                            None),
    ("H", "bourns_3590s", "NUT_AF",          "hex nut across flats",                "outside jaws, flat to flat",                       None),
    ("I", "bourns_3590s", "NUT_THICK",       "hex nut thickness",                   "outside jaws",                                     None),
    ("J", "bourns_3590s", "WASHER_OD",       "lock washer outside diameter",        "outside jaws, tab to tab if the tabs are widest",  None),
    ("K", "bourns_3590s", "WASHER_THICK",    "lock washer thickness",               "outside jaws, on the ring not a tab",              None),
    ("L", "bourns_3590s", "AR_PIN_OFFSET",   "anti-rotation pin, centre to shaft centre; 0 if none", "outside jaws pin edge to bushing edge, then add radii", None),
    ("M", "bourns_turns_dial", "DIAL_OD",      "dial skirt outside diameter",         "outside jaws across the grey skirt",               None),
    ("N", "bourns_turns_dial", "DIAL_HEIGHT",  "overall height, panel face to knob top", "outside jaws, dial standing on a flat",         None),
    ("O", "bourns_turns_dial", "KNOB_DIA",     "black knob diameter",                 "outside jaws",                                     None),
    ("P", "bourns_turns_dial", "BORE",         "shaft bore",                          "inside jaws, or trust E and note it",              6.35),
    ("Q", "bourns_turns_dial", "LEVER_REACH",  "lock lever, skirt edge to lever tip", "outside jaws, lever closed",                       None),
    ("R", "bourns_turns_dial", "REAR_RECESS_DIA", "rear counterbore that clears the nut", "inside jaws from the back",                    None),
    ("S", "bourns_turns_dial", "REAR_RECESS_DEPTH", "rear counterbore depth",         "depth rod from the skirt face",                    None),
]

def draw():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7.5))
    for ax in (ax1, ax2):
        ax.set_aspect("equal"); ax.axis("off")
    lw = 1.6; ec = "#111"; fc = "#e9e6df"; dc = "#b0122b"
    def dim(ax, x0, y0, x1, y1, letter, off=(0, 0)):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="<->", lw=1.1, color=dc))
        ax.text((x0 + x1) / 2 + off[0], (y0 + y1) / 2 + off[1], letter, color=dc, fontsize=13, fontweight="bold",
                ha="center", va="center", bbox=dict(boxstyle="circle,pad=0.25", fc="white", ec=dc, lw=1))
    # --- panel 1: pot, side elevation, shaft pointing right ---------------------
    ax = ax1
    ax.set_title("Bourns 3590S, side elevation (shaft to the right)", fontsize=12, loc="left")
    body = Rectangle((0, 0), 18.6, 22.2, fc=fc, ec=ec, lw=lw); ax.add_patch(body)
    bush = Rectangle((18.6, 11.1 - 4.76), 7.9, 9.5, fc="#cfcac0", ec=ec, lw=lw); ax.add_patch(bush)
    shaft = Rectangle((26.5, 11.1 - 3.17), 20, 6.34, fc="#d9d9d9", ec=ec, lw=lw); ax.add_patch(shaft)
    for y in (4, 11.1, 18.2):
        ax.add_patch(Rectangle((-5, y - 0.6), 5, 1.2, fc="#c9a227", ec=ec, lw=1))
    ax.add_patch(Rectangle((18.6, 11.1 + 4.76), 1.2, 3.0, fc="#999", ec=ec, lw=1))  # AR pin
    ax.add_patch(Rectangle((28.5, 11.1 - 6.2), 2.4, 12.4, fc="#c9a227", ec=ec, lw=lw))  # nut
    ax.add_patch(Rectangle((31.2, 11.1 - 7.0), 0.8, 14.0, fc="#c9a227", ec=ec, lw=1))   # washer
    dim(ax, -8, 0, -8, 22.2, "A", off=(-2.2, 0))
    dim(ax, 0, -4, 18.6, -4, "B", off=(0, -2.2))
    dim(ax, 22.5, 11.1 - 4.76, 22.5, 11.1 + 4.76, "C", off=(0, 7.5))
    dim(ax, 18.6, 27, 26.5, 27, "D", off=(0, 2.2))
    dim(ax, 38, 11.1 - 3.17, 38, 11.1 + 3.17, "E", off=(-3.2, 0))
    dim(ax, 26.5, -4, 46.5, -4, "F", off=(0, -2.2))
    dim(ax, -5, 25, 0, 25, "G", off=(0, 2.2))
    dim(ax, 28.5, 22.5, 30.9, 22.5, "I", off=(-3.2, 2.4))
    dim(ax, 31.2, 25.5, 32.0, 25.5, "K", off=(4.0, 0))
    dim(ax, 44, 11.1 - 6.2, 44, 11.1 + 6.2, "H", off=(3.2, -4))
    dim(ax, 48.5, 11.1 - 7.0, 48.5, 11.1 + 7.0, "J", off=(3.2, 4))
    dim(ax, 19.2, 11.1, 19.2, 11.1 + 4.76 + 1.5, "L", off=(-3.5, 1.5))
    ax.text(0, -14, "H, I, J, K: measure the nut and washer off the pot. L: 0 if there is no pin.", fontsize=9, color="#444")
    ax.set_xlim(-14, 55); ax.set_ylim(-16, 31)
    # --- panel 2: dial, side elevation + face ---------------------------------
    ax = ax2
    ax.set_title("Bourns turns-counting dial, side elevation (panel at bottom) and face.\nRecord the model number from the underside.", fontsize=11, loc="left")
    skirt = Rectangle((0, 0), 26, 6, fc="#8c98a4", ec=ec, lw=lw); ax.add_patch(skirt)
    knob = Rectangle((5, 6), 16, 12, fc="#222", ec=ec, lw=lw); ax.add_patch(knob)
    ax.add_patch(Rectangle((9, -3.5), 8, 3.5, fc="white", ec=ec, lw=1, ls="--"))  # rear recess
    ax.add_patch(Rectangle((26, 1.5), 4, 2.5, fc="#333", ec=ec, lw=1))          # lever
    dim(ax, 0, -7, 26, -7, "M", off=(0, -2.2))
    dim(ax, -4, 0, -4, 18, "N", off=(-2.2, 0))
    dim(ax, 5, 21, 21, 21, "O", off=(0, 2.2))
    dim(ax, 26, -1.5, 30, -1.5, "Q", off=(3.5, -1.5))
    dim(ax, 9, -5.5, 17, -5.5, "R", off=(0, 1.8))
    dim(ax, 19, -3.5, 19, 0, "S", off=(3, 0))
    face = Circle((44, 9), 13, fc="#8c98a4", ec=ec, lw=lw); ax.add_patch(face)
    ax.add_patch(Circle((44, 9), 8, fc="#222", ec=ec, lw=lw))
    ax.add_patch(Circle((44, 9), 3.2, fc="white", ec=ec, lw=1, ls="--"))
    dim(ax, 40.8, 9, 47.2, 9, "P", off=(0, -3.2))
    ax.text(0, -12, "P: the bore; if the inside jaws will not reach, record E and say so in the comment.", fontsize=9, color="#444")
    ax.set_xlim(-8, 60); ax.set_ylim(-14, 26)
    fig.suptitle("components worksheet: bourns_3590s + bourns_turns_dial   (mm, calipers; fill sheet.csv)", fontsize=13, y=0.98)
    fig.tight_layout()
    fig.savefig(HERE / "diagram.png", dpi=160)

def sheet():
    with open(HERE / "sheet.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["letter", "part", "const", "what", "how", "datasheet_nominal_mm", "measured_mm", "note"])
        for r in ROWS:
            w.writerow([*r, "", ""])

if __name__ == "__main__":
    draw(); sheet(); print("wrote", HERE / "diagram.png", "and", HERE / "sheet.csv")
