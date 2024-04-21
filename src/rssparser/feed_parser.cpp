#include "article.hpp"
#include "feed_digest.hpp"
#include "expat_parser.hpp"
#include "time_converters.hpp"

#include <memory>
#include <vector>
#include <print>

enum class FeedSystemType { Atom, Rss };
struct FeedSystem {
  const FeedSystemType type;
  const std::string channel_tag_name;
  const std::string item_name;
  const std::string last_build_date_name;
  const std::string guid_name;
  const std::string publish_item_date_name;
};

FeedSystem AtomSystem = {FeedSystemType::Atom, "feed", "entry", "updated", "id", "published"};
FeedSystem RssSystem = {FeedSystemType::Rss, "channel", "item", "lastBuildDate", "guid", "pubDate"};

std::string GetOrDefault(const std::map<std::string, std::string>& attributes, const std::string& key,
                         const std::string& default_value = "") {
  auto it = attributes.find(key);
  if (it == attributes.end()) {
    return default_value;
  }
  return it->second;
}

class FeedParser : public XmlParser {
public:
  FeedParser() {}
  ~FeedParser() override = default;

  bool StartElement(const std::string& name, const std::map<std::string, std::string>& attributes) override {
    if (!m_feed_system) {
      return UpdateFeedSystem(name);
    }
    if (!m_in_channel) {
      return StartChannel(name);
    }
    if (!m_in_item) {
      return StartItem(name);
    }
    return ProcessStartElementInItem(name, attributes);
  }

  bool EndElement(const std::string& name) override {
    if (!m_in_item) {
      return ProcessOutOfItemEndElement(name);
    }
    return ProcessInItemEndElement(name);
  }

  bool CharacterData(const std::string& data) override {
    m_current_data += data;
    return true;
  }

private:
  bool UpdateFeedSystem(const std::string& name) {
    if (name == "rss") {
      m_feed_system = std::make_unique<FeedSystem>(RssSystem);
    } else if (name == "feed") {
      m_feed_system = std::make_unique<FeedSystem>(AtomSystem);
    }
    return true;
  }

  bool StartChannel(const std::string& name) {
    m_in_channel = name == m_feed_system->channel_tag_name;
    return true;
  }

  bool StartItem(const std::string& name) {
    m_in_item = name == m_feed_system->item_name;
    if (m_in_item) {
      m_current_article = Article();
    }
    return true;
  }

  bool ProcessStartElementInItem(const std::string& name, const std::map<std::string, std::string>& attributes) {
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

  bool ProcessOutOfItemEndElement(const std::string& name) {
    if (m_in_channel) {
      if (name == m_feed_system->channel_tag_name) {
        m_in_channel = false;
      } else if (name == m_feed_system->last_build_date_name) {
        m_build_date = ConvertRfc822ToTimeStamp(m_current_data);
      }
    }
    return true;
  }

  bool ProcessInItemEndElement(const std::string& name) {
    if (name == m_feed_system->item_name) {
      m_in_item = false;
      if (!m_current_article.link.empty()) {
        m_articles.push_back(m_current_article);
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

  std::unique_ptr<FeedSystem> m_feed_system;
  bool m_in_channel{false};
  bool m_in_item{false};
  std::string m_current_data;
  std::string m_current_element;
  std::vector<Article> m_articles;
  Article m_current_article;
  time_t m_build_date;
};
