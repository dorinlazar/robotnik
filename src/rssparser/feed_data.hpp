#pragma once

#include <string>
#include <set>
#include <ctime>

class FeedData {
public:
private:
  std::string m_feed_url;
  std::set<std::string> m_article_ids;
  time_t m_last_updated = 0;
  time_t m_last_touched = 0;
  std::string m_destination = "<#shorts>";
};