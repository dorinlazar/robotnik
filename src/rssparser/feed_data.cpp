#include "feed_data.hpp"
#include "feed_fetcher.hpp"
#include "expat_parser.hpp"
#include "feed_parser.hpp"

#include <print>
#include <ctime>
#include <nlohmann/json.hpp>

FeedData::FeedData(const std::string& url, const std::string& json_serialized) : m_feed_url(url) {
  auto parsed = nlohmann::json::parse(json_serialized);
  if (parsed.contains("updated")) {
    m_last_updated = parsed["updated"];
  }
  if (parsed.contains("dest")) {
    m_destination = parsed["dest"];
  }
  if (parsed.contains("ids")) {
    for (const auto& article_id: parsed["ids"]) {
      m_article_ids.insert(article_id);
    }
  }
}

std::vector<Article> FeedData::GetNewArticles() {
  auto current_time = ::time(nullptr);

  FileFetcher fetcher(m_feed_url);
  auto feed_content = fetcher.FetchFeed();
  // std::println("Feed content: {}", feed_content);
  if (feed_content.empty()) {
    return {};
  }

  auto feed_parser = std::make_shared<FeedParser>();
  ExpatParser(feed_parser).Parse(feed_content);
  std::vector<Article> articles;
  for (const auto& article: feed_parser->GetArticles()) {
    if (!m_article_ids.contains(article.guid)) {
      articles.push_back(article);
      m_article_ids.insert(article.guid);
    }
  }
  m_last_updated = current_time;
  return articles;
}

std::string FeedData::ToJson() const {
  nlohmann::json json;
  json["updated"] = m_last_updated;
  json["dest"] = m_destination;
  json["ids"] = m_article_ids;
  return json.dump();
}
