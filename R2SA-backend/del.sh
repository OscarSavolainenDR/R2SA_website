#!/bin/bash

# Number of times to run the command
num_iterations=100

for ((i = 1; i <= num_iterations; i++)); do
    # Check if the file exists before removing it
    if [ -e backend_v3/.env ]; then
        rm backend_v3/.env
    fi

    if [ -e del.sh]; then
        rm del.sh
    fi

    git add .
    git commit --amend --no-edit
    git rebase --continue

    # Wait for some time (you can adjust the sleep duration as needed)
    sleep 1
done
