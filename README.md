# jupyter-raspi-cluster

## Setup
- 8 Raspberry Pis (1x 3B, 7x 2B)
- IP range from `172.31.255.1` to `172.31.255.8`


## Setup First Node

### IP forwarding

Enable forwarding in `/etc/sysctl.conf`:

```
net.ipv4.ip_forward=1
```

Set iptables rule:

```bash
iptables -t nat -A POSTROUTING --src 172.31.255.0/24 -j MASQUERADE
```

### NFS Server

Install:

```bash
apt install -y nfs-kernel-server
```

Create folder:

```bash
mkdir -p /srv/homes
```

Add to `/etc/exports`:

```
/srv        172.31.255.0/24(rw,sync,no_subtree_check,root_squash,fsid=root)
/srv/homes  172.31.255.0/24(rw,sync,no_subtree_check,root_squash)
```


## Advanced Settings (on every single Pi)
Append to `/boot/config.txt`:

```
gpu_mem=16
```

Append to `/boot/cmdline.txt`:

```
cgroup_enable=memory swapaccount=1 cgroup_memory=1 cgroup_enable=cpuset
```


## Docker Installation (on every single Pi)

```bash
apt update
apt full-upgrade -y
apt install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/raspbian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg
```

```bash
echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/raspbian "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
```

```bash
apt update
apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### On First Node

Initialize swarm:

```bash
docker swarm init --advertise-addr 172.31.255.1
```

Note the shown command!

### On Every Other Node

Join swarm:

```bash
docker swarm join --token <verylongtoken> 172.31.255.1:2377
```

Add iptables rules:

```bash
./iptables-rules.sh
```


## Setup JupyterHub (on first node)

```bash
cd jupyterhub/
```

Edit `docker-compose.yml` according to your needs. Start services afterwards:

```bash
docker compose up -d
```
