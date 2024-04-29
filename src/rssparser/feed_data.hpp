#pragma once

#include <string>
#include <set>
#include <vector>
#include <ctime>
#include <memory>

#include "article.hpp"

class FeedData {
public:
  FeedData() = default;
  static std::shared_ptr<FeedData> FromJson(const std::string& url, const std::string& json);
  static std::shared_ptr<FeedData> Create(const std::string& url, const std::string& destination);

  std::vector<Article> GetNewArticles();
  std::string ToJson() const;
  const std::string& Url() const;
  const std::string& Destination() const;

private:
  std::string m_feed_url;
  std::set<std::string> m_article_ids;
  time_t m_last_updated = 0;
  std::string m_destination = "<#shorts>";
};