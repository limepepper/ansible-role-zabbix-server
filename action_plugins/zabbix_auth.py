


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash


class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):

        result = super(ActionModule, self).run(tmp, task_vars)

        args = self._task.args.copy()

        facts = dict()

        if not result.get('skipped'):

            # FUTURE: better to let _execute_module calculate this internally?
            wrap_async = self._task.async_val and not self._connection.has_native_async

            # do work!
            result = merge_hash(result, self._execute_module(task_vars=args,
                wrap_async=wrap_async))

        print(result)


        # if "zabbix_server_auth" in task_vars:
        facts['zabbix_login_user'] = args.get('login_user')
        facts['zabbix_login_password'] = args.get('login_password')
        facts['zabbix_server_url'] = args.get('server_url')

        result['ansible_facts'] = facts

        return result
