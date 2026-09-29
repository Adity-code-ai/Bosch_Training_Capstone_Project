#include "ldm/decision.hpp"

namespace ldm {

LdmDecision evaluateLdm(const LdmInput& input) {
    if (!input.inputValid) {
        return {DecisionStatus::InputUnavailable, false, Risk::None, Reason::InputInvalid};
    }

    if (!input.inputFresh) {
        return {DecisionStatus::Degraded, false, Risk::None, Reason::InputStale};
    }

    if (!input.enabled) {
        return {DecisionStatus::MitigationInhibited, false, Risk::None, Reason::LdmDisabled};
    }

    if (!input.speedInTrainingRange) {
        return {DecisionStatus::MitigationInhibited, false, Risk::None, Reason::SpeedOutOfRange};
    }

    if (input.risk == Risk::None) {
        return {DecisionStatus::MitigationInhibited, false, Risk::None, Reason::NoDepartureRisk};
    }

    if ((input.risk == Risk::Left && input.leftTurnSignalOn) ||
        (input.risk == Risk::Right && input.rightTurnSignalOn)) {
        return {DecisionStatus::MitigationInhibited, false, Risk::None, Reason::MatchingTurnSignal};
    }

    if (input.driverOverride) {
        return {DecisionStatus::MitigationInhibited, false, Risk::None, Reason::DriverOverride};
    }

    if (input.risk == Risk::Left) {
        return {DecisionStatus::MitigationAllowed, true, Risk::Left, Reason::MitigationAllowed};
    }

    if (input.risk == Risk::Right) {
        return {DecisionStatus::MitigationAllowed, true, Risk::Right, Reason::MitigationAllowed};
    }

    return {DecisionStatus::MitigationInhibited, false, Risk::None, Reason::Unknown};
}

}  // namespace ldm
