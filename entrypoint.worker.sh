#!/bin/bash
set -e

# Run postinstall if necessary
if [ ! -f /var/spool/pbs/pbs_environment ]; then
  echo "Running PBS postinstall..."
  /opt/pbs/libexec/pbs_postinstall
fi

# Wait for PBS_SERVER env var (should be passed in docker-compose)
: "${PBS_SERVER:?Environment variable PBS_SERVER not set}"

# Add PBS server to /etc/hosts
echo "$(getent hosts $PBS_SERVER | awk '{ print $1 }') $PBS_SERVER" >> /etc/hosts

# Set PBS server name
echo "$PBS_SERVER" > /var/spool/pbs/server_name

# Source PBS environment
source /etc/profile.d/pbs.sh

# Wait a moment for networking
sleep 3

echo "[INFO] Starting PBS MOM on worker $(hostname)"
/opt/pbs/sbin/pbs_mom

# Keep the container alive
tail -f /var/spool/pbs/mom_logs/*
