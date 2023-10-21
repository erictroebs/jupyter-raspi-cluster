FROM python:3.11

RUN apt-get update                                          \
 && apt-get install -y rustc cargo nodejs npm               \
 && pip install --no-cache-dir jupyterhub                   \
 && npm install -g configurable-http-proxy                  \
 && pip install --no-cache-dir dockerspawner                \
 && pip install --no-cache-dir jupyterhub-ltiauthenticator  \
 && pip install --no-cache-dir jupyterhub-idle-culler

CMD ["jupyterhub", "-f", "/etc/jupyterhub_config.py"]
