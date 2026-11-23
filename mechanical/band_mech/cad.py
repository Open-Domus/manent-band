"""Solid model of the pod for STEP export and a visual check. Run as a module."""
from build123d import Axis, Box, Compound, Pos, export_step, fillet

from . import stack as S
from .checks import envelope_report
from .params import ENVELOPES


def _box(x, y, z, w, h, t, label):
    """Box with its low corner at (x, y, z), pod coordinates: origin at a back corner of the pod."""
    b = Pos(x + w / 2, y + h / 2, z + t / 2) * Box(w, h, t)
    b.label = label
    return b


def build(key: str) -> Compound:
    p, rep, parts = ENVELOPES[key], envelope_report(key), S.load_parts()
    outer = Pos(p.length / 2, p.width / 2, p.height / 2) * Box(p.length, p.width, p.height)
    outer = fillet(outer.edges().filter_by(Axis.Z), p.corner_r)
    shell = outer - _box(p.wall, p.wall, p.back, *p.cavity, "cavity")
    shell.label = "shell"
    solids = [shell]
    off = p.wall + p.board_gap
    board_z = p.back + rep["cell"]["board_to_back_wall"]
    cl, cw, ct = rep["cell"]["size"]
    solids.append(_box(off + S.end_zone(parts) + S.CELL_GAP, (p.width - cw) / 2, p.back + S.CELL_PAD, cl, cw, ct,
                       f"cell {rep['cell']['mpn']}"))
    solids.append(_box(off, off, board_z, *p.board, p.board_t, "board"))
    for pl in rep["placed"]:
        if pl["part"] is None:
            continue
        h = parts["parts"][pl["part"]]["size"][2]
        if pl["face"] == "top":
            z = board_z + p.board_t
        else:
            h = min(h, board_z - p.back)
            z = board_z - h
        solids.append(_box(off + pl["x"], off + pl["y"], z, pl["w"], pl["h"], h, pl["name"]))
    return Compound(label=f"manent-band-{key}", children=solids)


if __name__ == "__main__":
    out = S.ROOT / "mechanical" / "out"
    for key in ENVELOPES:
        model = build(key)
        export_step(model, str(out / f"band-{key}.step"))
        print(f"band-{key}.step: {len(model.children)} bodies, "
              f"bounding box {tuple(round(v, 2) for v in model.bounding_box().size)}")
