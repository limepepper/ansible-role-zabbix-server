#!/bin/bash

# {{ ansible_pkg_mgr }}

# me=$(basename -- "$(readlink -f -- "$0")")

me=`basename "$0"`


case "${me}" in
        pkg-diff-file)
            pkg-diff-file
            ;;

        pkg-provides-file)
            pkg-provides-file
            ;;

        *)
            echo $"Usage: $0 {start|stop|restart|condrestart|status}"
            exit 1

esac

pkg-diff-file(){
{% if ansible_pkg_mgr == 'yum' %}

rpm -q --whatprovides $1

{% elif ansible_pkg_mgr == 'apt' %}

apt-file list $1

# % dpkg -S /usr/lib/tracker/tracker-store
# tracker: /usr/lib/tracker/tracker-store

# Using apt-file:

# apt-file search /usr/lib/tracker/tracker-store

# or also possible:

# apt-file search --regex /tracker-extract$
# apt-file search --regex /tracker-miner-fs$


{% else %}

echo some other tool


{% endif %}
}
