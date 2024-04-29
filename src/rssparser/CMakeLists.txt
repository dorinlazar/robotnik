add_library(
  roborssparser
  article.hpp
  expat_parser.hpp
  expat_parser.cpp
  feed_data.cpp
  feed_data.hpp
  feed_digest.hpp
  feed_fetcher.cpp
  feed_fetcher.hpp
  feed_parser.cpp
  feed_parser.hpp
  time_converters.hpp
  time_converters.cpp)
target_link_libraries(roborssparser PUBLIC expat curl)

add_executable(
  roborssparser_test
  fetcher_test.cpp)
target_link_libraries(roborssparser_test PRIVATE roborssparser)