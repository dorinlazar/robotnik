add_library(
  roborssparser
  feed_parser.cpp
  feed_digest.hpp
  article.hpp
  expat_parser.hpp
  expat_parser.cpp
  feed_fetcher.cpp
  feed_fetcher.hpp
  time_converters.hpp
  time_converters.cpp)
target_link_libraries(roborssparser PUBLIC expat curl)
