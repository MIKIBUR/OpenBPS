#!/bin/bash
set -e

# Run PBS postinstall once
mkdir -p /var/spool/pbs
echo "Running PBS postinstall..."
/opt/pbs/libexec/pbs_postinstall

# Get container IP and update /etc/hosts for 'openpbs'
CONTAINER_IP=$(hostname -I | awk '{print $1}')
grep -v 'openpbs' /etc/hosts > /tmp/hosts
echo "$CONTAINER_IP openpbs" >> /tmp/hosts
cat /tmp/hosts > /etc/hosts

# Set PBS server name and env var
echo "openpbs" > /var/spool/pbs/server_name
export PBS_SERVER=openpbs
echo "PBS_SERVER=openpbs" >> /etc/environment

# Source PBS environment variables
source /etc/profile.d/pbs.sh

# Wait for network to settle
sleep 3

# Create pbsuser if not exists
if ! id -u pbsuser >/dev/null 2>&1; then
    echo "Creating user pbsuser"
    useradd -m -s /bin/bash pbsuser
fi

# Ensure mounted project directory exists and is owned by pbsuser
mkdir -p /home/pbsuser/project
chown -R pbsuser:pbsuser /home/pbsuser/project

# Start PBS service
/etc/init.d/pbs start

# Add nodes if missing
add_node_if_missing() {
  NODE_NAME=$1
  if ! qmgr -c "list node $NODE_NAME" &>/dev/null; then
    echo "Adding node $NODE_NAME"
    qmgr -c "create node $NODE_NAME"
  else
    echo "Node $NODE_NAME already exists"
  fi
}

add_node_if_missing worker1
add_node_if_missing worker2

pbsnodes -a

# Tail logs to keep container running
tail -f /var/spool/pbs/server_logs/* || true
