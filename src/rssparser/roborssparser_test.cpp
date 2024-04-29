#include "feed_data.hpp"

#include <print>

int main() {
  FeedData parser("https://dorinlazar.ro/index.xml");
  parser.GetNewArticles();
  int index = 0;
  for (const auto& article: parser.GetNewArticles()) {
    index++;
    std::println("{:02d}. Title: {} published on {} at {}", index, article.title, article.pub_date, article.link);
  }

  return 0;
}