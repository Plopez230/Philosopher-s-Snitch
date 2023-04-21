#!/bin/bash

# The path to the 'philosophers' executable
philosophers="../philo/philosophers"

${philosophers} $@ | python3 snitch.py $@

# Example with debug mode enabled
#   ${philosophers} $@ | python3 snitch.py debug $@