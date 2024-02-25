#include "robotnik.hpp"

#include <CLI/CLI.hpp>
#include <dpp/dpp.h>

int main(int argc, char** argv) {
  CLI::App app{"Robotnik C++ roboțel for discord"};

  std::string filename;
  app.add_option("-f,--file", filename, "The configuration file");

  CLI11_PARSE(app, argc, argv);

  YAML::Node config = YAML::LoadFile(filename);
  DiscordBot bot(config["discord"]);
  bot.bot.on_slashcommand([](auto event) {
    if (event.command.get_command_name() == "ping") {
      auto text = std::get<std::string>(event.get_parameter("text"));
      event.reply("Pong: " + text + "!");
    }
  });

  bot.bot.on_ready([&bot](auto event) {
    if (dpp::run_once<struct register_bot_commands>()) {
      dpp::slashcommand cmd("ping", "Ping pong!", bot.bot.me.id);

      cmd.add_option(dpp::command_option(dpp::co_string, "text", "The text to echo", false));
      bot.bot.global_command_create(cmd);
    }
  });

  bot.bot.start(dpp::st_wait);

  return 0;
}
