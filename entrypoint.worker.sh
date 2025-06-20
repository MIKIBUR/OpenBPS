#!/bin/bash
set -e

# Create pbsuser if not exists
if ! id -u pbsuser >/dev/null 2>&1; then
    echo "Creating user pbsuser"
    useradd -m -s /bin/bash pbsuser
fi

USER_HOME=/home/pbsuser
SSH_DIR="$USER_HOME/.ssh"
KEY_FILE="$SSH_DIR/id_rsa"

# Ensure SSH directory exists
mkdir -p "$SSH_DIR"
chown -R pbsuser:pbsuser "$SSH_DIR"
chmod 700 "$SSH_DIR"

# Configure SSH to accept hosts' key automatically
cat > "$SSH_DIR/config" <<EOF
Host *
    StrictHostKeyChecking no
    UserKnownHostsFile=/dev/null
EOF

# Run postinstall if necessary
echo "Running PBS postinstall..."
/opt/pbs/libexec/pbs_postinstall
echo "reject_remote_stage = true" > /var/spool/pbs/mom_priv/config

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
