#pragma once

#include <dpp/dpp.h>

struct RobotFeatureOption {
  dpp::command_option_type type;
  std::string option_name;
  std::string description;
  bool required;
};

struct RobotFeatureDescription {
  std::string moniker;
  std::string description;
  std::vector<RobotFeatureOption> options;
};

class IRobotFeature {
public:
  virtual ~IRobotFeature() = default;
  virtual RobotFeatureDescription Description() const = 0;
  virtual void HandleCommand(const dpp::slashcommand_t& event) = 0;
  virtual void Tick() = 0;
};
