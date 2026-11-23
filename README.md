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
| Fit model, drawings, STEP | `mechanical/`, `mechanical/out/` |

## Build

Needs `uv`, and either KiCad 10 or Docker (`docker pull kicad/kicad:10.0`).

```
make all        # schematic, checks, tests, fit report, drawings, budgets, STEP
make test       # tests only
```

The schematic is generated: edit `electrical/gen/design.py`, never the `.kicad_sch` files.
Every pin carries a label with its net name instead of drawn wires. `make schematic` runs
KiCad's rule check and compares the netlist KiCad reads with the one in `design.py`.

There is no board yet: no footprints, no placement file, no routing. The fit model places
the large parts and counts the small ones by area.

## Licences

As for the ring: hardware under CERN-OHL-S v2 (`LICENSE`), documents under CC BY-SA 4.0
(`LICENSE-docs`). The licence of the scripts is not decided.
