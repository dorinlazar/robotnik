#pragma once
#include <string>
#include <map>
#include <memory>

class XmlParser {
public:
  virtual ~XmlParser() = default;
  virtual void StartElement(const std::string& name, const std::map<std::string, std::string>& attrs) = 0;
  virtual void EndElement(const std::string& name) = 0;
  virtual void CharacterData(const std::string& data) = 0;
};

class ExpatParser {
public:
  ExpatParser(std::shared_ptr<XmlParser> parser);
  void Parse(const std::string& data);
};
