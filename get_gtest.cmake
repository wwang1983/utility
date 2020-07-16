include(FetchContent)

FetchContent_Declare(
    gtest
    GIT_REPOSITORY    https://github.com/google/googletest
    GIT_TAG           release-1.10.0
)
set(FETCHCONTENT_QUIET OFF)
FetchContent_MakeAvailable(gtest)