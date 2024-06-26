#include "robotnik.hpp"
#include "echo_feature.hpp"
#include <CLI/CLI.hpp>
#include <yaml-cpp/yaml.h>
#include "rss_feature.hpp"
#include <unistd.h>
#include <print>
#include <systemd/sd-daemon.h>

int main(int argc, char** argv) {
  CLI::App app{"Robotnik C++ roboțel for discord"};

  std::string home = std::getenv("HOME");
  std::println("Home: {}", home);
  std::string filename = home + "/.robotnik.yml";
  app.add_option("-f,--file", filename, "The configuration file");

  CLI11_PARSE(app, argc, argv);

  YAML::Node config = YAML::LoadFile(filename);
  auto bot = std::make_shared<DiscordBot>(config["discord"]);
  auto gdbm_file = home + "/.robotnik.rss.gdbm";
  InitializeFeedCollector(bot, gdbm_file);
  bot->RegisterFeature(std::make_shared<EchoFeature>());
  bot->RegisterFeature(std::make_shared<RssAddFeature>());
  bot->RegisterFeature(std::make_shared<RssDelFeature>());
  bot->RegisterFeature(std::make_shared<RssListFeature>());
  sd_notify(0, "READY=1");
  bot->Start();
  sd_notify(0, "STOPPING=1");
  return 0;
}
