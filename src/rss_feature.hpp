#pragma once
#include "bot_feature.hpp"

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

class FeedCollection {
public:
  FeedCollection& Instance();
  void AddFeed(const std::string& url, const std::string& channel);
};