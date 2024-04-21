#pragma once
#include <string>
#include <ctime>

class FileFetcher {
public:
  explicit FileFetcher(const std::string& url, time_t last_modified = 0);

  time_t LastModified() const;
  std::string FetchFeed();

private:
  std::string m_url;
  time_t m_last_modified = 0;
};
