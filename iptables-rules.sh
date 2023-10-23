#!/usr/bin/env bash

# clear rules
/usr/sbin/iptables -F DOCKER-USER

# allow dns
/usr/sbin/iptables -A DOCKER-USER -p udp --sport 53  -j ACCEPT
/usr/sbin/iptables -A DOCKER-USER -p udp --dport 53  -j ACCEPT

# allow https
/usr/sbin/iptables -A DOCKER-USER -p tcp -d 141.24.212.82 --dport 443                                      -j ACCEPT
/usr/sbin/iptables -A DOCKER-USER -p tcp -s 141.24.212.82 --sport 443 -m state --state RELATED,ESTABLISHED -j ACCEPT

# deny others
/usr/sbin/iptables -A DOCKER-USER -j REJECT
