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
            # these args are injected by zabbix_auth action plugin if setup
            server_url=dict(type='str', required=False, aliases=['url']),
            login_user=dict(type='str', required=True),
            login_password=dict(type='str', required=True, no_log=True),
            http_login_user=dict(type='str', required=False, default=None),
            http_login_password=dict(
                type='str', required=False, default=None, no_log=True),
            validate_certs=dict(type='bool', required=False, default=True),
            timeout=dict(type='int', default=10),

            name=dict(type='str', required=False),
            type=dict(type='str', required=False),
            state=dict(required=False, choices=[
                       'present', 'absent'], default="present"),
            smtp_server=dict(type='str', required=False),
            smtp_helo=dict(type='str', required=False),
            smtp_port=dict(type='str', required=False, default=25),
            from_address=dict(type='str', required=False),
            smtp_auth=dict(type='dict', required=False),
            enabled=dict(type='bool', default=None),
        ),
        supports_check_mode=True
    )

    # status = module.params['status']

    media_args = dict(
        smtp_server=module.params.get('smtp_server'),
        smtp_port=module.params.get('smtp_port'),
        smtp_email=module.params.get('from_address'),
        smtp_helo=module.params.get('smtp_helo'),
        from_address=module.params.get('from_address'),
        # name=module.params.get('name'),
        # type=module.params.get('type'),
    )

    smtp_auth = module.params.get('smtp_auth')
    if smtp_auth:
        if 'username' not in smtp_auth:
            module.fail_json(
                msg="(smtp_auth) username is required if smtp_auth key "
                "provided '%s'." % smtp_auth)
        else:
          media_args['username'] = smtp_auth.get('username')
        if 'password' not in smtp_auth:
            module.fail_json(
                msg="(smtp_auth) password is required if smtp_auth key "
                "provided '%s'." % smtp_auth)
        else:
          media_args['passwd'] = smtp_auth.get('password')
        media_args['smtp_authentication'] = 1


    module.warn("media_args is %s" % media_args)
    media_args = {k: v for k, v in media_args.items() if v is not None}
    module.warn("media_args is %s" % media_args)

    zbx = None
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

    zbx_media = zbx.get_mediatype_by_description(module.params['name'])

    module.warn("user is %s" % zbx_media)

    if zbx_media:
        if module.params['state'] == 'absent':
            # changed, user, warnings = zbx.user_delete(user_args['alias'])
            # result['changed'] = changed
            # result['user'] = user
            # result['warnings'] = warnings
            pass
        else:

            changed, user, warnings = zbx.mediatype_update(
                zbx_media, media_args)
            result['changed'] = changed
            result['user'] = user
            result['warnings'] = warnings
            # zabbix_host_obj = host.get_host_by_host_name(host_name)
            # host_id = zabbix_host_obj['hostid']

    # else:
    #     if module.params['state'] == 'absent':
    #         result['user'] = None
    #         module.exit_json(**result)

    #     if module.params['state'] == 'present':
    #         if not module.params.get('passwd'):
    #             module.warn("password will be generated, as none was provided")

        #result['user'] = user.is_user_exist(alias)
        # changed, user, warnings = zbx.user_create(user_args)
        # result['changed'] = changed
        # result['user'] = user
        # result['warnings'] = warnings

    module.exit_json(**result)


if __name__ == '__main__':
    main()
