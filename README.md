# Manent band: hardware

Hardware design of the Manent band: a small pod on a strap or a clip that listens for
speech around its wearer, records it, and hands it to the phone over Bluetooth LE. It is
the always-listening sibling of the ring in `manent-ring`, in the form of Amazon's Bee.
Firmware and radio protocol live in the `mnemo-band` repository.

Nothing here has been built or measured. This is a first design on paper, checked by
scripts, and several of its choices still wait for the project owner.

| What | Where |
| --- | --- |
| Design document: requirements, architecture, decisions | [docs/design.md](docs/design.md) |
| Does it fit? Pod, layers, cell, board area | [docs/space-budget.md](docs/space-budget.md) |
| How long does it last? | [docs/power-budget.md](docs/power-budget.md) |
| What is undecided or unknown, and what would settle it | [docs/open-questions.md](docs/open-questions.md) |
| Parts with sizes and how far each is verified | [parts/parts.yaml](parts/parts.yaml) |
| Circuit, as data | [electrical/gen/design.py](electrical/gen/design.py) |
| Schematic (KiCad 10), PDF, bill of materials | `electrical/kicad/`, `electrical/out/` |
| Board: placed and routed by scripts, not reviewed | `electrical/kicad/band.kicad_pcb`, `electrical/out/board-*.svg` |
| Fit model, drawings, STEP | `mechanical/`, `mechanical/out/` |

## Build

Needs `uv`, and either KiCad 10 or Docker (`docker pull kicad/kicad:10.0`).

```
make all        # schematic, board, checks, tests, fit report, drawings, budgets, STEP
make test       # tests only
make route      # draw the tracks again with Freerouting (needs Java and its jar; see tools/route.sh)
```

The schematic and the board are generated: edit `electrical/gen/design.py` and the fit
model, never the `.kicad_sch` or `.kicad_pcb` files.
Every pin carries a label with its net name instead of drawn wires. `make schematic` runs
KiCad's rule check and compares the netlist KiCad reads with the one in `design.py`.

The board is placed and routed by scripts and passes KiCad's checks, but nobody has reviewed
it: see "Board" in the design document before taking it for more than it is. The tracks
are kept in `electrical/kicad/band.ses`; when the placement changes, `make route` draws
them again.

## Licences

As for the ring: hardware under CERN-OHL-S v2 (`LICENSE`), documents under CC BY-SA 4.0
(`LICENSE-docs`). The licence of the scripts is not decided.
