#pragma once

#include <yaml-cpp/yaml.h>
#include "bot_feature.hpp"

class DiscordBot {
private:
  std::string m_token;
  std::string m_owner;
  std::string m_guild_name;
  dpp::cluster m_bot;
  std::vector<std::shared_ptr<IRobotFeature>> m_features;

  void CommandHandler(const dpp::slashcommand_t& event);

public:
  DiscordBot(const YAML::Node& config);
  ~DiscordBot();
  void RegisterFeature(std::shared_ptr<IRobotFeature> feature);
  void Start();
};
