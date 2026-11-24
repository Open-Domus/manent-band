# Manent band: design

Status: first draft on paper, written 2026-11-23. No board, no pod, no measurement.
Numbers are either from manufacturers' documents or estimates, and each table says which.
Choices marked "draft" were made to have something to check; the project owner has not
confirmed them. They are listed again in [open-questions.md](open-questions.md).

## What the band does

It waits for sound. When somebody speaks near the wearer it records, and the words reach
the phone as audio, to be turned into text there. The band keeps a recording only until
the phone confirms it has it. A light shows that it is listening and one button mutes it.

The ring records when its wearer asks; the band records until its wearer says stop. That
is the whole difference, and every change from the ring's design follows from it.

## Requirements

| Requirement | Source |
| --- | --- |
| Listens all the time; records when there is sound | `mnemo-band` |
| At least 2 days between charges; 5 is the stretch goal | `mnemo-band` |
| No audio lost while the phone is away for a working day | `mnemo-band` |
| A light other people can see whenever the microphones have power | `mnemo-band` |
| Mute works on the band alone and cuts the microphones' power | `mnemo-band` |
| 16 kHz mono, Opus at about 16 kbit/s encoded on the band | `mnemo-band` |
| Bluetooth LE; store and forward; one phone; no server of ours | `mnemo-band` |
| Firmware the owner can rebuild and load | as the ring |
| A pod that comes out of its strap and also fits a clip | `mnemo-band`, and what Bee ships |
| Pod 36 x 19 x 9 mm | draft, from the space budget |
| Two microphones, one button in the middle of the outer face | draft, as on Bee |
| Closed pod, charged through two pads on its back; no USB socket | draft |
| No vibration motor | draft: there is no room for one in the slim pod |

## Button

| Gesture | Meaning | Handled by |
| --- | --- | --- |
| Short press | Mark this moment | firmware |
| Hold 2 s | Mute, or listen again | firmware; muting switches the microphone rail off |
| Press while in ship mode (96 ms) | Wake from storage | power chip |
| Hold 10 s | Power cycle: the way out of a hung firmware | power chip |

The first two are the `mnemo-band` gestures. Its third, a factory reset at 10 s, collides
with the power chip's own 10 s reset and needs another home: see the open questions.
Without a motor, the only confirmation of a mute is the light going out.

## Light

One red LED behind a light pipe in the outer face, with two levels:

- **Steady glow**, about 0.05 mA. Its switch is driven by the microphones' supply rail, not
  by firmware: if a microphone has power, the light is on, and there is no code path that
  can listen in the dark.
- **Bright**, about 0.5 mA, added by firmware while sound is actually being recorded.
  Firmware can add this light; it has no pin that can remove the glow.

A light that must be on for days is expensive. At these currents it takes about a quarter
of the typical day's energy. Whether 0.05 mA can be seen by somebody across a table, in
daylight, through a light pipe, is not known; if it takes 0.2 mA the battery life drops by
a third.

## Blocks

```
back pads --springs--TVS-- VBUS --> [ nPM1304 ] <--> cell (+ protection)
                                     |  |  |
                        1.8 V buck --+  |  +-- load switch 2 --> flash supply
                                     |  +----- load switch 1 --> microphone supply --> glow
                                     v
   button -----> SHPHLD          [ nRF54L15 ] --PDM--> microphone A, microphone B
                                    |  |  |
                               SPI --+  |  +-- matching -- tuning -- antenna
                                v       +-- bright light
                          512 Mbit flash
```

One logic rail at 1.8 V, as on the ring: the microphones accept nothing higher.

## Parts

