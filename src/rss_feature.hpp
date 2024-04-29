#pragma once
#include <string>
#include "bot_feature.hpp"

void InitializeFeedCollector(const std::string& filename);

class RssAddFeature : public IRobotFeature {
public:
  ~RssAddFeature() override = default;

  RobotFeatureDescription Description() const override;
  void HandleCommand(const dpp::slashcommand_t& event) override;
};

class RssDelFeature : public IRobotFeature {
public:
  ~RssDelFeature() override = default;

  RobotFeatureDescription Description() const override;
  void HandleCommand(const dpp::slashcommand_t& event) override;
};

class RssListFeature : public IRobotFeature {
public:
  ~RssListFeature() override = default;

  RobotFeatureDescription Description() const override;
  void HandleCommand(const dpp::slashcommand_t& event) override;
};
