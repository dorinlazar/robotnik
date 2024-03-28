add_library(roborssparser rss_parser.cpp feed_digest.hpp article.hpp)
target_link_libraries(roborssparser PUBLIC expatpp)
