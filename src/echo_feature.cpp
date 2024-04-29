#include "echo_feature.hpp"

RobotFeatureDescription EchoFeature::Description() const {
  return RobotFeatureDescription{"echo",
                                 "Un ecou, că un răsunet nu avem",
                                 {{.type = dpp::co_string,
                                   .option_name = "text",
                                   .description = "The text to echo",
                                   .required = false,
                                   .choices = ""}}};
}

void EchoFeature::HandleCommand(const dpp::slashcommand_t& event) {
  auto text = std::get<std::string>(event.get_parameter("text"));
  event.reply("Pong: " + text + "!");
}
