import os
import re
import sys
from pathlib import Path
from hashlib import md5


# Configuration file for jupyterhub.
c = get_config()  # noqa

# log level
c.JupyterHub.log_level = 'DEBUG'
c.SwarmSpawner.debug = True

# activate dummy authenticator
c.JupyterHub.authenticator_class = 'dummy'

# network configuration according to docker-compose.yml
c.JupyterHub.hub_ip = '0.0.0.0'

# cleanup servers on restart (?)
c.JupyterHub.cleanup_servers = True

##################################################
# SwarmSpawner                                   #
##################################################
c.JupyterHub.spawner_class = 'dockerspawner.SwarmSpawner'

# timeouts
c.SwarmSpawner.http_timeout = 60
c.SwarmSpawner.start_timeout = 300

# allowed images
c.SwarmSpawner.allowed_images = {
    'Datenbanksysteme':  'jupyter-duckdb',
    'SWI Prolog':        'jupyter-swi-prolog',
}

# always pull the newest image version (default: skip)
#c.SwarmSpawner.pull_policy = 'always'

# only spawn user environments on workers
c.SwarmSpawner.extra_placement_spec = {
    'constraints': ['node.role == worker']
}

# network settings
network_name = os.environ['DOCKER_NETWORK_NAME']

c.SwarmSpawner.network_name = network_name
c.SwarmSpawner.extra_host_config = {
    'network_mode': network_name
}

# memory limit
# c.SwarmSpawner.mem_limit = '384M'

c.SwarmSpawner.extra_host_config = {
    'mem_limit': '384M'
}

c.SwarmSpawner.environment = {
    'MEM_LIMIT': str(384 * 1024 * 1024)
}

# persistence options
work_dir = '/home/jovyan/work'

def pre_spawn_hook(spawner):
    clear_name = re.sub(r'[^A-Za-z0-9]', '', spawner.user.name)
    clear_hash = md5(spawner.user.name.encode('utf-8')).hexdigest()
    username = f'{clear_name} {clear_hash}'

    home = Path(f'/srv/homes/{username}')
    if not home.exists():
        home.mkdir()
        os.chown(str(home), 1000, 100)

    spawner.extra_container_spec = {
        'mounts': [{
            'type': 'volume',
            'target': work_dir,
            'VolumeOptions': {
                'nocopy': True,
                'DriverConfig': {
                    'name': 'local',
                    'options': {
                        'type': 'nfs',
                        'o': 'addr=127.0.0.1,nfsvers=4',
                        'device': f':/homes/{username}'  # no prefix for nfs mounts!!
                    }
                }
            }
        }]
    }

c.Spawner.pre_spawn_hook = pre_spawn_hook
c.SwarmSpawner.notebook_dir = work_dir

# culling
c.JupyterHub.load_roles = [{
    "name": "jupyterhub-idle-culler-role",
    "scopes": [
        "list:users",
        "read:users:activity",
        "read:servers",
        "delete:servers",
        # "admin:users", # if using --cull-users
    ],
    # assignment of role's permissions to:
    "services": ["jupyterhub-idle-culler-service"],
}]

c.JupyterHub.services = [{
    "name": "jupyterhub-idle-culler-service",
    "command": [
        sys.executable,
        "-m", "jupyterhub_idle_culler",
        "--timeout=1200",
    ],
    # "admin": True,
}]
