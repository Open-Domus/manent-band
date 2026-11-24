# Open questions

## Decisions for the project owner

Each has a draft answer in the design, chosen so the scripts had something to check.

| Question | Why it matters | Draft |
| --- | --- | --- |
| Pads on the back with a dock, or a USB-C socket | Pads keep the pod closed; a socket needs no dock | pads |
| Pod size | 36 x 19 x 9 holds about 120 mAh; 38 x 22 x 10 about 170 mAh | 36 x 19 x 9 |
| One microphone or two | The second costs a part and a hole; whether a covered port loses speech is not measured | two |
| Button on the outer face or on the side | The face is where Bee has it; `mnemo-band`'s carrier board asks for the side | outer face, centre |
| Where the factory reset goes | The firmware's 10 s hold collides with the power chip's 10 s power cycle | not chosen |
| A vibration motor | Confirms a mute without looking; no room for one in the slim pod | none |
| How bright the light is, and whether it glows all day | It is a quarter of the energy at the draft currents | 0.05 mA steady, 0.5 mA while recording |
| Name | The firmware repository is `mnemo-band`; this one follows the ring | Manent band |
| Licence for the scripts | Not covered by the hardware or document licences | undecided |

## To confirm from documents

| Item | Where to look |
| --- | --- |
| Flash: exact 512 Mbit 1.8 V part, package drawing, height, exposed pad, standby current | Winbond, and one alternative maker |
| nPM1304: what to do with SW2, VOUT2, LED0-2, GPIO2-3 when unused; which capacitor on which net | Nordic's reference design files |
| nPM1304 against nPM1300 for a cell this size: charge current range, quiescent current | Nordic |
| nRF54L15 QFN48 and nPM1304 QFN32: pin tables read once as page text, to compare with the package figures | Nordic's product specifications |
| nRF54L15 QFN48 reference circuit: which net each capacitor, the bead and the matching parts sit on; the 32 MHz crystal part | Nordic's reference layout files (the schematic on the site is a picture) |
| Land patterns for both QFN packages | Nordic's package drawings |
| T5838: both microphones on one data line with separate threshold pins; behaviour of the sleeping one on the bus | TDK datasheet and application note |
| Cell: a real part with drawing, capacity, protection board or not, tab position | quotes from two suppliers |
| Spring contacts about 5 mm tall, or another way from the board to the back pads | distributor search |
| N-MOSFETs for the light and the protection; 2.2 uH inductor | distributor search |
| nRF54L15 errata for P1.04-P1.10 at power-on | Nordic errata, revision in stock |
| What Bee actually contains | a teardown or its radio approval file, if one appears |

## To measure, no band needed (development kit and breakouts)

1. Current while recording: Opus duty cycle, PDM, flash writes.
2. Wake-on-sound: which mode and threshold wakes on speech across a table and not on a room's hum.
3. Light: current needed to be seen through a light pipe, indoors and outdoors.
4. Link current with the 32.768 kHz crystal and without.
5. Charging a 120 mAh cell through the power chip; fuel-gauge behaviour.

## To measure on a band

1. How much of a real day is recorded, and the days between charges that follow.
2. Microphones: sleeve and handling noise, a covered port, the membrane's loss.
3. Antenna efficiency and range in the closed pod, on a wrist and on a clip.
4. Button feel through the cap; accidental presses.
5. Heat while charging in a closed pod; water; skin contact of the back shell.

## Not designed yet

A review of the board by a person: antenna feed, supply and return paths, crystal, the layer stack with a fabricator; the two shells, their joint and
seal; the button cap, the light pipe, the microphone gaskets and membranes; the strap and
the clip; the dock; the antenna; firmware changes against `mnemo-band` (pins, power chip
driver, two microphones, two light levels, 512 Mbit buffer); compliance (radio, lithium
cell); the law on recording other people, which differs by country.
