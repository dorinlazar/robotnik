#include "feed_data.hpp"

#include <print>

int main(int argc, char** argv) {
  std::string site_feed = "https://dorinlazar.ro/index.xml";
  if (argc == 2) {
    site_feed = argv[1];
  }
  FeedData parser(site_feed, "{}");
  int index = 0;
  for (const auto& article: parser.GetNewArticles()) {
    index++;
    std::println("{:02d}. Title: {} published on {} at {}", index, article.title, article.pub_date, article.link);
  }

  return 0;
}
