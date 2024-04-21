#pragma once
#include <ctime>
#include <string>

struct Article {
  std::string title;
  std::string link;
  std::string guid;
  time_t pub_date;
  std::string target = "<#shorts>";
};
