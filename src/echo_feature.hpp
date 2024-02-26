#pragma once
#include "bot_feature.hpp"

class EchoFeature : public IRobotFeature {
public:
  ~EchoFeature() override = default;

  RobotFeatureDescription Description() const override;
  void HandleCommand(const dpp::slashcommand_t& event) override;
};