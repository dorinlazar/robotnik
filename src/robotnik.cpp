#include "robotnik.hpp"

DiscordBot::DiscordBot(const YAML::Node& config)
    : m_token(config["token"].as<std::string>()), m_owner(config["owner"].as<std::string>()),
      m_guild_name(config["guild"].as<std::string>()), bot(dpp::cluster(m_token)) {}

DiscordBot::~DiscordBot() = default;
