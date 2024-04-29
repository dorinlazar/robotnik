#include "feed_fetcher.hpp"
#include "time_converters.hpp"

#include <curl/curl.h>
#include <map>
#include <optional>

class CurlLibrary {
private:
  CurlLibrary() { curl_global_init(CURL_GLOBAL_ALL); }
  ~CurlLibrary() { curl_global_cleanup(); }

  static size_t WriteCallback(void* contents, size_t size, size_t nmemb, void* userp) {
    size_t realsize = size * nmemb;
    ((std::string*)userp)->append((char*)contents, realsize);
    return realsize;
  }

public:
  static CurlLibrary& GetInstance() {
    static CurlLibrary instance;
    return instance;
  }

  std::optional<std::string> FetchFile(const std::string& url, std::map<std::string, std::string> headers) {
    std::string result;
    CURL* curl = curl_easy_init();
    if (curl) {
      curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
      struct curl_slist* chunk = nullptr;
      for (const auto& [key, value]: headers) {
        chunk = curl_slist_append(chunk, (key + ": " + value).c_str());
      }
      curl_easy_setopt(curl, CURLOPT_HTTPHEADER, chunk);
      curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, WriteCallback);
      curl_easy_setopt(curl, CURLOPT_WRITEDATA, &result);
      curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
      auto res = curl_easy_perform(curl);
      curl_easy_cleanup(curl);
    }
    return result;
  }
};

FileFetcher::FileFetcher(const std::string& url, time_t last_modified) : m_url(url), m_last_modified(last_modified) {}

time_t FileFetcher::LastModified() const { return m_last_modified; }

std::string FileFetcher::FetchFeed() {
  std::map<std::string, std::string> headers;
  if (m_last_modified != 0) {
    headers["If-Modified-Since"] = ConvertTimeStampToRfc822(m_last_modified);
  }
  time_t request_time = time(nullptr);
  auto result = CurlLibrary::GetInstance().FetchFile(m_url, headers);
  if (result) {
    m_last_modified = request_time;
    return *result;
  }
  return "";
}
