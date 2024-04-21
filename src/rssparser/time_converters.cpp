#include "time_converters.hpp"

time_t ConvertRfc822ToTimeStamp(const std::string& rfc822_date) {
  std::tm tm = {};
  if (strptime(rfc822_date.c_str(), "%a, %d %b %Y %H:%M:%S %z", &tm) == nullptr) {
    return 0;
  }
  return std::mktime(&tm);
}

std::string ConvertTimeStampToRfc822(time_t timestamp) {
  std::tm tm = *std::localtime(&timestamp);
  char buffer[128];
  std::strftime(buffer, sizeof(buffer), "%a, %d %b %Y %H:%M:%S %z", &tm);
  return buffer;
}
