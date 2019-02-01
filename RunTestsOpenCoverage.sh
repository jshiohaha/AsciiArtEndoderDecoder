#!/bin/bash
filename="AsciiTransformTests.py"
if [ $# -gt 0 ]
  then
    srcdir = "src/"
    coverage run --source $srcdir "tests/$filename"
    if [ $1 == "report" ]
    then
      coverage report -m # prints to console
    elif [ $1 == "html" ]
    then
      coverage html # this will create a dir named htmlcov/ which contains html coverage data
      open htmlcov/index.html
    fi
else
  python "tests/$filename"       
fi