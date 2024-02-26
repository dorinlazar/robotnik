#include "echo_feature.hpp"

RobotFeatureDescription EchoFeature::Description() const {
  return RobotFeatureDescription{"echo",
                                 "Un ecou, că un răsunet nu avem",
                                 {{dpp::co_string, "text", "The text to echo", false}}};
}

void EchoFeature::HandleCommand(const dpp::slashcommand_t& event) {
  auto text = std::get<std::string>(event.get_parameter("text"));
  event.reply("Pong: " + text + "!");
}
