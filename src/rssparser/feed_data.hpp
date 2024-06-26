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

  std::vector<Article> GetNewArticles(bool force = false);
  std::string ToJson() const;
  const std::string& Url() const;
  const std::string& Destination() const;
  const std::string& Title() const;
  bool Rare() const;
  bool Updated() const;

private:
  void UpdateRarity(const std::vector<Article>& articles);
  bool m_updated = false;
  int64_t m_recheck_counter = 10000;
  int64_t m_rarity_score = 0;
  std::string m_title;
  std::string m_feed_url;
  std::set<std::string> m_article_ids;
  time_t m_last_updated = 0;
  std::string m_destination = "<#shorts>";
};