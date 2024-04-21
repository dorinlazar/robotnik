add_library(roborssparser feed_parser.cpp feed_digest.hpp article.hpp expat_parser.hpp expat_parser.cpp)
target_link_libraries(roborssparser PUBLIC expat)