| Block | Part | Size (mm) | Why | Confidence |
| --- | --- | --- | --- | --- |
| Microcontroller | Nordic nRF54L15, QFN48 | 6 x 6 x 0.85 | The firmware targets it; its PDM clock suits the microphone | pin table read once from the product specification |
| Power | Nordic nPM1304, QFN32 | 5 x 5 x 0.85 | Charges at 4 to 100 mA, enough for a 120-170 mAh cell; 1.8 V buck; two load switches; ship mode at 370 nA | pin table read once from the product specification; some terminations not |
| Flash | Winbond W25Q512NW, WSON-8 | 8 x 6 x 0.8 | 512 Mbit holds about 7 h of speech not yet uploaded | from memory: part number, package and height to confirm |
| Microphones | 2 x TDK T5838 | 3.5 x 2.65 x 0.98 | Wake-on-sound at 20-137 uA; already planned by the firmware | verified |
| Button | Panasonic EVP-BB, 1.6 N | 2.6 x 1.6 x 0.53 | Sealed to IP67; pressed through a flexible cap | datasheet from a distributor |
| Light | Rohm SML-P11VT | 1.0 x 0.6 x 0.2 | Already on the ring | verified at 1 mA; dimmer is from curves |
| Cell protection | ABLIC S-82A1A | 1.4 x 1.4 | Fitted only if the cell has none of its own | verified |
| Charging input, service pads | 3 x Infineon ESD230-B1-W0201 | 0.58 x 0.28 | Every pad on the outside of the pod needs ESD protection | verified |
| Cell temperature | 10 k thermistor, B about 3380 K | 0402 | The charger stops outside the cell's temperature range, as on the ring and the card | part not chosen |
| Cell | flat LiPo pouch, 401525 class | 25 x 15 x 4 | See the space budget | trade size code; capacity estimated |

The full list with part numbers is `electrical/out/bom.csv`.

### QFN packages, not the ring's chip-scale ones

The ring has to use 0.3 mm pitch chip-scale packages, with microvias and X-ray inspection.
The pod has about three times the board area, so both Nordic chips are the QFN versions:
0.4 and 0.5 mm pitch with the pins on the edge, which an ordinary four-layer board with
through vias can carry and an ordinary assembler can place. Resistors and capacitors are
0402 where the reference does not ask for 0201.

What this rests on: the two pin tables were read on 2026-11-23 from Nordic's product
specifications as page text, once (`parts/pins`). The clock-capable pins come out the same
as in the ring's table, which was checked ball by ball.

The circuit around both chips is Nordic's: the reference layouts nRF54L15-QFAA 0.8 and
nPM1304-QEAA 1.0 (configuration 2, one buck, a load switch and an LED: this circuit) were
opened as boards with KiCad's Altium importer on 2026-11-24, which gives the net of every
part. Reading them corrected the first draft, which had followed the ring's chip-scale
circuit where the QFN schematic was only a picture:

| What | Draft | Nordic's reference, now on the board |
| --- | --- | --- |
| Reset pin | straight to its test pad | 1 k in series and 3.9 pF to ground at the pin, which sits next to the antenna pin |
| DECA | 2.2 uF and 10 nF | also 2.2 nF |
| End of the matching network | a shunt place left empty | 0.3 pF to ground |
| Ferrite bead | value not given | 120 ohm at 100 MHz, 200 mA: Murata BLM03AG121SN1D, the ring's |
| Unused BUCK2 output (VOUT2) | to ground | to VSYS |
| Cell capacitor | 10 uF | 2.2 uF |
| VSYS | one 10 uF | two: one at the buck's input, one at the output |

The order of the matching parts, DECRF joined to DECA and the place of every other capacitor
were as drafted. The one part kept different on purpose is the converter inductor: the
reference takes a 0603 of 0.65 ohm, this board the ring's 0402 of 1.08 ohm at most.

### Microcontroller pins

| Signal | Pin | Rule it satisfies |
| --- | --- | --- |
| Microphone clock, data | P1.04, P1.05 | PDM lives on port 1; the clock is on a clock pin |
| Microphone A threshold, wake | P1.06, P1.07 | port 1 can wake the chip |
| Microphone B threshold, wake | P1.09, P1.10 | port 1 can wake the chip |
| Microphone power request | P1.13 | to the power chip's GPIO1, which drives load switch 1 |
| Flash clock, out, in, select | P2.01, P2.02, P2.04, P2.05 | the dedicated fast-SPI pins |
| Power chip clock, data, interrupt | P0.03, P0.02, P0.01 | clock on a clock pin; port 0 can wake the chip. The button arrives through this interrupt |
| Bright light | P0.04 | |
| Test serial port | P1.11, P1.12 | test pads on the board; this package has no P1.15 |
| 32.768 kHz crystal | P1.00, P1.01 | fitted |

`electrical/gen/checks.py` enforces these rules on every build.

### Choices worth explaining

