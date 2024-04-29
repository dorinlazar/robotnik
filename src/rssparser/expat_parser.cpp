#include "expat_parser.hpp"
#include <print>
#include <expat.h>

ExpatParser::ExpatParser(std::shared_ptr<XmlParser> parser) : m_parser(parser) {}

void StartElementHandler(void* userData, const XML_Char* name, const XML_Char** attrs) {
  ExpatParser* parser = static_cast<ExpatParser*>(userData);
  std::map<std::string, std::string> attributes;
  for (int i = 0; attrs[i]; i += 2) {
    attributes[attrs[i]] = attrs[i + 1];
  }
  parser->OnStartElement(name, attributes);
}

void EndElementHandler(void* userData, const XML_Char* name) {
  ExpatParser* parser = static_cast<ExpatParser*>(userData);
  parser->OnEndElement(name);
}

void CharacterDataHandler(void* userData, const XML_Char* s, int len) {
  ExpatParser* parser = static_cast<ExpatParser*>(userData);
  parser->OnCharacterData(std::string(s, len));
}

void ExpatParser::Parse(const std::string& data) {
  using XmlParserPtr = std::unique_ptr<XML_ParserStruct, decltype(XML_ParserFree)*>;

  XmlParserPtr parser_ptr(XML_ParserCreate(nullptr), XML_ParserFree);
  auto parser = parser_ptr.get();
  XML_SetUserData(parser, this);
  XML_SetElementHandler(parser, StartElementHandler, EndElementHandler);
  XML_SetCharacterDataHandler(parser, CharacterDataHandler);

  if (XML_Parse(parser, data.c_str(), data.length(), true) == XML_STATUS_ERROR) {
    // Handle parsing error
    const XML_Error code = XML_GetErrorCode(parser);
    const std::string error = XML_ErrorString(code);
    std::println("An error encountered while parsing data: {}", error);
    std::println("Erroneous data: {}", data);
  }
}
