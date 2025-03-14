#!/bin/bash

REPO="mxcoppell/tradestation-api-python"
echo "Fetching all issues (both open and closed) from $REPO..."

# Get all issues (both open and closed)
issues=$(gh issue list --repo $REPO --state all --limit 1000 --json number,title,state)

# Count total issues
count=$(echo $issues | jq '. | length')
echo "Found $count issues. Processing..."

# For each issue, delete it
for i in $(seq 0 $(($count - 1))); do
  number=$(echo $issues | jq -r ".[$i].number")
  title=$(echo $issues | jq -r ".[$i].title")
  state=$(echo $issues | jq -r ".[$i].state")
  
  echo "Processing #$number: $title (currently $state)"
  
  echo "Deleting issue #$number..."
  gh issue delete --repo $REPO $number --yes
  
  echo "Issue #$number deleted."
  
  # Add a small delay to avoid rate limiting
  sleep 0.5
done

echo "All issues deleted!" 