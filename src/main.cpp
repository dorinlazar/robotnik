#include "robotnik.hpp"
#include "echo_feature.hpp"
#include <CLI/CLI.hpp>
#include <yaml-cpp/yaml.h>

int main(int argc, char** argv) {
  CLI::App app{"Robotnik C++ roboțel for discord"};

  std::string filename;
  app.add_option("-f,--file", filename, "The configuration file");

  CLI11_PARSE(app, argc, argv);

  YAML::Node config = YAML::LoadFile(filename);
  DiscordBot bot(config["discord"]);
  bot.RegisterFeature(std::make_shared<EchoFeature>());
  bot.Start();
  return 0;
}
