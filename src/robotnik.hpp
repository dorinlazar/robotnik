#pragma once

#include <yaml-cpp/yaml.h>
#include <dpp/dpp.h>

class DiscordBot {
private:
  std::string m_token;
  std::string m_owner;
  std::string m_guild_name;
public:
  DiscordBot(const YAML::Node& config);
  ~DiscordBot();

  dpp::cluster bot;

};