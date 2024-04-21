#pragma once
#include <string>
#include <map>
#include <memory>

class XmlParser {
public:
  virtual ~XmlParser() = default;
  virtual bool StartElement(const std::string& name, const std::map<std::string, std::string>& attrs) = 0;
  virtual bool EndElement(const std::string& name) = 0;
  virtual bool CharacterData(const std::string& data) = 0;
};

class ExpatParser {
public:
  ExpatParser(std::shared_ptr<XmlParser> parser);
  void Parse(const std::string& data);

  void OnStartElement(const std::string& name, const std::map<std::string, std::string>& attrs) {
    m_parser->StartElement(name, attrs);
  }
  void OnEndElement(const std::string& name) { m_parser->EndElement(name); }
  void OnCharacterData(const std::string& data) { m_parser->CharacterData(data); }

private:
  std::shared_ptr<XmlParser> m_parser;
};
