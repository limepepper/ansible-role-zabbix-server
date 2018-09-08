#!/usr/bin/python
# -*- coding: utf-8 -*-


from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.module_utils import crypto as crypto_utils

# import sys
# import zabbix_helper
# #from zabbix_helper import ZabbixHelper
from ansible.module_utils.zabbix import ZabbixHelper, Trigger, Template

# print(repr(zabbix_helper))

# sys.modules["zabbix"].zabbix = ZabbixHelper

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


import copy
import random
import string

try:
    from zabbix_api import ZabbixAPI, ZabbixAPISubClass

    # Extend the ZabbixAPI
    # Since the zabbix-api python module too old (version 1.0, no higher version so far),
    # it does not support the 'hostinterface' api calls,
    # so we have to inherit the ZabbixAPI class to add 'hostinterface' support.
    class ZabbixAPIExtends(ZabbixAPI):
        hostinterface = None

        def __init__(self, server, timeout, user, passwd, validate_certs, **kwargs):
            ZabbixAPI.__init__(self, server, timeout=timeout, user=user,
                               passwd=passwd, validate_certs=validate_certs)
            self.hostinterface = ZabbixAPISubClass(
                self, dict({"prefix": "hostinterface"}, **kwargs))

    HAS_ZABBIX_API = True
except ImportError:
    HAS_ZABBIX_API = False

from ansible.module_utils.basic import AnsibleModule


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

            trigger_name=dict(type='str', required=True),
            template_name=dict(type='str', required=True),
            trigger_expression=dict(type='str', required=False, default=None),
            status=dict(default="enabled", choices=['enabled', 'disabled'])
        ),
        supports_check_mode=True
    )

    if not HAS_ZABBIX_API:
        module.fail_json(
            msg="Missing required zabbix-api module (check docs or install with: pip install zabbix-api)")

    server_url = module.params['server_url']
    login_user = module.params['login_user']
    login_password = module.params['login_password']
    http_login_user = module.params['http_login_user']
    http_login_password = module.params['http_login_password']
    validate_certs = module.params['validate_certs']
    timeout = module.params['timeout']

    trigger_name = module.params['trigger_name']
    template_name = module.params['template_name']
    trigger_expression = module.params['trigger_expression']
    status = module.params['status']

    # convert enabled to 0; disabled to 1
    status = 1 if status == "disabled" else 0

    zbx = None
    # login to zabbix
    try:
        zbx = ZabbixAPIExtends(server_url, timeout=timeout, user=http_login_user, passwd=http_login_password,
                               validate_certs=validate_certs)
        zbx.login(login_user, login_password)
    except Exception as e:
        module.fail_json(msg="Failed to connect to Zabbix server: %s" % e)

    result = {}
    template = Template(module, zbx)
    template_ids = template.get_template_ids([template_name])

    if not template_ids or len(template_ids) != 1:
        module.fail_json(msg="Unable to find template: %s (%s)" %
                         (template_name, len(template_ids)))

    module.warn("template ids: %s" % template_ids)

    trigger = Trigger(module, zbx)

    is_trigger_exist = trigger.is_trigger_exist(trigger_name, template_name)
    # is_trigger_exist = trigger.is_trigger_exist(trigger_name, template_name)

    module.warn("add params: %s" % len(is_trigger_exist))
    module.warn("add params: %s" % repr(is_trigger_exist))

    if is_trigger_exist:

        zabbix_trigger = trigger.update_trigger(
            is_trigger_exist[0]['triggerid']
        )

    #     result['trigger'] = is_trigger_exist
    #     result['changed'] = False
    #     # zabbix_host_obj = host.get_host_by_host_name(host_name)
    #     # host_id = zabbix_host_obj['hostid']

    else:

        zabbix_trigger = trigger.create_trigger()

        pass

    #   #result['user'] = user.is_user_exist(alias)
    #   user_id = user.add_user(alias, email, autologin, type, passwd, user_groups,
    #               status, timeout)
    #   # print(user_id)
    #   result['user'] = user_id
    #   result['changed'] = True

    module.exit_json(**result)


if __name__ == '__main__':
    main()
