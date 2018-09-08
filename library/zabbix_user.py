#!/usr/bin/python
# -*- coding: utf-8 -*-


from __future__ import absolute_import, division, print_function
__metaclass__ = type
from ansible.module_utils import crypto as crypto_utils


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


import copy
import random
import string


from ansible.module_utils.basic import AnsibleModule

from ansible.module_utils.zabbix2 import ZabbixApi2, User, UserGroup, Media


def main():
    module = AnsibleModule(
        argument_spec=dict(
            server_url=dict(type='str', required=True, aliases=['url']),
            login_user=dict(type='str', required=True),
            login_password=dict(type='str', required=True, no_log=True),
            http_login_user=dict(type='str', required=False, default=None),
            http_login_password=dict(
                type='str', required=False, default=None, no_log=True),
            validate_certs=dict(type='bool', required=False, default=True),
            timeout=dict(type='int', default=10),

            state=dict(required=False, choices=[
                       'present', 'absent'], default="present"),
            userid=dict(type='str', required=False),
            alias=dict(type='str', required=True),
            email=dict(type='str', required=False),
            autologin=dict(type='bool', required=False),
            name=dict(type='str', required=False),
            surname=dict(type='str', required=False),
            type=dict(type='int', required=False),
            passwd=dict(type='str', required=False, default=None, no_log=True),
            user_groups=dict(type='list', required=False),
            user_groups_append=dict(type='bool', default=True),
            enabled=dict(type='bool', default=None),
            status=dict(default="enabled", choices=['enabled', 'disabled'])
        ),
        supports_check_mode=True
    )


    # userid = module.params['userid']
    # alias = module.params['alias']
    # email = module.params['email']
    # autologin = module.params['autologin']
    # name = module.params['name']
    # surname = module.params['surname']
    # type = module.params['type']
    # passwd = module.params['passwd']
    # user_groups = module.params['user_groups']
    status = module.params['status']

    user_args = dict(
        alias=module.params.get('alias'),
        email=module.params.get('email'),
        autologin=module.params.get('autologin'),
        name=module.params.get('name'),
        type=module.params.get('type'),
        user_groups=module.params.get('user_groups'),
        passwd=module.params.get('passwd'),
        enabled=module.params.get('enabled'),
    )
    module.warn("user_args is %s" % user_args)

    # user_args = {k: v for k, v in user_args.items() if v is not None}
    user_args = dict((k, user_args[k])
                     for k in user_args if user_args[k] is not None)
    module.warn("user_args is %s" % user_args)


    # convert enabled to 0; disabled to 1
    status = 1 if status == "disabled" else 0

    zbx = None
    # login to zabbix
    try:
        zbx = ZabbixApi2(module.params['server_url'],
                         module.params['timeout'],
                         module.params['http_login_user'],
                         module.params['http_login_password'],
                         module.params['validate_certs'],
                         module.params['login_user'],
                         module.params['login_password']
                         )
    except Exception as e:
        module.fail_json(msg="Failed to connect to Zabbix server: %s" % e)

    result = {
        'changed': False
    }

    zbx_user = zbx.get_user_by_alias(module.params['alias'])

    module.warn("user is %s" % zbx_user)

    if zbx_user:
        if module.params['state'] == 'absent':
          changed, user, warnings = zbx.user_delete(user_args['alias'])
          result['changed'] = changed
          result['user'] = user
          result['warnings'] = warnings
        else:

          changed, user, warnings = zbx.update_user(zbx_user, user_args)
          result['changed'] = changed
          result['user'] = user
          result['warnings'] = warnings
          # zabbix_host_obj = host.get_host_by_host_name(host_name)
          # host_id = zabbix_host_obj['hostid']

    else:
        if module.params['state'] == 'absent':
            result['user'] = None
            module.exit_json(**result)

        if module.params['state'] == 'present':
            if not module.params.get('passwd'):
               module.warn("password will be generated, as none was provided")


        #result['user'] = user.is_user_exist(alias)
        changed, user, warnings = zbx.user_create(user_args)
        result['changed'] = changed
        result['user'] = user
        result['warnings'] = warnings

    module.exit_json(**result)


if __name__ == '__main__':
    main()
