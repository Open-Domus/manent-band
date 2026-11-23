"""SVG drawings for the design document: the board seen from outside and a section along the pod."""
from . import stack as S
from .checks import envelope_report
from .params import ENVELOPES

INK, SHELL, BOARD, PART, UNDER, CELL, KEEP = "#222", "#d9d4c8", "#3d7a4f", "#33475b", "#8fa3b5", "#c2603c", "#e8c66a"


def _svg(body, w, h, scale=22):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-1 -1 {w + 2:.2f} {h + 2:.2f}" '
            f'width="{(w + 2) * scale:.0f}" font-family="sans-serif">\n'
            f'<rect x="-1" y="-1" width="{w + 2:.2f}" height="{h + 2:.2f}" fill="#fff"/>\n{body}</svg>\n')


def _rect(x, y, w, h, fill, dash=False, rx=0.0, opacity=1.0):
    d = ' stroke-dasharray="0.3 0.2"' if dash else ""
    return (f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{rx}" fill="{fill}" '
            f'fill-opacity="{opacity}" stroke="{INK}" stroke-width="0.05"{d}/>\n')


def _text(x, y, s, size=0.7):
    return f'<text x="{x:.2f}" y="{y:.2f}" font-size="{size}" fill="{INK}">{s}</text>\n'


def plan(key: str) -> str:
    """Seen from outside the wrist. Solid: outer face of the board. Dashed: what hangs under it."""
    p, rep = ENVELOPES[key], envelope_report(key)
    off = p.wall + p.board_gap
    L, W = p.board
    body = _rect(0, 0, p.length, p.width, SHELL, rx=p.corner_r) + _rect(off, off, L, W, BOARD, rx=p.board_corner_r, opacity=0.35)
    if rep["cell"]:
        cl, cw, _ = rep["cell"]["size"]
        x0 = off + S.end_zone(S.load_parts()) + S.CELL_GAP
        body += _rect(x0, (p.width - cw) / 2, cl, cw, CELL, dash=True, opacity=0.25)
        body += _text(x0 + 0.4, p.width / 2 + cw / 2 - 0.5, f"cell {rep['cell']['mpn']} (under the board)", 0.6)
    for pl in rep["placed"]:
        fill = KEEP if pl["part"] is None else (UNDER if pl["face"] == "bottom" else PART)
        body += _rect(off + pl["x"], off + pl["y"], pl["w"], pl["h"], fill, dash=pl["face"] == "bottom",
                      opacity=0.45 if pl["part"] is None else 0.9)
    for pl in rep["placed"]:
        if pl["part"] in ("soc", "pmic", "flash", "mic", "button", "led", "antenna"):
            body += _text(off + pl["x"], off + pl["y"] - 0.15, pl["name"], 0.55)
    return _svg(body, p.length, p.width)


def section(key: str) -> str:
    """Cut along the pod. The wrist is at the bottom."""
    p, rep, parts = ENVELOPES[key], envelope_report(key), S.load_parts()
    off, H = p.wall + p.board_gap, p.height
    up = lambda z, h: H - z - h                      # SVG y of a layer that starts z above the wrist
    body = _rect(0, 0, p.length, H, SHELL, rx=1.5)
    body += _rect(p.wall, p.front, p.cavity[0], p.cavity[2], "#fff")
    board_z = p.back + rep["cell"]["board_to_back_wall"] if rep["cell"] else H - p.front - 2.0
    if rep["cell"]:
        cl, _, ct = rep["cell"]["size"]
        x0 = off + S.end_zone(parts) + S.CELL_GAP
        body += _rect(x0, up(p.back + S.CELL_PAD, ct), cl, ct, CELL, opacity=0.6)
        body += _text(x0 + 0.4, up(p.back + S.CELL_PAD, ct) + ct / 2 + 0.25, f"cell, {rep['cell']['capacity_mah']} mAh")
    body += _rect(off, up(board_z, p.board_t), p.board[0], p.board_t, BOARD)
    for pl in rep["placed"]:
        if pl["part"] is None:
            continue
        h = parts["parts"][pl["part"]]["size"][2]
        if pl["face"] == "top":
            body += _rect(off + pl["x"], up(board_z + p.board_t, h), pl["w"], h, PART)
        else:
            h = min(h, board_z - p.back)
            body += _rect(off + pl["x"], up(board_z - h, h), pl["w"], h, UNDER)
    return _svg(body, p.length, H)


if __name__ == "__main__":
    out = S.ROOT / "mechanical" / "out"
    out.mkdir(exist_ok=True)
    for key in ENVELOPES:
        (out / f"plan-{key}.svg").write_text(plan(key))
        (out / f"section-{key}.svg").write_text(section(key))
    print(f"drawings written to {out}")
