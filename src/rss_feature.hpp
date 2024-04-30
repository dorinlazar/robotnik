#pragma once
#include <string>
#include <memory>
#include "bot_feature.hpp"
class DiscordBot;

void InitializeFeedCollector(std::shared_ptr<DiscordBot> bot, const std::string& filename);

class RssAddFeature : public IRobotFeature {
public:
  ~RssAddFeature() override = default;

  RobotFeatureDescription Description() const override;
  void HandleCommand(const dpp::slashcommand_t& event) override;
  void Tick() override;
};

class RssDelFeature : public IRobotFeature {
public:
  ~RssDelFeature() override = default;

  RobotFeatureDescription Description() const override;
  void HandleCommand(const dpp::slashcommand_t& event) override;
  void Tick() override;
};

class RssListFeature : public IRobotFeature {
public:
  ~RssListFeature() override = default;

  RobotFeatureDescription Description() const override;
  void HandleCommand(const dpp::slashcommand_t& event) override;
  void Tick() override;
};
