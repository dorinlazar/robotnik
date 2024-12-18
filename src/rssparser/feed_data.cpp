#include "feed_data.hpp"
#include "feed_fetcher.hpp"
#include "expat_parser.hpp"
#include "feed_parser.hpp"

#include <print>
#include <ctime>
#include <nlohmann/json.hpp>
#include <ranges>

std::shared_ptr<FeedData> FeedData::Create(const std::string& url, const std::string& destination) {
  auto feed_data = std::make_shared<FeedData>();
  feed_data->m_feed_url = url;
  feed_data->m_destination = destination;
  return feed_data;
}

std::shared_ptr<FeedData> FeedData::FromJson(const std::string& url, const std::string& json) {
  auto feed_data = std::make_shared<FeedData>();
  auto parsed = nlohmann::json::parse(json);
  if (parsed.contains("updated")) {
    feed_data->m_last_updated = parsed["updated"];
  }
  if (parsed.contains("dest")) {
    feed_data->m_destination = parsed["dest"];
  }
  if (parsed.contains("ids")) {
    for (const auto& article_id: parsed["ids"]) {
      feed_data->m_article_ids.insert(article_id);
    }
  }
  if (parsed.contains("title")) {
    feed_data->m_title = parsed["title"];
  }
  feed_data->m_feed_url = url;
  return feed_data;
}

std::vector<Article> FeedData::GetNewArticles() {
  m_updated = false;
  std::println("Checking for new articles in {} ({})", m_title, m_feed_url);

  auto current_time = ::time(nullptr);
  FileFetcher fetcher(m_feed_url, m_last_updated);
  auto feed_content = fetcher.FetchFeed();
  if (feed_content.empty()) {
    return {};
  }

  auto feed_parser = std::make_shared<FeedParser>();
  ExpatParser(feed_parser).Parse(feed_content);
  std::vector<Article> articles;
  auto all_articles = feed_parser->GetArticles();
  if (all_articles.empty()) {
    return {};
  }
  for (const auto& article: all_articles) {
    if (!m_article_ids.contains(article.guid)) {
      articles.push_back(article);
    }
  }
  m_article_ids.clear();
  for (const auto& article: all_articles) {
    m_article_ids.insert(article.guid);
  }
  if (m_title != feed_parser->Title()) {
    m_updated = true;
    m_title = feed_parser->Title();
  }
  m_last_updated = feed_parser->BuildDate();
  if (!articles.empty()) {
    m_updated = true;
  }
  return articles;
}

std::string FeedData::ToJson() const {
  nlohmann::json json;
  json["updated"] = m_last_updated;
  json["dest"] = m_destination;
  json["ids"] = m_article_ids;
  json["title"] = m_title;
  return json.dump();
}

const std::string& FeedData::Url() const { return m_feed_url; }

const std::string& FeedData::Destination() const { return m_destination; }

bool FeedData::Updated() const { return m_updated; }