- **Two microphones on two wires.** Both share one clock and one data line; a strap pin
  on each picks the clock edge it answers on. In silence only microphone A waits for sound
  and B sleeps at under a microamp. Each has its own threshold and wake pins, so firmware
  can also arm B, or record from whichever is louder. No beamforming: the geometry between
  wrist and mouth changes with every gesture.
- **Both microphones on one switched rail.** Mute opens load switch 1 and both lose power.
  The glow hangs on that rail.
- **A bigger flash, in an ordinary package.** An always-listening band fills its buffer
  while the phone is in another room. One 256-byte slot holds 100 ms of speech, so
  512 Mbit is 262,144 slots, about 7 h 17 min. It sits behind load switch 2: in silence it
  has no power at all.
- **The 32.768 kHz crystal is fitted.** The ring leaves it out to save room. The band keeps
  a link alive for days, where a more accurate clock shortens every listening window.
- **Pads, not a socket.** Two spring contacts reach two pads on the back of the pod, at one
  end. A pod laid in its dock the wrong way round touches nothing, so there is no reverse
  polarity to protect against. Two more pads carry SWDIO and SWDCLK: the pod can be
  reprogrammed closed. Bee's first model has a USB-C socket on its back instead; that
  needs no dock and gives up the seal.
- **Button to the power chip only**, as on the ring: to its ship-mode input, which pulls it
  up towards the cell voltage. The microcontroller learns of a press, and of its release,
  from the power chip's interrupt, and times the 2 s hold from the two. The first draft
  also ran it through a diode to a microcontroller pin; the ring had already dropped that,
  and so has this board. The cost is a few milliseconds per press, to be measured.
- **A thermistor against the cell.** A 120 mAh pouch charged in a closed pod on a wrist:
  the charger stops when the cell is too warm or too cold. The first draft disabled the
  input instead.
- **The microphone rail is emptied when it is switched off.** 470 k to ground, as on the
  ring: when a mute opens the load switch, the rail falls in a fraction of a second and the
  glow goes out with it, instead of fading or staying half on. It costs about 4 uA while
  listening.
- **Every outside pad is protected.** The charging pad and the two service pads touch skin
  and fingers: each has a 5.5 V protection diode, as on the card.

## Pod and assembly

- A plastic box 36 x 19 x 9 mm with 3 mm corners, in two shells, with no lugs: it pushes
  into a pocket in a silicone strap or into a clip. Material and how the shells are joined
  are open.
- From the wrist outwards: back shell, cell, board, parts, front shell. The board is
  33.4 x 16.4 mm, 0.6 thick, with every part on its outer face except the microphones, the
  spring contacts and the pads for the cell tabs.
- The microphones hang under the board, one at each end, each with a hole through the
  board, a gasket between board and front shell, and a hole in the shell behind a membrane.
- The cell lies between the two microphones. That limits it to 25 mm in a 36 mm pod.
- Openings in the front shell: two microphone holes, a light pipe, and a thinned or
  two-material zone over the button. In the back shell: four contact pads.
- The antenna takes one corner of the board, at the end away from the contacts, with no
  copper under it.

Whether it all fits is in [space-budget.md](space-budget.md). In short: the 36 x 19 x 9 pod
holds a cell of about 120 mAh with 0.6 mm of height to spare; the 38 x 22 x 10 pod that
`mnemo-band` asks for holds about 170 mAh. The slim one is adopted, as a draft, because on
paper it already reaches the five days.

## Board

`electrical/kicad/band.kicad_pcb`: four copper layers, 33.4 x 16.4 mm with rounded corners,
seen from outside the wrist. Top copper faces outwards, bottom copper faces the cell, the
first inner layer is a ground plane. There is no ground under the antenna corner on any
layer.

What is done:

- Every part of the schematic has a footprint and a place. The parts the pod decides
  (chips, microphones, button, light, antenna, contacts, test pads) are where the fit
  model puts them. The rest are placed by a script, each as near as it can get to the pads
  it connects to: first the radio, crystal and converter parts, then the small decoupling
  capacitors, then everything else. It keeps 0.35 mm between land patterns, 0.4 mm from
  the board edge and 0.9 mm free around the two QFN chips (1.5 mm on the side of the microcontroller that faces the antenna).
- Every connection is routed, by Freerouting, an open-source autorouter, and the result is
  kept in `electrical/kicad/band.ses` so that `make board` rebuilds the same board.
  `make route` draws the tracks again; it needs Java and the Freerouting jar, and it is
  only needed when the placement changes.
