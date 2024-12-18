#!/bin/bash

sudo dnf groupinstall -y "Development Tools"
sudo dnf install -y clang-tools-extra clang gcc-g++ ninja-build fmt-devel gtest-devel gmock-devel openssl-devel \
                    cppcheck valgrind lcov python3-devel pip cmake cli11-devel yaml-cpp-devel curl-devel expat-devel \
                    gdbm-devel nlohmann-json-devel systemd-devel zlib-ng-compat-static
pip install CodeChecker cmake-format
git submodule update --init --recursive
