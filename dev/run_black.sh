#!/bin/bash

find . -name \*.py -not -path "./venv/*" -exec black {} \;