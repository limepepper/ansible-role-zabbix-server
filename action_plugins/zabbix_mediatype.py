

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash


class ActionModule(ActionBase):

    def run(self, tmp=None, task_vars=None):

        result = super(ActionModule, self).run(tmp, task_vars)

        args = self._task.args.copy()

        if not args.get('login_user'):
          args['login_user'] = task_vars.get('zabbix_login_user')

        if not args.get('login_password'):
          args['login_password'] = task_vars.get('zabbix_login_password')

        if not args.get('server_url'):
          args['server_url'] = task_vars.get('zabbix_server_url')

        if not result.get('skipped'):

            # FUTURE: better to let _execute_module calculate this internally?
            wrap_async = self._task.async_val and not self._connection.has_native_async

            # do work!
            result = merge_hash(result,
                                self._execute_module(task_vars=args,
                                                     module_args=args,                wrap_async=wrap_async))

        return result