- The first inner layer carries ground and nothing else: the router is not allowed to use
  it, so no signal cuts the plane. Signals run on the top, the bottom and the second inner
  layer. Ground is also poured on both outer layers.
- Supply tracks (battery, charger input, 1.8 V, the two switched rails, the converter
  node) are 0.15 mm wide against 0.1 mm for signals. About 94 % of their length is at
  that width; the rest is where they narrow to enter a chip pad.
- The radio line from the chip through the matching parts to the antenna is 0.205 mm wide
  over its whole length, on the top layer, with no ground poured beside it. That width
  gives 50 ohm over the plane on an assumed stack: 0.10 mm of prepreg with a dielectric
  constant of 4.1. The stack is an assumption until a fabricator states theirs.
- There is no copper, track or via under the body of the switch.
- KiCad's check finds no open connection, no rule violation and no difference between
  board and schematic.
- The rules in the project file are an ordinary fabricator's: 0.09 mm track and gap,
  0.4 mm vias with a 0.2 mm hole, through vias only. They are an assumption, not a quote.
- Footprints are in `electrical/kicad/band.pretty`: KiCad's stock patterns for the QFN,
  the flash, crystals and chip parts; the microphone, switch and protector as drawn for the
  ring; placeholders for the antenna, the spring contacts and the cell tabs.

What this board is not: reviewed. "Routed without violations" means the copper obeys the
spacing rules and joins what the schematic joins. An autorouter knows nothing else:

- The radio line has the right width but nobody chose its path: its bends, the pads of the
  matching parts and the antenna itself (a placeholder) are not tuned.
- The converter loops, the crystal tracks and the return paths were not laid out by
  anyone, and 0.15 mm for supplies is a choice the router could finish, not a calculation.
- The router gives a different result on every run and with the ground layer closed to it
  finishes about one run in six; the script repeats it until KiCad is satisfied.
- The QFN patterns are KiCad's stock ones, compared with Nordic's package tables (a test
  keeps that comparison) and with the patterns in Nordic's reference layouts
  (nRF54L15-QFAA 0.8, nPM1304-QEAA 1.0; the numbers are in `parts/pins`). Pin order, pitch
  and the outer end of the pads agree. They differ in three ways, none changed here:
  - Microcontroller: Nordic's pads are shorter towards the centre (0.65 mm against 0.8)
    and its centre land larger (4.7 mm against 4.6), which leaves 0.35 mm between the two
    where this board has 0.25.
  - Power chip: Nordic's pads are wider (0.3 mm against 0.25) and its centre land is
    3.5 mm against 3.45.
  - Nordic puts through vias under both chips into the ground plane (16 and 9). This
    board has none: the centre lands reach ground only through the top copper, and the
    router ran tracks under the chips on the other layers.

It is a board to look at and to measure the placement against, not one to order.

Courtyard checks are switched off: spacing is enforced by the placer instead.

## Power

In [power-budget.md](power-budget.md). In short, on the 120 mAh cell: about six days on a
typical day at the nominal figures, between two and fifteen across all the cases in the
table. `mnemo-band` estimated 1.3 mA for the same day on the older chip; this budget says
0.66 mA. The difference is the nRF54L15's lower active current, taken from the vendor and
not yet from a bench, so the older figure is the one to plan on until then.

## Radio

Unknown until measured, but a much easier case than the ring: a plastic pod, an antenna
in a corner clear of copper, the cell a centimetre away. The wrist behind it absorbs; expect
to lose a few dB against free space (an estimate). The tuning network stays next to the
antenna and the antenna type stays open.

## Prior art

| Product | What it shows |
| --- | --- |
| Bee, first model (Pioneer) | Two microphones, one button in the middle of the band, a light, USB-C on the back, a strap and a clip in the box, seven days claimed |
| Bee, second model (Frontier), under Amazon | Smaller, lighter, water-resistant; one retailer's sheet gives 36 x 19 x 13.4 mm and 8 g and warns it may be wrong |
| Omi Consumer | Open hardware with the same blocks: two T5838, a 1.8 V rail, wake-on-sound. See `mnemo-band/docs/prior-art.md` |

Read on 2026-11-23 from product pages and press, not from a device. No teardown of either
Bee was found: its chip, its cell and its real battery life are not known here. One review
is reported to have measured much less than the seven days claimed.
