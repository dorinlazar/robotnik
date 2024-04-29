#include "rss_feature.hpp"
#include "dblayer/key_value_store.hpp"
#include "rssparser/feed_data.hpp"

#include <nlohmann/json.hpp>
#include <set>

class FeedCollection {
private:
  FeedCollection() {}

public:
  static FeedCollection& Instance() {
    static FeedCollection instance;
    return instance;
  }

  void RestoreFeeds(const std::string& filename) {
    m_kvstore = std::make_unique<KVStore>(filename);
    auto items = m_kvstore->GetAll();
    for (const auto& item: items) {
      m_feeds.emplace_back(item.key, item.value);
    }
  }
  void AddFeed(const std::string& url, const std::string& channel);
  void DelFeed(const std::string& url);
  std::vector<std::string> ListFeeds();

private:
  std::unique_ptr<KVStore> m_kvstore;
  std::vector<FeedData> m_feeds;
};

void InitializeFeedCollector(const std::string& filename) { FeedCollection::Instance().RestoreFeeds(filename); }

RobotFeatureDescription RssAddFeature::Description() const {
  return RobotFeatureDescription{.moniker = "rssadd",
                                 .description = "Add an RSS feed to the bot.",
                                 .options = {{.type = dpp::co_string,
                                              .option_name = "url",
                                              .description = "The URL to add to the bod",
                                              .required = true,
                                              .choices = ""},
                                             {.type = dpp::co_string,
                                              .option_name = "channel",
                                              .description = "The channel to post the feed to",
                                              .required = true,
                                              .choices = ""}}};
}

void RssAddFeature::HandleCommand(const dpp::slashcommand_t& event) {
  auto url = std::get<std::string>(event.get_parameter("url"));
  auto channel = std::get<std::string>(event.get_parameter("channel"));

  FeedCollection::Instance().AddFeed(url, channel);
  event.reply("Feed added!");
}
