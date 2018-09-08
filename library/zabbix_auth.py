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
            login_password=dict(type='str', required=True),
            http_login_user=dict(type='str', required=False, default=None),
            http_login_password=dict(type='str', required=False, default=None),
            validate_certs=dict(type='bool', required=False, default=True),
            timeout=dict(type='int', default=10)
        ),
        supports_check_mode=True
    )

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

    result = {}

    data= zbx.get_users()

    result = dict(
        warnings=zbx.warnings,
        changed=False,
        api=data,
        msg="successully cached credentials"
    )

    module.exit_json(**result)


if __name__ == '__main__':
    main()
