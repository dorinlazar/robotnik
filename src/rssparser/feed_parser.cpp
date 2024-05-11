#include "article.hpp"

#include <memory>
#include <vector>
#include <print>

#include "expat_parser.hpp"
#include "time_converters.hpp"
#include "feed_parser.hpp"

FeedSystem AtomSystem = {FeedSystemType::Atom,
                         "feed",
                         "title"
                         "entry",
                         "updated",
                         "id",
                         "published"};
FeedSystem RssSystem = {FeedSystemType::Rss, "channel", "title", "item", "lastBuildDate", "guid", "pubDate"};

FeedParser::~FeedParser() = default;

std::string GetOrDefault(const std::map<std::string, std::string>& attributes, const std::string& key,
                         const std::string& default_value = "") {
  auto it = attributes.find(key);
  if (it == attributes.end()) {
    return default_value;
  }
  return it->second;
}

bool FeedParser::StartElement(const std::string& name, const std::map<std::string, std::string>& attributes) {
  m_current_data = "";
  if (!m_feed_system) {
    return UpdateFeedSystem(name);
  }
  if (!m_in_item) {
    return StartItem(name);
  }
  return ProcessStartElementInItem(name, attributes);
}

bool FeedParser::EndElement(const std::string& name) {
  if (!m_in_item) {
    return ProcessOutOfItemEndElement(name);
  }
  return ProcessInItemEndElement(name);
}

bool FeedParser::CharacterData(const std::string& data) {
  m_current_data += data;
  return true;
}

bool FeedParser::UpdateFeedSystem(const std::string& name) {
  if (name == "rss") {
    // std::println("Using system: RSS ");
    m_feed_system = std::make_unique<FeedSystem>(RssSystem);
  } else if (name == "feed") {
    // std::println("Using system: Atom");
    m_feed_system = std::make_unique<FeedSystem>(AtomSystem);
  }
  return true;
}

bool FeedParser::StartItem(const std::string& name) {
  m_in_item = name == m_feed_system->item_name;
  if (m_in_item) {
    m_current_article = Article();
  }
  return true;
}

bool FeedParser::ProcessStartElementInItem(const std::string& name,
                                           const std::map<std::string, std::string>& attributes) {
  m_current_element = name;
  m_current_data = "";
  if (name == "link" && GetOrDefault(attributes, "rel", "alternate") == "alternate") {
    m_current_article.link = GetOrDefault(attributes, "href");
  }
  if (name == "enclosure" && m_current_article.link.empty()) {
    m_current_article.link = GetOrDefault(attributes, "url");
  }
  return true;
}

bool FeedParser::ProcessOutOfItemEndElement(const std::string& name) {
  if (!m_in_item) {
    if (name == m_feed_system->last_build_date_name) {
      m_build_date = ConvertRfc822ToTimeStamp(m_current_data);
    }
    if (name == m_feed_system->channel_title_name) {
      m_title = m_current_data;
    }
  }
  return true;
}

bool FeedParser::ProcessInItemEndElement(const std::string& name) {
  if (name == m_feed_system->item_name) {
    m_in_item = false;
    if (!m_current_article.link.empty()) {
      // std::println("New article: {} {} {} {}", m_current_article.title, m_current_article.guid,
      // m_current_article.link,
      //              m_current_article.pub_date);

      m_articles.push_back(m_current_article);
    } else {
      // std::println("No article found: {} {}", m_current_article.title, m_current_article.guid);
    }
  } else if (name == "link") {
    if (m_current_article.link.empty() && !m_current_data.empty()) {
      m_current_article.link = m_current_data;
    }
  } else if (name == m_feed_system->publish_item_date_name || name == "updated") {
    m_current_article.pub_date = ConvertRfc822ToTimeStamp(m_current_data);
  } else if (name == m_feed_system->guid_name) {
    m_current_article.guid = m_current_data;
  } else if (name == "title") {
    m_current_article.title = m_current_data;
  }
  return true;
}

const std::vector<Article>& FeedParser::GetArticles() const { return m_articles; }

const std::string& FeedParser::Title() const { return m_title; }