"""What is inside the pod and where: the layers from back to front and the plan of the board.

From the wrist outwards: back wall, cell, board, the parts on the board's outer face, front
wall. The microphones are bottom-port parts, so they hang from the inner face of the board
with their hole through it; the cell therefore stops short of both ends of the board, and
the two end zones also carry the spring contacts to the pads on the back.
"""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

from .params import PodParams

ROOT = Path(__file__).resolve().parents[2]

SWELL = 0.08          # cell thickness growth over its life
CELL_PAD = 0.10       # adhesive under the cell
CELL_GAP = 0.20       # around the cell, each side
CELL_TABS = 1.5       # beyond the cell body, for its tabs
BOARD_CLEAR = 0.30    # between the swollen cell and the board (solder joints, tolerance)
TOP_GAP = 0.20        # between the tallest part and the front wall
MIC_EDGE = 0.25       # microphone to the board edge
MIC_CELL_GAP = 0.30   # microphone to the cell
PART_SPACING = 0.15   # between the land patterns of small parts
FINE_PITCH_MARGIN = 0.30
PACKING = 0.50        # share of the free board area that small parts may take; the rest is for tracks
TEST_PAD = 1.0
MIN_MIC_DISTANCE = 20.0
SMALL = {"passive0201", "passive0402", "nfet", "testpad"}


@lru_cache
def load_parts() -> dict:
    return yaml.safe_load((ROOT / "parts" / "parts.yaml").read_text())


def body_of(c) -> str | None:
    """Key in parts.yaml of the body a circuit component occupies; None if it occupies none."""
    name, value, pkg = c.sym.name, c.value, c.fields.get("Package", "")
    if c.sym.virtual or name == "CELL":
        return None
    by_value = {"nRF54L15": "soc", "nPM1304": "pmic", "W25Q512NW": "flash", "T5838": "mic", "S-82A1A": "protector"}
    by_symbol = {"SW": "button", "LED": "led", "ANTENNA": "antenna", "NMOS": "nfet", "CONTACT": "contact",
                 "PAD": "testpad"}
    if value in by_value:
        return by_value[value]
    if name in by_symbol:
        return by_symbol[name]
    if name == "XTAL":
        return "xtal32m" if value.startswith("32MHz") else "xtal32k"
    if pkg == "0603":
        return "inductor"
    return "passive0402" if pkg == "0402" else "passive0201"


@dataclass(frozen=True)
class Placed:
    name: str
    part: str | None      # key in parts.yaml; None for a keep-out
    face: str             # "top" (outer face), "bottom" (towards the cell) or "both"
    x: float              # rectangle on the board, origin at one corner
    y: float
    w: float
    h: float

    @property
    def area(self) -> float:
        return self.w * self.h

    def overlaps(self, o: "Placed") -> bool:
        if "both" not in (self.face, o.face) and self.face != o.face:
            return False
        return self.x < o.x + o.w and o.x < self.x + self.w and self.y < o.y + o.h and o.y < self.y + self.h


def on_board(pl: Placed, p: PodParams) -> bool:
    """Inside the board outline, rounded corners included."""
    L, W = p.board
    r = p.board_corner_r
    for x, y in ((pl.x, pl.y), (pl.x + pl.w, pl.y), (pl.x, pl.y + pl.h), (pl.x + pl.w, pl.y + pl.h)):
        if not (-1e-9 <= x <= L + 1e-9 and -1e-9 <= y <= W + 1e-9):
            return False
        dx, dy = max(r - x, x - (L - r), 0.0), max(r - y, y - (W - r), 0.0)
        if dx > 0 and dy > 0 and dx * dx + dy * dy > r * r:
            return False
    return True


def end_zone(parts) -> float:
    """Length at each end of the board that the cell must leave to a microphone."""
    return MIC_EDGE + parts["parts"]["mic"]["size"][0] + MIC_CELL_GAP


def layout(p: PodParams, parts=None) -> list[Placed]:
    """Every large part and keep-out on the board. Positions are a first arrangement, not a routed board."""
    parts = parts or load_parts()
    L, W = p.board
    e = end_zone(parts)
    out = []

    def part(name, key, face, cx, cy, margin=0.0, turn=False):
        w, h = parts["parts"][key]["size"][:2]
        if turn:
            w, h = h, w
        out.append(Placed(name, key, face, cx - w / 2 - margin, cy - h / 2 - margin, w + 2 * margin, h + 2 * margin))

    def keep(name, face, x, y, w, h):
        out.append(Placed(name, None, face, x, y, w, h))

    mic_x = MIC_EDGE + parts["parts"]["mic"]["size"][0] / 2
    mic_b_y = 1.0 + parts["parts"]["mic"]["size"][1] / 2
    # one end: antenna in the corner, microphone A in the middle
    keep("antenna keep-out", "both", 0.0, 0.0, e, 6.0)
    part("antenna", "antenna", "top", e / 2, 0.9)
    part("microphone A", "mic", "bottom", mic_x, W / 2)
    keep("microphone A gasket", "top", mic_x - 1.5, W / 2 - 1.5, 3.0, 3.0)
    # the other end: microphone B in a corner, four spring contacts in a row, the light above them
    part("microphone B", "mic", "bottom", L - mic_x, mic_b_y)
    keep("microphone B gasket", "top", L - mic_x - 1.5, mic_b_y - 1.5, 3.0, 3.0)
    for i, name in enumerate(("charge +", "charge -", "SWDIO", "SWDCLK")):
        part(f"contact {name}", "contact", "bottom", L - e / 2, 6.0 + 2.5 * i)
    part("light", "led", "top", L - e / 2, W - 1.5)
    # between the ends, on the outer face
    part("button", "button", "top", L / 2, W / 2)
    keep("button cap", "top", L / 2 - 2.5, W / 2 - 2.5, 5.0, 5.0)
    part("microcontroller", "soc", "top", e + 3.5, 3.0, margin=FINE_PITCH_MARGIN)
    part("32 MHz crystal", "xtal32m", "top", e + 3.5, 6.0)
    part("32.768 kHz crystal", "xtal32k", "top", e + 7.5, 3.0)
    part("flash", "flash", "top", e + 5.0, W - 3.5)
    part("power chip", "pmic", "top", L - e - 4.0, 3.5, margin=FINE_PITCH_MARGIN)
    part("buck inductor", "inductor", "top", L - e - 4.0, 6.5)
    part("cell protection", "protector", "top", L - e - 3.0, W - 2.5)
    keep("cell tab slot", "both", L - e - 1.6, W / 2 - 2.0, 1.2, 4.0)
    return out


def small_area(bodies: list[str], parts=None) -> float:
    """Board area the small parts need, each with its share of spacing."""
    parts = parts or load_parts()
    total = 0.0
    for b in bodies:
        w, h = (TEST_PAD, TEST_PAD) if b == "testpad" else parts["parts"][b]["size"][:2]
        total += (w + PART_SPACING) * (h + PART_SPACING)
    return total
