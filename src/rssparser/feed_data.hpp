#pragma once

#include <string>
#include <set>
#include <vector>
#include <ctime>

#include "article.hpp"

class FeedData {
public:
  FeedData(const std::string& url, const std::string& json_serialized);

  std::vector<Article> GetNewArticles();
  std::string ToJson() const;

private:
  std::string m_feed_url;
  std::set<std::string> m_article_ids;
  time_t m_last_updated = 0;
  std::string m_destination = "<#shorts>";
};