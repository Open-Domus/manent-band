import pytest

from band_mech import stack as S
from band_mech.checks import circuit_bodies, envelope_report, size_sweep
from band_mech.params import ADOPTED, ENVELOPES


@pytest.fixture(scope="module")
def reports():
    return {k: envelope_report(k) for k in ENVELOPES}


def test_both_envelopes_fit(reports):
    for key, rep in reports.items():
        assert rep["ok"], (key, rep["problems"])


def test_adopted_envelope_is_the_slim_one(reports):
    assert reports[ADOPTED]["pod"] == [36.0, 19.0, 9.0]
    assert reports[ADOPTED]["cell"]["capacity_mah"] >= 100


def test_the_stack_adds_up_to_the_pod_height(reports):
    for key, rep in reports.items():
        assert sum(rep["stack"].values()) == pytest.approx(ENVELOPES[key].height, abs=0.02)


def test_a_pod_too_thin_has_no_cell():
    thin = ENVELOPES["A"].resized(height=7.0)
    rep = envelope_report("A", thin)
    assert not rep["ok"] and rep["cell"] is None


def test_microphones_are_at_opposite_ends(reports):
    for rep in reports.values():
        assert rep["mic_distance"] >= S.MIN_MIC_DISTANCE


def test_every_part_of_the_circuit_is_in_the_model(reports):
    bodies = circuit_bodies()
    large = sorted(b for b in bodies if b not in S.SMALL)
    placed = sorted(pl["part"] for pl in reports[ADOPTED]["placed"] if pl["part"])
    assert placed == large and len(large) >= 19
    assert reports[ADOPTED]["area"]["small_parts"] == len(bodies) - len(large) > 40


def test_wider_or_taller_pods_never_lose_capacity():
    rows = size_sweep()
    assert all(r["capacity_mah"] for r in rows)
    by = {(r["pod"][1], r["pod"][2]): r["capacity_mah"] for r in rows}
    assert by[(22.0, 10.0)] >= by[(19.0, 10.0)] >= by[(19.0, 8.5)]


def test_parts_are_complete():
    parts = S.load_parts()
    for group in ("parts", "cells"):
        for key, part in parts[group].items():
            assert part["mpn"] and part["manufacturer"], key
            assert len(part["size"]) == 3 and all(v > 0 for v in part["size"]), key
            assert part["status"] in {"verified", "secondary", "unverified"}, key
    assert set(circuit_bodies()) - {"testpad"} <= set(parts["parts"])
