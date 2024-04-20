#include "article.hpp"
#include "feed_digest.hpp"
#include "expat_parser.hpp"

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

  void StartElement(const std::string& name, const std::map<std::string, std::string>& attributes) override {
    m_current_element = name;
    m_current_data = "";
    if (!m_feed_system) {
      if (name == "rss") {
        m_feed_system = std::make_unique<FeedSystem>(RssSystem);
      } else if (name == "feed") {
        m_feed_system = std::make_unique<FeedSystem>(AtomSystem);
      }
      return;
    }
    if (!m_in_channel) {
      m_in_channel = name == m_feed_system->channel_tag_name;
      return;
    }
    if (m_in_item) {
      if (name == "link" && GetOrDefault(attributes, "rel", "alternate") == "alternate") {
        m_current_article.link = GetOrDefault(attributes, "href");
      }
      if (name == "enclosure" && m_current_article.link.empty()) {
        m_current_article.link = GetOrDefault(attributes, "url");
      }
    } else {
      m_in_item = name == m_feed_system->item_name;
      if (m_in_item) {
        m_current_article = Article();
      }
    }
  }

  // if self.__in_item:
  //     if name == self.__system.item_name:
  //         self.__in_item = False
  //         if self.__current_element and self.__current_element.link:
  //             self.__feed_digest.articles.append(self.__current_element)
  //         else:
  //             print("Current element is not good")
  //     else:
  //         match (name):
  //             case "link":
  //                 if not self.__current_element.link and self.__current_data:
  //                     self.__current_element.link = self.__current_data
  //             case self.__system.publish_item_date_name:
  //                 self.__current_element.pub_date = dtparser.parse(
  //                     self.__current_data
  //                 ).replace(tzinfo=tzutc())
  //             case "updated":
  //                 self.__current_element.pub_date = dtparser.parse(
  //                     self.__current_data
  //                 ).replace(tzinfo=tzutc())
  //             case self.__system.guid_name:
  //                 self.__current_element.guid = self.__current_data
  //             case "title":
  //                 f = HtmlTextFilter()
  //                 f.feed(self.__current_data)
  //                 self.__current_element.title = f.text
  // else:
  //     if name == self.__system.last_build_date_name:
  //         self.__feed_digest.build_date = dtparser.parse(
  //             self.__current_data
  //         ).replace(tzinfo=tzutc())
  // if self.__in_channel and name == self.__system.channel_tag_name:
  //     self.__in_channel = False

  void EndElement(const std::string& name) override {
    if (m_in_item) {
      if (name == m_feed_system->item_name) {
        m_in_item = false;
        if (!m_current_article.link.empty()) {
          m_articles.push_back(m_current_article);
        } else {
          std::print("Current element is not good");
        }
      }
    }
  }
  void CharacterData(const std::string& data) override { m_current_data += data; }

  // void charData(const XML_Char* s, int len) override {
  //   std::string data(s, len);
  //   if (currentElement == "title") {
  //     currentArticle.title += data;
  //   } else if (currentElement == "link") {
  //     currentArticle.link += data;
  //   } else if (currentElement == "description") {
  //     currentArticle.description += data;
  //   }
  // }

private:
  std::unique_ptr<FeedSystem> m_feed_system;
  bool m_in_channel{false};
  bool m_in_item{false};
  std::string m_current_data;
  std::string m_current_element;
  std::vector<Article> m_articles;
  Article m_current_article;
};
