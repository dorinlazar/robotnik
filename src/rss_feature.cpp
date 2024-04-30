#include "rss_feature.hpp"
#include "dblayer/key_value_store.hpp"
#include "rssparser/feed_data.hpp"
#include "robotnik.hpp"

#include <nlohmann/json.hpp>
#include <set>
#include <thread>
#include <condition_variable>
#include <mutex>
#include <print>

class FeedCollection {
private:
  FeedCollection() = default;

public:
  static FeedCollection& Instance() {
    static FeedCollection instance;
    return instance;
  }

  void RestoreFeeds(const std::string& filename) {
    std::unique_lock<std::mutex> lock(m_mutex);
    m_kvstore = std::make_unique<KVStore>(filename);
    auto items = m_kvstore->GetAll();
    for (const auto& item: items) {
      m_feeds.emplace_back(FeedData::FromJson(item.key, item.value));
    }
  }

  bool AddFeed(const std::string& url, const std::string& channel) {
    std::println("Adding feed: {} to channel: {}", url, channel);
    std::unique_lock<std::mutex> lock(m_mutex);
    std::println("AddFeed lock acquired");
    for (const auto& feed: m_feeds) {
      if (feed->Url() == url) {
        std::println("Feed already exists: {}", url);
        return false;
      }
    }

    std::println("Creating entry for feed: {} in channel: {}", url, channel);
    auto feed_data = FeedData::Create(url, channel);
    std::println("Storing entry for feed: {} in channel: {}", url, channel);
    m_kvstore->Put(url, feed_data->ToJson());
    std::println("Feed added: {}", url);
    m_feeds.emplace_back(std::move(feed_data));
    return true;
  }

  bool DelFeed(const std::string& url) {
    std::unique_lock<std::mutex> lock(m_mutex);
    if (!m_kvstore) {
      return false;
    }
    for (auto it = m_feeds.begin(); it != m_feeds.end(); ++it) {
      if ((*it)->Url() == url) {
        m_feeds.erase(it);
        m_kvstore->Remove(url);
        return true;
      }
    }
    return false;
  }

  std::vector<std::string> ListFeeds() {
    std::unique_lock<std::mutex> lock(m_mutex);
    std::vector<std::string> urls;
    for (const auto& feed: m_feeds) {
      urls.push_back(feed->Url());
    }
    return urls;
  }

  void RefreshFeeds() {
    std::vector<std::shared_ptr<FeedData>> feeds_to_process;
    {
      std::unique_lock<std::mutex> lock(m_mutex);
      feeds_to_process = m_feeds;
    }
    std::println("Processing {} feeds", feeds_to_process.size());
    for (auto& feed: feeds_to_process) {
      auto new_articles = feed->GetNewArticles();
      std::println("Found {} new articles in {}", new_articles.size(), feed->Url());
      for (const auto& article: new_articles) {
        std::string message = std::format("{} {}", article.title, article.link);
        m_bot->SendMessage(message, feed->Destination());
      }
      if (!new_articles.empty()) {
        m_kvstore->Put(feed->Url(), feed->ToJson());
      }
    }
  }

  static void RefreshThread(std::stop_token stop_token) {
    while (!stop_token.stop_requested()) {
      std::println("Refreshing feeds.");
      FeedCollection::Instance().RefreshFeeds();
      std::unique_lock<std::mutex> lock(FeedCollection::Instance().m_mutex);
      std::println("Waiting for next refresh. ");
      FeedCollection::Instance().m_cv.wait_for(lock, std::chrono::seconds(20),
                                               [&stop_token] { return stop_token.stop_requested(); });
    }
  }

  void UseBot(std::shared_ptr<DiscordBot> bot) { m_bot = bot; }
  void StartFeedThread() {
    // m_thread = std::make_unique<std::jthread>(RefreshThread);
  }

private:
  std::unique_ptr<KVStore> m_kvstore;
  std::vector<std::shared_ptr<FeedData>> m_feeds;
  std::mutex m_mutex;
  std::condition_variable m_cv;
  std::unique_ptr<std::jthread> m_thread;
  std::shared_ptr<DiscordBot> m_bot;
};

void InitializeFeedCollector(std::shared_ptr<DiscordBot> bot, const std::string& filename) {
  auto& feed_collector = FeedCollection::Instance();
  feed_collector.UseBot(bot);
  feed_collector.RestoreFeeds(filename);
  feed_collector.StartFeedThread();
}

RobotFeatureDescription RssAddFeature::Description() const {
  return RobotFeatureDescription{
      .moniker = "rssadd",
      .description = "Add an RSS feed to the bot.",
      .options = {
          {.type = dpp::co_string, .option_name = "url", .description = "The URL to add to the bot", .required = true},
          {.type = dpp::co_string,
           .option_name = "channel",
           .description = "The channel to post the feed to",
           .required = true}}};
}

void RssAddFeature::HandleCommand(const dpp::slashcommand_t& event) {
  auto url = std::get<std::string>(event.get_parameter("url"));
  auto channel = std::get<std::string>(event.get_parameter("channel"));

  std::println("Adding feed: {} to channel: {}", url, channel);
  if (FeedCollection::Instance().AddFeed(url, channel)) {
    event.reply("Feed added!");
  } else {
    event.reply("Feed already exists!");
  }
}

void RssAddFeature::Tick() {
  // Do nothing
}

RobotFeatureDescription RssDelFeature::Description() const {
  return RobotFeatureDescription{
      .moniker = "rssdel",
      .description = "Remove an RSS feed from the bot.",
      .options = {
          {.type = dpp::co_string, .option_name = "url", .description = "The URL of the feed", .required = true}}};
}

void RssDelFeature::HandleCommand(const dpp::slashcommand_t& event) {
  auto url = std::get<std::string>(event.get_parameter("url"));

  std::println("Removing feed: {}", url);
  if (FeedCollection::Instance().DelFeed(url)) {
    event.reply("Feed removed!");
  } else {
    event.reply("Feed not found!");
  }
}

void RssDelFeature::Tick() {
  // Do nothing
}

RobotFeatureDescription RssListFeature::Description() const {
  return RobotFeatureDescription{.moniker = "rsslist", .description = "List registered RSS feeds.", .options = {}};
}

std::vector<std::string> DumpList(const std::vector<std::string>& urls) {
  std::vector<std::string> result;
  int index = 1;
  result.push_back("");
  for (const auto& url: urls) {
    auto new_value = std::format("{}. {}\n", index++, url);
    if (result.back().size() + new_value.size() > 1999) {
      result.push_back("");
    }
    result.back() += new_value;
  }
  return result;
}

void RssListFeature::HandleCommand(const dpp::slashcommand_t& event) {
  auto urls = FeedCollection::Instance().ListFeeds();
  std::println("Listing feeds: {}", urls.size());
  auto replies = DumpList(urls);
  for (const auto& reply: replies) {
    event.reply(reply);
  }
};

void RssListFeature::Tick() {
  static int counter = 0;
  if (counter++ % 20 == 0) {
    FeedCollection::Instance().RefreshFeeds();
  }
}