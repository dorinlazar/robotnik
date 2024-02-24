#include "robotnik.hpp"

#include <CLI/CLI.hpp>

int main(int argc, char **argv)
{
  CLI::App app{"Robotnik C++ roboțel for discord"};

  std::string filename;
  app.add_option("-f,--file", filename, "A help string");

  CLI11_PARSE(app, argc, argv);

  // Use filename here

  return 0;
}
