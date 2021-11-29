#!/bin/bash

coverage run --source=pdb2pqr -m pytest
coverage report -m | tee coverage.txt
coverage html
coverage xml
