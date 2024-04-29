#include "feed_data.hpp"
#include "feed_fetcher.hpp"
#include "expat_parser.hpp"
#include "feed_parser.hpp"

FeedData::FeedData(const std::string& url) : m_feed_url(url) {}

std::vector<Article> FeedData::GetNewArticles() {
  FileFetcher fetcher(m_feed_url);
  auto feed_content = fetcher.FetchFeed();
  if (feed_content.empty()) {
    return {};
  }

  auto feed_parser = std::make_shared<FeedParser>();
  ExpatParser(feed_parser).Parse(feed_content);
  return feed_parser->GetArticles();
}
