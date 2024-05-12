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
  if (parsed.contains("rarity")) {
    feed_data->m_rarity_score = parsed["rarity"];
  }

  feed_data->m_feed_url = url;
  return feed_data;
}

std::vector<Article> FeedData::GetNewArticles() {
  auto current_time = ::time(nullptr);

  if (m_rarity_score > 0) {
    m_recheck_counter++;
    if (m_recheck_counter < m_rarity_score) {
      std::println("Skipping for new articles in {} ({})", m_title, m_feed_url);
      return {};
    }
    m_recheck_counter = 0;
  }

  std::println("Checking for new articles in {} ({})", m_title, m_feed_url);

  FileFetcher fetcher(m_feed_url);
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
  m_title = feed_parser->Title();
  UpdateRarity(all_articles);
  m_last_updated = current_time;
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

void FeedData::UpdateRarity(const std::vector<Article>& articles) {
  // Determine last 10 articles timestamps
  const size_t last_articles_count = 10;
  std::array<time_t, last_articles_count> last_article_times;
  for (size_t i = 0; i < last_articles_count; i++) {
    last_article_times[i] = 0;
  }

  for (const auto& article: articles) {
    auto iterator = std::ranges::min_element(last_article_times);
    if (article.pub_date > *iterator) {
      *iterator = article.pub_date;
    }
  }
  auto n_articles_considered = last_articles_count;
  auto max_time = *std::ranges::max_element(last_article_times);
  for (auto& timestamp: last_article_times) {
    if (timestamp == 0) {
      timestamp = max_time;
      n_articles_considered--;
    }
  }
  if (n_articles_considered == 0) {
    std::println("No rarity updates for {} ({}) (no articles? bad timestamps?)", m_title, m_feed_url);
    return;
  }
  auto min_time = *std::ranges::min_element(last_article_times);
  auto time_diff = (max_time - min_time) / n_articles_considered;
  auto old_rarity = m_rarity_score;
  if (time_diff < 3600) { // 1h
    m_rarity_score = 1;
  } else if (time_diff < 86400) { // 1d
    m_rarity_score = 3;
  } else if (time_diff < 604800) { // 1w
    m_rarity_score = 5;
  } else {
    m_rarity_score = 30;
  }
  if (old_rarity != m_rarity_score) {
    std::println("Rarity score changed from {} to {} for {} ({})", old_rarity, m_rarity_score, m_title, m_feed_url);
  }
}
