#include "robotnik.hpp"
#include <print>

DiscordBot::DiscordBot(const YAML::Node& config)
    : m_token(config["token"].as<std::string>()), m_owner(config["owner"].as<std::string>()),
      m_guild_name(config["guild"].as<std::string>()), m_bot(dpp::cluster(m_token)) {
  m_bot.on_slashcommand([this](auto event) { CommandHandler(event); });
}

DiscordBot::~DiscordBot() = default;

void DiscordBot::RegisterFeature(std::shared_ptr<IRobotFeature> feature) { m_features.push_back(feature); }

void DiscordBot::Start() {
  m_bot.on_ready([this](auto event) {
    if (dpp::run_once<struct register_bot_commands>()) {
      for (const auto& feature: m_features) {
        auto description = feature->Description();
        dpp::slashcommand cmd(description.moniker, description.description, m_bot.me.id);
        std::println("Registering command: {} --> {}", description.moniker, description.description);

        for (const auto& option: description.options) {
          cmd.add_option(dpp::command_option(option.type, option.option_name, option.description, option.required));
        }

        m_bot.global_command_create(cmd);
      }
    }
    // m_bot.start_timer(
    //     [this](const dpp::timer& timer) {
    //       for (const auto& feature: m_features) {
    //         feature->Tick();
    //       }
    //     },
    //     60);
  });

  m_bot.start(dpp::st_wait);
}

void DiscordBot::CommandHandler(const dpp::slashcommand_t& event) {
  for (const auto& feature: m_features) {
    if (event.command.get_command_name() == feature->Description().moniker) {
      feature->HandleCommand(event);
      return;
    }
  }
}

void DiscordBot::SendMessage(const std::string& message, const std::string& channel) {
  std::println("Sending message '{}' on channel {}", message, channel);
  std::string ch = channel;
  if (ch.starts_with("<#")) {
    ch = ch.substr(2, ch.size() - 3);
  }
  dpp::message msg(dpp::snowflake(ch), message);
  std::println("Sending message '{}' on channel {}", msg.content, msg.channel_id.str());
  m_bot.message_create(msg);
}
