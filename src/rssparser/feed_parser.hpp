#pragma once
#include <vector>
#include <string>

#include "expat_parser.hpp"
#include "article.hpp"

enum class FeedSystemType { Atom, Rss };
struct FeedSystem {
  const FeedSystemType type;
  const std::string channel_tag_name;
  const std::string item_name;
  const std::string last_build_date_name;
  const std::string guid_name;
  const std::string publish_item_date_name;
};

class FeedParser : public XmlParser {
public:
  FeedParser() = default;
  ~FeedParser() override;

  bool StartElement(const std::string& name, const std::map<std::string, std::string>& attributes) override;

  bool EndElement(const std::string& name) override;
  bool CharacterData(const std::string& data) override;

  const std::vector<Article>& GetArticles() const;

private:
  bool UpdateFeedSystem(const std::string& name);
  bool StartChannel(const std::string& name);
  bool StartItem(const std::string& name);
  bool ProcessStartElementInItem(const std::string& name, const std::map<std::string, std::string>& attributes);
  bool ProcessOutOfItemEndElement(const std::string& name);
  bool ProcessInItemEndElement(const std::string& name);

  std::unique_ptr<FeedSystem> m_feed_system;
  bool m_in_channel{false};
  bool m_in_item{false};
  std::string m_current_data;
  std::string m_current_element;
  std::vector<Article> m_articles;
  Article m_current_article;
  time_t m_build_date;
};
