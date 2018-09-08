Role Name
=========

A role to help with installing zabbix server, and to provide modules for
managing users, groups and hosts in Zabbix

Example Playbook
----------------

If you just want to manage users (or problem notifications) on an existing
zabbix installation, you can do a basic role import, and then use the
`zabbix_user` module in your own roles/playbooks like so;

```yml

tasks:
  - import_role:
      name: limepepper.zabbix-server

  - name: create a zabbix user, set password, add email notifications
    zabbix_user:
      login_user: Admin
      login_password: "{{ zabbix_web_admin_pass }}"
      server_url: http://localhost/zabbix
      alias: "new_user_1"
      enabled: yes
      passwd: xxxxxxx
      email: xfexxx@example.com
      name: Marty
      surname: McFly

```
In the previous example, the user would be configured to receive all problem
report notifications

If you want to install, and configure zabbix on the server, you can tell ansible
to install the server side components.  Currently this role only supports the
mysql and apache options. (postgresql and nginx are on the todo list)

Zabbix with a mysql backend depends on
a running mysql and apache services, so something like this should build the
whole thing;

```yml

tasks:
  - include_role:
      name: limepepper.mysql

  - include_role:
      name: limepepper.apache

  - import_role:
      name: limepepper.zabbix-server
    vars:
      zabbix_server_components:
        - zabbix-server-mysql
        - zabbix-web

```

or you can use the classic role import syntax, which is slightly less verbose;

```yml
- hosts: zabbix
  roles:
    - limepepper.mysql
    - limepepper.apache
    - limepepper.zabbix-server
  vars:
    zabbix_server_components:
      - zabbix-server-mysql
      - zabbix-web
    # use a more recent version of mysql
    mysql_profile: mysql_community_server_5_7

```

To successfully send email notifications, zabbix needs to know how to send email
via SMTP. You can configure those with the `zabbix_mediatype` and `zabbix_user`
modules like so;

```yml

- hosts: zabbix
  roles:
    - limepepper.mysql
    - limepepper.apache
    - limepepper.zabbix-server
  vars:
    # set the main super admin password, also used for api access
    zabbix_web_admin_pass: some_complex_password
    # install mysql backend, and web components
    zabbix_server_components:
      - zabbix-server-mysql
      - zabbix-web

  tasks:
    - name: create a zabbix user with an email for notifications
      zabbix_user:
        # zabbix api login details
        login_user: Admin
        login_password: "{{ zabbix_web_admin_pass }}"
        server_url: http://localhost/zabbix
        # module args
        alias: "my_zabbix_user"
        passwd: my_zabbix_password
        email: xfexxx@example.com

    - name: setup SMTP for the default Email media type
      zabbix_media:
        # zabbix api login details
        login_user: Admin
        login_password: "{{ zabbix_web_admin_pass }}"
        server_url: http://localhost/zabbix
        # module args
        name: Email
        smtp_server: smtp.google.com
        smtp_server_port: 25
        from_address: zabbix@somedomain.com
        auth:
          username: my_smtp_login
          password: my_smtp_password

```

License
-------

BSD

Author Information
------------------

An optional section for the role authors to include contact information, or a
website (HTML is not allowed).
