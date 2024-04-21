#pragma once

#include <ctime>
#include <string>

time_t ConvertRfc822ToTimeStamp(const std::string& rfc822_date);
std::string ConvertTimeStampToRfc822(time_t timestamp);
