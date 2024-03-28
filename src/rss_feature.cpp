#include <expatpp.h>

class MyXmlParser : public expatpp {
public:
  MyXmlParser() : expatpp(false) {}

  void startElement(const XML_Char* name, const XML_Char** atts) override {}

  void endElement(const XML_Char* name) override {}

  void charData(const XML_Char* s, int len) override {}
};

int function() {
  MyXmlParser parser;
  if (!parser.parseString("<input/>")) {
    return 1;
  }

  return 0;
}