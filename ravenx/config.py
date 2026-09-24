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

# Per-observation features. Every model (RF, XGBoost, GRU, GAT, RAVEN-X) gets
# exactly the same columns, so differences between models come from the
# architecture (temporal / spatial context), not from extra inputs.
# The first eight are the plan's baseline list; AccelError (plan 3.3),
# TimeLag and MsgCount are added because timing and flooding attacks are
# otherwise invisible to a per-message model. RoadEdgeDist (NextGen's
# distance_to_road_edge of the claimed position) and ClaimedDistance
# (receiver to claimed position) are map/geometry plausibility checks: a
# constant position offset keeps every message self-consistent, and on the
# real data no other feature detects it.
FEATURES = [
    "Speed",
    "Heading",
    "Acceleration",
    "PositionChange",
    "SpeedChange",
    "HeadingChange",
    "SpeedError",
    "MessageGap",
    "AccelError",
    "TimeLag",
    "MsgCount",
    "RoadEdgeDist",
    "ClaimedDistance",
]

SPLITS = ("train", "val", "test")

# Defaults (all overridable from the command line).
BIN_SECONDS = 1.0      # length of one graph snapshot / one observation step
NEIGHBOR_RADIUS = 150.0  # metres; edge if reported positions are closer than this
SEQ_LEN = 10           # T in the plan (t1 ... t10)
