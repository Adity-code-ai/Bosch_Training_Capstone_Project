#pragma once

namespace ldm {

enum class Risk {
    None,
    Left,
    Right
};

enum class DecisionStatus {
    MitigationAllowed,
    MitigationInhibited,
    InputUnavailable,
    Degraded
};

enum class Reason {
    MitigationAllowed,
    LdmDisabled,
    InputInvalid,
    InputStale,
    SpeedOutOfRange,
    NoDepartureRisk,
    MatchingTurnSignal,
    DriverOverride,
    Unknown
};

struct LdmInput {
    bool enabled;
    Risk risk;
    bool speedInTrainingRange;
    bool leftTurnSignalOn;
    bool rightTurnSignalOn;
    bool driverOverride;
    bool inputValid;
    bool inputFresh;
};

struct LdmDecision {
    DecisionStatus status;
    bool requestMitigation;
    Risk requestedSide;
    Reason reason;
};

LdmDecision evaluateLdm(const LdmInput& input);

}  // namespace ldm
