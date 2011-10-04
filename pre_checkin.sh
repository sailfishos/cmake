#!/bin/sh

sed -e 's,build_with_qt 0,build_with_qt 1,' cmake.spec > cmake-gui.spec
cp cmake.changes cmake-gui.changes

