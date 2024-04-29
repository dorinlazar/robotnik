#pragma once

#include <string>
#include <vector>

struct KVItem {
  std::string key;
  std::string value;
};

class KVStore {
public:
  KVStore(const std::string& filename);
  ~KVStore() = default;

  void Put(const std::string& key, const std::string& value);
  std::vector<KVItem> GetAll();
  void Remove(const std::string& key);

private:
  const std::string& m_filename;
};
