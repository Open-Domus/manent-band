"""Pod envelope parameters. All lengths in millimetres.

The pod is a closed plastic box with rounded corners that sits in a strap or a clip.
X runs along its length, Y across it, Z from the face against the wrist to the outer face.
"""
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class PodParams:
    name: str
    length: float
    width: float
    height: float
    wall: float = 1.0        # side walls
    back: float = 0.9        # face against the wrist
    front: float = 1.0       # outer face: button cap, light pipe, microphone holes
    corner_r: float = 3.0     # seen from outside; the board follows it
    board_gap: float = 0.3   # between the board edge and the side walls
    board_t: float = 0.6

    @property
    def board(self) -> tuple[float, float]:
        m = 2 * (self.wall + self.board_gap)
        return self.length - m, self.width - m

    @property
    def board_corner_r(self) -> float:
        return self.corner_r - self.wall - self.board_gap

    @property
    def cavity(self) -> tuple[float, float, float]:
        return self.length - 2 * self.wall, self.width - 2 * self.wall, self.height - self.back - self.front

    def resized(self, **kw) -> "PodParams":
        return replace(self, **kw)


# Envelope A: about the outline reported for Amazon's second Bee (36 x 19 mm, from a
# retailer's sheet that warns it may be wrong), with a height chosen here.
SLIM = PodParams("A-slim", 36.0, 19.0, 9.0)
# Envelope B: the pod the mnemo-band design document asks for (about 38 x 22 x 10).
ROOMY = PodParams("B-roomy", 38.0, 22.0, 10.0)

ENVELOPES = {"A": SLIM, "B": ROOMY}
ADOPTED = "A"
