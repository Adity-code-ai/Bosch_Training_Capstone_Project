#include <gtest/gtest.h>

#include "ldm/decision.hpp"

namespace ldm {

namespace {

LdmInput makeValidInput(Risk risk, bool leftSignal = false, bool rightSignal = false, bool overrideOn = false) {
    return LdmInput{
        .enabled = true,
        .risk = risk,
        .speedInTrainingRange = true,
        .leftTurnSignalOn = leftSignal,
        .rightTurnSignalOn = rightSignal,
        .driverOverride = overrideOn,
        .inputValid = true,
        .inputFresh = true};
}

}  // namespace

TEST(LdmDecisionTest, AllowsLeftMitigationWhenAllConditionsAreSatisfied) {
    const auto input = makeValidInput(Risk::Left);

    const auto result = evaluateLdm(input);

    EXPECT_EQ(result.status, DecisionStatus::MitigationAllowed);
    EXPECT_TRUE(result.requestMitigation);
    EXPECT_EQ(result.requestedSide, Risk::Left);
    EXPECT_EQ(result.reason, Reason::MitigationAllowed);
}

TEST(LdmDecisionTest, AllowsRightMitigationWhenAllConditionsAreSatisfied) {
    const auto input = makeValidInput(Risk::Right);

    const auto result = evaluateLdm(input);

    EXPECT_EQ(result.status, DecisionStatus::MitigationAllowed);
    EXPECT_TRUE(result.requestMitigation);
    EXPECT_EQ(result.requestedSide, Risk::Right);
    EXPECT_EQ(result.reason, Reason::MitigationAllowed);
}

TEST(LdmDecisionTest, InhibitsWhenLdmDisabled) {
    LdmInput input = makeValidInput(Risk::Left);
    input.enabled = false;

    const auto result = evaluateLdm(input);

    EXPECT_EQ(result.status, DecisionStatus::MitigationInhibited);
    EXPECT_FALSE(result.requestMitigation);
    EXPECT_EQ(result.reason, Reason::LdmDisabled);
}

TEST(LdmDecisionTest, InhibitsWhenSpeedIsOutOfRange) {
    LdmInput input = makeValidInput(Risk::Left);
    input.speedInTrainingRange = false;

    const auto result = evaluateLdm(input);

    EXPECT_EQ(result.status, DecisionStatus::MitigationInhibited);
    EXPECT_FALSE(result.requestMitigation);
    EXPECT_EQ(result.reason, Reason::SpeedOutOfRange);
}

TEST(LdmDecisionTest, InhibitsWhenNoDepartureRiskExists) {
    LdmInput input = makeValidInput(Risk::None);

    const auto result = evaluateLdm(input);

    EXPECT_EQ(result.status, DecisionStatus::MitigationInhibited);
    EXPECT_FALSE(result.requestMitigation);
    EXPECT_EQ(result.reason, Reason::NoDepartureRisk);
}

TEST(LdmDecisionTest, InhibitsWhenMatchingLeftTurnSignalIsActive) {
    LdmInput input = makeValidInput(Risk::Left, true, false);

    const auto result = evaluateLdm(input);

    EXPECT_EQ(result.status, DecisionStatus::MitigationInhibited);
    EXPECT_FALSE(result.requestMitigation);
    EXPECT_EQ(result.reason, Reason::MatchingTurnSignal);
}

TEST(LdmDecisionTest, InhibitsWhenMatchingRightTurnSignalIsActive) {
    LdmInput input = makeValidInput(Risk::Right, false, true);

    const auto result = evaluateLdm(input);

    EXPECT_EQ(result.status, DecisionStatus::MitigationInhibited);
    EXPECT_FALSE(result.requestMitigation);
    EXPECT_EQ(result.reason, Reason::MatchingTurnSignal);
}

TEST(LdmDecisionTest, InhibitsWhenDriverOverrideIsActive) {
    LdmInput input = makeValidInput(Risk::Right, false, false, true);

    const auto result = evaluateLdm(input);

    EXPECT_EQ(result.status, DecisionStatus::MitigationInhibited);
    EXPECT_FALSE(result.requestMitigation);
    EXPECT_EQ(result.reason, Reason::DriverOverride);
}

TEST(LdmDecisionTest, ReturnsUnavailableWhenInputIsInvalid) {
    LdmInput input = makeValidInput(Risk::Left);
    input.inputValid = false;

    const auto result = evaluateLdm(input);

    EXPECT_EQ(result.status, DecisionStatus::InputUnavailable);
    EXPECT_FALSE(result.requestMitigation);
    EXPECT_EQ(result.reason, Reason::InputInvalid);
}

TEST(LdmDecisionTest, ReturnsDegradedWhenInputIsStale) {
    LdmInput input = makeValidInput(Risk::Right);
    input.inputFresh = false;

    const auto result = evaluateLdm(input);

    EXPECT_EQ(result.status, DecisionStatus::Degraded);
    EXPECT_FALSE(result.requestMitigation);
    EXPECT_EQ(result.reason, Reason::InputStale);
}

TEST(LdmDecisionTest, InvalidInputHasHighestPriorityOverOtherInhibits) {
    LdmInput input = makeValidInput(Risk::Left, true, false, true);
    input.inputValid = false;
    input.inputFresh = false;
    input.enabled = false;
    input.speedInTrainingRange = false;

    const auto result = evaluateLdm(input);

    EXPECT_EQ(result.status, DecisionStatus::InputUnavailable);
    EXPECT_FALSE(result.requestMitigation);
    EXPECT_EQ(result.reason, Reason::InputInvalid);
}

TEST(LdmDecisionTest, StaleInputHasPriorityOverDisabledAndRiskRules) {
    LdmInput input = makeValidInput(Risk::Left, false, false, false);
    input.inputFresh = false;
    input.enabled = false;

    const auto result = evaluateLdm(input);

    EXPECT_EQ(result.status, DecisionStatus::Degraded);
    EXPECT_FALSE(result.requestMitigation);
    EXPECT_EQ(result.reason, Reason::InputStale);
}

TEST(LdmDecisionTest, DisabledLdmHasPriorityOverNoRiskAndTurnSignalRules) {
    LdmInput input = makeValidInput(Risk::Left, true, false, false);
    input.enabled = false;

    const auto result = evaluateLdm(input);

    EXPECT_EQ(result.status, DecisionStatus::MitigationInhibited);
    EXPECT_FALSE(result.requestMitigation);
    EXPECT_EQ(result.reason, Reason::LdmDisabled);
}

TEST(LdmDecisionTest, SameInputProducesSameResultAcrossRepeatedCalls) {
    const auto input = makeValidInput(Risk::Right);

    const auto first = evaluateLdm(input);
    const auto second = evaluateLdm(input);

    EXPECT_EQ(first.status, second.status);
    EXPECT_EQ(first.requestMitigation, second.requestMitigation);
    EXPECT_EQ(first.requestedSide, second.requestedSide);
    EXPECT_EQ(first.reason, second.reason);
}

TEST(LdmDecisionTest, InputIsNotMutatedByEvaluation) {
    auto input = makeValidInput(Risk::Left);
    const auto original = input;

    const auto result = evaluateLdm(input);

    EXPECT_EQ(input.enabled, original.enabled);
    EXPECT_EQ(input.risk, original.risk);
    EXPECT_EQ(input.speedInTrainingRange, original.speedInTrainingRange);
    EXPECT_EQ(input.leftTurnSignalOn, original.leftTurnSignalOn);
    EXPECT_EQ(input.rightTurnSignalOn, original.rightTurnSignalOn);
    EXPECT_EQ(input.driverOverride, original.driverOverride);
    EXPECT_EQ(input.inputValid, original.inputValid);
    EXPECT_EQ(input.inputFresh, original.inputFresh);
    EXPECT_EQ(result.requestedSide, Risk::Left);
}

}  // namespace ldm
