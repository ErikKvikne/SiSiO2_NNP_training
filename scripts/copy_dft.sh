#!/bin/bash

# Define the remote login details
REMOTE_USER="ekvikne"
REMOTE_HOST="puhti.csc.fi"

# Ensure both remote and local paths are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <remote_full_path> <local_destination>"
    echo "Example: $0 /scratch/jeakola/ekvikne/deepmd/test_run /path/to/local/destination/"
    exit 1
fi

# Assign input arguments
REMOTE_PATH="$1"
LOCAL_DESTINATION="$2"

# Perform rsync with exclusions
rsync -av --progress --exclude="*.wfn" --exclude="*.wfn.bak-*" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH" "$LOCAL_DESTINATION"

echo "✅ Sync complete: $REMOTE_PATH -> $LOCAL_DESTINATION"
