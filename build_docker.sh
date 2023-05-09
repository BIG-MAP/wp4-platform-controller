#!/usr/bin/env bash

docker build -t nokal/wp4-platform-controller:$(poetry version -s) . 
