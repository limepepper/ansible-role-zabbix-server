#!/bin/bash

# {{ ansible_pkg_mgr }}

# me=$(basename -- "$(readlink -f -- "$0")")

me=`basename "$0"`

echo me is $me

cache=/var/cache/pkg-tools
mkdir -p ${cache}
cd ${cache}

_diff_file(){
  if [ $# -eq 0 ]; then
    echo "need the file to diff"
    exit 99
  fi
myfile=$1

{% if ansible_pkg_mgr == 'yum' %}

mypackage=$(rpm -q --whatprovides ${myfile})
echo looking at package ${mypackage}

echo rpm -V ${mypackage}
rpm -V ${mypackage}
changed=`rpm -V ${mypackage}| grep ${myfile}`
if [ $? -eq 0 ]; then
  echo "$changed"
else
  echo "not changed"
  exit 0
fi

echo ${mypackage}

mkdir -p ${cache}/${mypackage}
cd ${cache}/${mypackage}

#yumdownloader samba httpd --destdir /opt/downloaded_rpms --resolve
yumdownloader ${mypackage}

rpm2cpio ${mypackage}.rpm | cpio -idmv


echo colordiff -y ${myfile} ${cache}/${mypackage}/${myfile}
colordiff -y ${myfile} ${cache}/${mypackage}/${myfile}

{% elif ansible_pkg_mgr == 'dnf' %}



{% elif ansible_pkg_mgr == 'apt' %}

dpkg -S ${myfile}
mypackage=$(dpkg -S  ${myfile} | cut -d' ' -f1 | tr -d ':')

echo ${mypackage}

mkdir -p ${cache}/${mypackage}
cd ${cache}/${mypackage}

apt-get download ${mypackage}

ar vx ${mypackage}*.deb
tar xzf data.tar.gz
tar xzf control.tar.gz

echo colordiff -y ${myfile} ${cache}/${mypackage}/${myfile}
colordiff -y ${myfile} ${cache}/${mypackage}/${myfile}

# Using apt-file:

# apt-file search /usr/lib/tracker/tracker-store

# or also possible:

# apt-file search --regex /tracker-extract$
# apt-file search --regex /tracker-miner-fs$

{% else %}
echo some other tool
{% endif %}
}

#           _      _           _    __ _ _
#   ___ _ _(_)__ _(_)_ _  __ _| |  / _(_) |___
#  / _ \ '_| / _` | | ' \/ _` | | |  _| | / -_)
#  \___/_| |_\__, |_|_||_\__,_|_| |_| |_|_\___|
#            |___/

_original_file(){
  if [ $# -eq 0 ]; then
    echo "need the file to diff"
    exit 99
  fi
myfile=$1

{% if ansible_pkg_mgr == 'yum' %}

mypackage=$(rpm -q --whatprovides ${myfile})
echo looking at package ${mypackage}

echo rpm -V ${mypackage}
rpm -V ${mypackage}
changed=`rpm -V ${mypackage}| grep ${myfile}`
if [ $? -eq 0 ]; then
  echo "$changed"
else
  echo "not changed"
  exit 0
fi

echo ${mypackage}

mkdir -p ${cache}/${mypackage}
cd ${cache}/${mypackage}

#yumdownloader samba httpd --destdir /opt/downloaded_rpms --resolve
yumdownloader ${mypackage}

rpm2cpio ${mypackage}.rpm | cpio -idmv


# echo colordiff -y ${myfile} ${cache}/${mypackage}/${myfile}
cat ${cache}/${mypackage}/${myfile}

{% elif ansible_pkg_mgr == 'dnf' %}



{% elif ansible_pkg_mgr == 'apt' %}

dpkg -S ${myfile}
mypackage=$(dpkg -S  ${myfile} | cut -d' ' -f1 | tr -d ':')

echo ${mypackage}

mkdir -p ${cache}/${mypackage}
cd ${cache}/${mypackage}

apt-get download ${mypackage}

ar vx ${mypackage}*.deb
tar xzf data.tar.gz
tar xzf control.tar.gz

echo colordiff -y ${myfile} ${cache}/${mypackage}/${myfile}
colordiff -y ${myfile} ${cache}/${mypackage}/${myfile}

# Using apt-file:

# apt-file search /usr/lib/tracker/tracker-store

# or also possible:

# apt-file search --regex /tracker-extract$
# apt-file search --regex /tracker-miner-fs$

{% else %}
echo some other tool
{% endif %}
}

_provides_file(){
  if [ $# -eq 0 ]; then
    echo "need the file to diff"
    exit 99
  fi
  myfile=$1

{% if ansible_pkg_mgr == 'yum' %}

rpm -q --whatprovides $1

{% elif ansible_pkg_mgr == 'apt' %}

dpkg -S ${myfile}

{% else %}
echo some other tool
{% endif %}
}

# dpkg -S $1
# rpm -q --whatprovides $1




case "${me}" in
        pkg-diff-file)
            _diff_file "$@"
            ;;

        pkg-provides-file)
            _provides_file "$@"
            ;;

        pkg-original-file)
            _original_file "$@"
            ;;

        *)
            echo $"Usage: $0 {start|stop|restart|condrestart|status}"
            exit 1

esac


