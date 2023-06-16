#!/bin/bash

# https://gist.github.com/marufshidiq/8bb457ae0bbf9e1d06873515b362cfcf

# set the directory for the backups
BACKUP_DIR="/home/ubuntu/mongodb_backup"

# create a directory based on the current date
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_PATH="$BACKUP_DIR/$DATE"
mkdir -p $BACKUP_PATH

echo $BACKUP_PATH

# create the mongodump
docker compose exec -T mongo mongodump --archive --gzip > $BACKUP_PATH/dump.gz

# # Remove old backups (older than 7 days)
# find $BACKUP_DIR/* -mtime +7 -exec rm -rf {} \;
