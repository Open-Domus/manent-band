"""Does it fit? Run as a module to write mechanical/out/fit-report.json."""
import json
import math

from . import stack as S
from .params import ADOPTED, ENVELOPES, PodParams

PLASTIC, FR4 = 1.2, 1.85          # g/cm3
CELL_G_PER_MAH = 0.023            # estimate
ELECTRONICS_G = 0.5               # parts and solder, estimate


def circuit_bodies() -> list[str]:
    from electrical.gen.design import build
    return [b for b in map(S.body_of, build()) if b]


def top_height(parts, placed) -> float:
    tall = [parts["parts"][pl.part]["size"][2] for pl in placed if pl.part and pl.face == "top"]
    return max(tall + [parts["parts"]["passive0402"]["size"][2]])


def cell_room(p: PodParams, parts) -> dict:
    """The box left for the cell: under the board, between the two end zones."""
    L, _ = p.board
    placed = S.layout(p, parts)
    return {
        "length": round(L - 2 * S.end_zone(parts) - S.CELL_TABS - 2 * S.CELL_GAP, 2),
        "width": round(p.cavity[1] - 2 * S.CELL_GAP, 2),
        "thickness": round((p.cavity[2] - S.CELL_PAD - S.BOARD_CLEAR - p.board_t - top_height(parts, placed) - S.TOP_GAP)
                           / (1 + S.SWELL), 2),
    }


def best_cell(p: PodParams, parts) -> str | None:
    room = cell_room(p, parts)
    fits = [k for k, c in parts["cells"].items()
            if c["size"][0] <= room["length"] and c["size"][1] <= room["width"] and c["size"][2] <= room["thickness"]]
    return max(fits, key=lambda k: parts["cells"][k]["capacity_mah"]) if fits else None


def envelope_report(key: str, p: PodParams | None = None) -> dict:
    p = p or ENVELOPES[key]
    parts = S.load_parts()
    placed = S.layout(p, parts)
    L, W = p.board
    problems = []

    for i, a in enumerate(placed):
        if a.part and not S.on_board(a, p):
            problems.append(f"{a.name} is off the board")
        # A part may sit inside its own keep-out (antenna, button); two parts may not overlap.
        problems += [f"{a.name} overlaps {b.name}" for b in placed[i + 1:]
                     if a.overlaps(b) and a.part and b.part]
    keepouts = [k for k in placed if k.part is None]
    owners = {"antenna keep-out": {"antenna"}, "button cap": {"button"}}
    for k in keepouts:
        problems += [f"{a.name} is inside {k.name}" for a in placed
                     if a.part and a.overlaps(k) and a.name not in owners.get(k.name, set())]

    bodies = circuit_bodies()
    large = sorted(b for b in bodies if b not in S.SMALL)
    if large != sorted(pl.part for pl in placed if pl.part):
        problems.append("the placed parts are not the large parts of the circuit")
    small = [b for b in bodies if b in S.SMALL]
    taken = sum(pl.area for pl in placed if pl.face in ("top", "both") and not
                (pl.part and any(pl.overlaps(k) for k in keepouts)))
    free = L * W - taken
    need = S.small_area(small, parts)
    if need > S.PACKING * free:
        problems.append("not enough free board area for the small parts")

    ck = best_cell(p, parts)
    room = cell_room(p, parts)
    cell = None
    if ck is None:
        problems.append("no cell in the list fits")
    else:
        c = parts["cells"][ck]
        swollen = c["size"][2] * (1 + S.SWELL)
        under_board = S.CELL_PAD + swollen + S.BOARD_CLEAR
        cell = {"key": ck, "mpn": c["mpn"], "size": c["size"], "capacity_mah": c["capacity_mah"],
                "spare_length": round(room["length"] - c["size"][0], 2),
                "spare_width": round(room["width"] - c["size"][1], 2),
                "spare_height": round((room["thickness"] - c["size"][2]) * (1 + S.SWELL), 2),
                "board_to_back_wall": round(under_board, 2)}
        if parts["parts"]["mic"]["size"][2] + 0.2 > under_board:
            problems.append("the microphones do not fit under the board")

    mics = [pl for pl in placed if pl.part == "mic"]
    distance = math.dist(*[(m.x + m.w / 2, m.y + m.h / 2) for m in mics])
    if distance < S.MIN_MIC_DISTANCE:
        problems.append("the microphones are too close together")

    cl, cw, ch = p.cavity
    shell_g = (p.length * p.width * p.height - cl * cw * ch) / 1000 * PLASTIC
    board_g = L * W * p.board_t / 1000 * FR4 + ELECTRONICS_G
    cell_g = cell["capacity_mah"] * CELL_G_PER_MAH if cell else 0.0
    return {
        "envelope": p.name, "pod": [p.length, p.width, p.height], "board": [round(L, 2), round(W, 2), p.board_t],
        "ok": not problems, "problems": problems,
        "stack": {"back wall": p.back, "adhesive": S.CELL_PAD,
                  "cell, swollen": round(cell["size"][2] * (1 + S.SWELL), 2) if cell else None,
                  "gap under the board": S.BOARD_CLEAR, "board": p.board_t,
                  "tallest part on the outer face": top_height(parts, placed),
                  "gap under the front wall": S.TOP_GAP, "front wall": p.front,
                  "left over": cell["spare_height"] if cell else None},
        "cell_room": room, "cell": cell,
        "area": {"board": round(L * W, 1), "large_parts_and_keepouts": round(taken, 1), "free": round(free, 1),
                 "small_parts": len(small), "small_parts_need": round(need, 1),
                 "share_of_free": round(need / free, 2)},
        "mic_distance": round(distance, 1),
        "mass": {"shell_g": round(shell_g, 2), "board_g": round(board_g, 2), "cell_g": round(cell_g, 2),
                 "total_g_estimate": round(shell_g + board_g + cell_g, 1)},
        "placed": [{"name": pl.name, "part": pl.part, "face": pl.face, "x": round(pl.x, 2), "y": round(pl.y, 2),
                    "w": round(pl.w, 2), "h": round(pl.h, 2)} for pl in placed],
    }


def size_sweep() -> list[dict]:
    """What each millimetre of pod buys in cell capacity."""
    parts = S.load_parts()
    rows = []
    for width in (19.0, 20.0, 22.0):
        for height in (8.5, 9.0, 10.0):
            p = ENVELOPES["A"].resized(width=width, height=height)
            ck = best_cell(p, parts)
            rows.append({"pod": [p.length, width, height], "room": cell_room(p, parts), "best_cell": ck,
                         "capacity_mah": parts["cells"][ck]["capacity_mah"] if ck else None})
    return rows


def full_report() -> dict:
    return {"adopted": ADOPTED, "envelopes": {k: envelope_report(k) for k in ENVELOPES}, "size_sweep": size_sweep()}


if __name__ == "__main__":
    rep = full_report()
    out = S.ROOT / "mechanical" / "out"
    out.mkdir(exist_ok=True)
    (out / "fit-report.json").write_text(json.dumps(rep, indent=1) + "\n")
    for key, e in rep["envelopes"].items():
        c = e["cell"]
        print(f"{e['envelope']}: {'fits' if e['ok'] else 'DOES NOT FIT: ' + '; '.join(e['problems'])}"
              + (f"; cell {c['mpn']} {c['capacity_mah']} mAh, {c['spare_height']} of height left" if c else ""))
    raise SystemExit(0 if rep["envelopes"][ADOPTED]["ok"] else 1)
