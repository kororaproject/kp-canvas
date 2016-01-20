#!/bin/bash

find test/ -name test_*.py | while read F
do
  echo "Executing test: $F"
  PYTHONPATH='./lib' python3 $F
  echo
done
