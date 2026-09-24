"""Shared constants for the RAVEN-X experiments."""

# The 15 VeReMi NextGen attack subsets, in the order used by the plan.
ATTACKS = [
    "constantPositionOffset",
    "randomPositionOffset",
    "positionMirroring",
    "constantSpeedOffset",
    "randomSpeedOffset",
    "zeroSpeedReport",
    "suddenConstantSpeed",
    "reversedHeading",
    "feignedBraking",
    "accelerationMultiplication",
    "suddenStop",
    "dosAttack",
    "trafficCongestionSybil",
    "dataReplay",
    "timeDelayAttack",
]

ATTACK_NAMES = {
    "constantPositionOffset": "Constant Position Offset",
    "randomPositionOffset": "Random Position Offset",
    "positionMirroring": "Position Mirroring",
    "constantSpeedOffset": "Constant Speed Offset",
    "randomSpeedOffset": "Random Speed Offset",
    "zeroSpeedReport": "Zero Speed Report",
    "suddenConstantSpeed": "Sudden Constant Speed",
    "reversedHeading": "Reversed Heading",
    "feignedBraking": "Feigned Braking",
    "accelerationMultiplication": "Acceleration Multiplication",
    "suddenStop": "Sudden Stop",
    "dosAttack": "DoS",
    "trafficCongestionSybil": "Traffic Congestion Sybil",
    "dataReplay": "Data Replay",
    "timeDelayAttack": "Time Delay",
}

# Per-observation features. Every model gets exactly the same columns, so
# differences between models come from the architecture (temporal / spatial
# context), not from extra inputs.
#
#   reported state        Speed, Heading, Acceleration
#   change over time      PositionChange, SpeedChange, HeadingChange, Jerk
#   self-consistency      SpeedInconsistency (position-derived vs reported
#                         speed), AccelerationInconsistency (speed change vs
#                         reported acceleration), HeadingInconsistency
#                         (reported heading vs direction of motion)
#   timing / flooding     MessageGap, TimeLag, MsgCount
#   map / geometry        RoadEdgeDist (NextGen distance_to_road_edge of the
#                         claimed position), DistanceToReceiver
#   relative to receiver  RelativeSpeed, RelativeHeading
FEATURES = [
    "Speed",
    "Heading",
    "Acceleration",
    "PositionChange",
    "SpeedChange",
    "HeadingChange",
    "Jerk",
    "SpeedInconsistency",
    "AccelerationInconsistency",
    "HeadingInconsistency",
    "MessageGap",
    "TimeLag",
    "MsgCount",
    "RoadEdgeDist",
    "DistanceToReceiver",
    "RelativeSpeed",
    "RelativeHeading",
]

SPLITS = ("train", "val", "test")

# Defaults (all overridable from the command line).
BIN_SECONDS = 1.0      # length of one graph snapshot / one observation step
NEIGHBOR_RADIUS = 150.0  # metres; edge if reported positions are closer than this
SEQ_LEN = 10           # T in the plan (t1 ... t10)
