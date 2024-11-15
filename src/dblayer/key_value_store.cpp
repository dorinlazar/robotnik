#include "key_value_store.hpp"
#include <gdbm.h>
#include <exception>
#include <print>

KVStore::KVStore(const std::string& filename) : m_filename(filename) {}

void KVStore::Put(const std::string& key, const std::string& value) {
  std::lock_guard<std::mutex> lock(m_mutex);
  GDBM_FILE db = gdbm_open(m_filename.c_str(), 0, GDBM_WRCREAT, 0666, nullptr);
  if (!db) {
    std::println("Unable to open GDBM file: {}", m_filename);
    throw std::runtime_error("Unable to open GDBM file");
  }
  datum k, v;
  k.dptr = const_cast<char*>(key.c_str());
  k.dsize = key.size();
  v.dptr = const_cast<char*>(value.c_str());
  v.dsize = value.size();
  gdbm_store(db, k, v, GDBM_REPLACE);
  gdbm_close(db);
}

std::vector<KVItem> KVStore::GetAll() {
  std::lock_guard<std::mutex> lock(m_mutex);
  std::vector<KVItem> items;
  GDBM_FILE db = gdbm_open(m_filename.c_str(), 0, GDBM_READER, 0666, nullptr);
  if (!db) {
    return {};
  }
  datum k = gdbm_firstkey(db);
  while (k.dptr) {
    KVItem item;
    item.key = std::string(k.dptr, k.dsize);
    datum v = gdbm_fetch(db, k);
    item.value = std::string(v.dptr, v.dsize);
    items.push_back(item);
    k = gdbm_nextkey(db, k);
  }
  gdbm_close(db);
  return items;
}

void KVStore::Remove(const std::string& key) {
  std::lock_guard<std::mutex> lock(m_mutex);
  GDBM_FILE db = gdbm_open(m_filename.c_str(), 0, GDBM_WRITER, 0666, nullptr);
  datum k;
  k.dptr = const_cast<char*>(key.c_str());
  k.dsize = key.size();
  gdbm_delete(db, k);
  gdbm_close(db);
}
