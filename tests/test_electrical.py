from pathlib import Path

import pytest

from gen import checks
from gen.design import build, netlist

NETLIST = Path(__file__).resolve().parents[1] / "electrical" / "out" / "netlist.xml"


def test_circuit_rules_hold():
    assert checks.lint() == []


def test_kicad_reads_the_same_nets_we_wrote():
    if not NETLIST.exists():
        pytest.skip("run `make schematic` first")
    assert checks.compare(NETLIST) == []
    assert len(checks.kicad_netlist(NETLIST)) == len(netlist()) > 40


def test_light_follows_the_microphone_rail():
    # The steady glow must not depend on firmware: its switch is gated by VMIC itself.
    comps = build()
    gate = [c for c in comps if c.sym.name == "NMOS" and c.nets["1"] == "VMIC"]
    assert len(gate) == 1 and gate[0].nets["3"] == "LED_SW"
    assert all("VMIC" in c.nets.values() for c in comps if c.value == "T5838")


def test_firmware_can_add_light_but_not_remove_it():
    comps = build()
    led = next(c for c in comps if c.sym.name == "LED")
    cathode = led.nets["1"]
    paths = {next(n for n in c.nets.values() if n != cathode) for c in comps
             if c.sym.name == "R" and cathode in c.nets.values()}
    assert paths == {"LED_SW", "LED_HI"}
    # Nothing but the light and its two resistors touches the cathode: no pin can hold it off.
    assert len(netlist(comps)[cathode]) == 3


def test_muting_cuts_both_microphones_with_one_switch():
    comps = build()
    pmic = next(c for c in comps if c.value == "nPM1304")
    names = {p.name: pmic.nets[p.number] for p in pmic.sym.pins}
    assert names["LSOUT1"] == "VMIC" and names["GPIO1"] == "MIC_EN"
    assert len([c for c in comps if c.value == "T5838"]) == 2


def test_no_vibration_motor():
    assert not any("haptic" in c.value.lower() or "motor" in c.value.lower() for c in build())
