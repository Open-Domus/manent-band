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
   button --+--> SHPHLD          [ nRF54L15 ] --PDM--> microphone A, microphone B
            +-|<|-> wake            |  |  |
                               SPI --+  |  +-- matching -- tuning -- antenna
                                v       +-- bright light
                          512 Mbit flash
```

One logic rail at 1.8 V, as on the ring: the microphones accept nothing higher.

## Parts

| Block | Part | Size (mm) | Why | Confidence |
| --- | --- | --- | --- | --- |
| Microcontroller | Nordic nRF54L15, CSP47 | 2.45 x 2.25 x 0.42 | The firmware targets it; its PDM clock suits the microphone | pinout verified for the ring |
| Power | Nordic nPM1304, CSP35 | 3.08 x 2.38 x 0.46 | Charges at up to 100 mA, enough for a 120-170 mAh cell; 1.8 V buck; two load switches; ship mode | pinout verified for the ring; some terminations not |
| Flash | Winbond W25Q512NW, WSON-8 | 8 x 6 x 0.8 | 512 Mbit holds about 7 h of speech not yet uploaded | from memory: part number, package and height to confirm |
| Microphones | 2 x TDK T5838 | 3.5 x 2.65 x 0.98 | Wake-on-sound at 20-137 uA; already planned by the firmware | verified |
| Button | Panasonic EVP-BB, 1.6 N | 2.6 x 1.6 x 0.53 | Sealed to IP67; pressed through a flexible cap | datasheet from a distributor |
| Light | Rohm SML-P11VT | 1.0 x 0.6 x 0.2 | Already on the ring | verified at 1 mA; dimmer is from curves |
| Cell protection | ABLIC S-82A1A | 1.4 x 1.4 | Fitted only if the cell has none of its own | verified |
| Charging input | Infineon ESD230-B1-W0201 | 0.58 x 0.28 | Exposed pads need ESD protection | verified |
| Cell | flat LiPo pouch, 401525 class | 25 x 15 x 4 | See the space budget | trade size code; capacity estimated |

The full list with part numbers is `electrical/out/bom.csv`.

### What is taken from the ring, and what that costs

The power chip, the microcontroller and their surrounding parts are copied from the ring,
in the same chip-scale packages, because those pin tables have been checked ball by ball
and the firmware is the same. The price is the ring's board technology: 0.3 mm pitch needs
microvias and an assembler with X-ray inspection, in a pod that has about three times the board area.
Both chips exist in QFN packages that an ordinary four-layer board can carry. Moving to
them needs their pin tables read with the same care; it is the first open question.

### Microcontroller pins

| Signal | Pin | Rule it satisfies |
| --- | --- | --- |
| Microphone clock, data | P1.04, P1.05 | PDM lives on port 1; the clock is on a clock pin |
| Microphone A threshold, wake | P1.06, P1.07 | port 1 can wake the chip |
| Microphone B threshold, wake | P1.09, P1.10 | port 1 can wake the chip |
| Microphone power request | P1.13 | to the power chip's GPIO1, which drives load switch 1 |
| Flash clock, out, in, select | P2.01, P2.02, P2.04, P2.05 | the dedicated fast-SPI pins |
| Power chip clock, data, interrupt | P0.03, P0.02, P0.01 | clock on a clock pin; port 0 can wake the chip |
| Button | P0.00 | port 0 can wake the chip |
| Bright light | P0.04 | |
| Test serial port | P1.14, P1.15 | test pads on the board |
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
- **Button to two chips**, as on the ring: to the power chip's ship-mode input, and through
  a diode to the microcontroller.

## Pod and assembly

- A plastic box 36 x 19 x 9 mm with 3 mm corners, in two shells, with no lugs: it pushes
  into a pocket in a silicone strap or into a clip. Material and how the shells are joined
  are open.
- From the wrist outwards: back shell, cell, board, parts, front shell. The board is
  33.4 x 16.4 mm, 0.6 thick, with every part except the microphones and the spring contacts
  on its outer face.
- The microphones hang under the board, one at each end, each with a hole through the
  board, a gasket between board and front shell, and a hole in the shell behind a membrane.
- The cell lies between the two microphones. That limits it to 25 mm in a 36 mm pod.
- Openings in the front shell: two microphone holes, a light pipe, and a thinned or
  two-material zone over the button. In the back shell: four contact pads.
- The antenna takes one corner of the board, at the end away from the contacts, with no
  copper under it.

Whether it all fits is in [space-budget.md](space-budget.md). In short: the 36 x 19 x 9 pod
holds a cell of about 120 mAh with 0.8 mm of height to spare; the 38 x 22 x 10 pod that
`mnemo-band` asks for holds about 170 mAh. The slim one is adopted, as a draft, because on
paper it already reaches the five days.

## Power

In [power-budget.md](power-budget.md). In short, on the 120 mAh cell: about six days on a
typical day at the nominal figures, between two and fifteen across all the cases in the
table. `mnemo-band` estimated 1.3 mA for the same day on the older chip; this budget says
0.65 mA. The difference is the nRF54L15's lower active current, taken from the vendor and
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
