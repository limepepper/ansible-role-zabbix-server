
import json
import os
import urllib
import random
import string
from ansible.module_utils.urls import fetch_url
from ansible.module_utils._text import to_text
from ansible.module_utils.basic import env_fallback
from ansible.module_utils import crypto as crypto_utils

# in skeleton


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
    raise


class ZabbixApi2:
    def __init__(self,
                 server_url,
                 timeout,
                 http_user,
                 http_passwd,
                 validate_certs,
                 login_user,
                 login_password):

        self.login_user = login_user
        self.login_password = login_password
        self.warnings = []
        try:
            self._zapi = ZabbixAPIExtends(server_url, timeout,
                                          http_user,
                                          http_passwd,
                                          validate_certs)

            self._zapi.login(login_user, login_password)
        except Exception:
            raise
            # raise ValueError('A very specific bad thing happened')
            # # module.fail_json(msg="Failed to connect to Zabbix server: %s" % e)

    def get_apiinfo(self):
        """ not working, needs to be without auth """
        apiinfos = self._zapi.apiinfo.version([])

        return False, apiinfos, self.warnings

    #   _   _
    #  | | | |___ ___ _ _ ___
    #  | |_| (_-</ -_) '_(_-<
    #   \___//__/\___|_| /__/
    #

    def user_delete(self, alias):
        userids = self._zapi.user.get({'filter': {'alias': alias}})
        if len(userids) == 1:
            self._zapi.user.delete([int(userids[0]['userid'])])

        return True, None, self.warnings

    def user_create(self, user_args):
        self.warnings = []

        # if no passwd provided, generate a random long string
        if not 'passwd' in user_args or user_args['passwd'] is None:
            user_args['passwd'] = ''.join(random.choice(
                string.ascii_uppercase + string.digits) for _ in range(28))

        # if no groups provided, add the user to the Guests group
        if not 'user_groups' in user_args or not user_args['user_groups']:
            user_args['user_groups'] = ['Guests']

        grps = self._zapi.usergroup.get(
            {'filter': {'name': user_args['user_groups']}})
        grps = [dict(usrgrpid=i['usrgrpid'])
                for i in grps]

        # zbx_user = self.get_user_by_id(user)
        parameters = {'alias': user_args['alias'],
                      'passwd': user_args.get('passwd'),
                      'usrgrps': grps}
        self.warn("parameters are %s" % parameters)

        for k, v in user_args.items():
            if k in ['lang', 'name', 'surname', 'theme', 'url', 'autologin',
                     'autologout', 'refresh', 'rows_per_page', 'type']:
                parameters[k] = v
            elif k == 'email':
                parameters['user_medias'] = [
                    {
                        "mediatypeid": "1",
                        "sendto": v,
                        "active": 0,
                        "severity": 63,
                        "period": "1-7,00:00-24:00"
                    }
                ]

        user_list = self._zapi.user.create(parameters)

        self.warn("user list is %s" % user_list)
        if len(user_list) > 1:
            raise ValueError("more than 1 user created. (%s)" % user_list)

        user = self.get_user_by_id(user_list['userids'][0])
        # user = None
        return True, user, self.warnings

    def update_user(self, user, user_args):
        self.warnings = []

        if isinstance(user, (int)):
            user = self.get_user_by_id(user)

        updated = False
        for k, v in user_args.items():
            if k == 'passwd':
                updated = updated or self.update_user_passwd(
                    user['userid'], user_args)
            elif k in ['userid', 'alias']:
                pass  # can't change these values
            elif k in ['lang', 'name', 'surname', 'theme', 'url']:
                if user_args[k] != user[k]:   # compare string values
                    updated = updated or self.user_update_attribute(
                        user['userid'], k, v)
            elif k in ['autologin', 'autologout', 'refresh', 'rows_per_page', 'type']:
                if int(user_args[k]) != int(user[k]):   # compare string values
                    updated = updated or self.user_update_attribute(
                        user['userid'], k, v)
            elif k in ['enabled']:
                if v:
                    self.remove_userid_from_groupname(
                        user['userid'], 'Disabled')
                else:
                    self.add_userid_to_groupname(user['userid'], 'Disabled')
            elif k == 'email':
                updated = updated or self.user_update_media(
                    user['userid'], v)

        user = self.get_user_by_id(user['userid'])
        return updated, user, self.warnings

    def get_user_by_alias(self, alias):
        result = self._zapi.user.get({'filter': {'alias': alias}})
        return result[0] if len(result) == 1 else None

    def get_users(self):
        result = self._zapi.user.get({})
        return result[0] if len(result) == 1 else result

    def get_user_by_id(self, userid):
        result = self._zapi.user.get({'userids': userid})
        return result[0] if len(result) == 1 else None

    def update_user_passwd(self, userid, user_args):
        self._zapi.user.update(
            [{'userid': userid, 'passwd': user_args['passwd']}])
        # can't know whether passwd was updated
        return False

    def user_update_attribute(self, userid, key, val):
        self._zapi.user.update(
            [{'userid': userid, key: val}])
        return True

    #   __  __        _ _
    #  |  \/  |___ __| (_)__ _
    #  | |\/| / -_) _` | / _` |
    #  |_|  |_\___\__,_|_\__,_|
    #

    def get_mediatype_by_description(self, description):
        result = self._zapi.mediatype.get(
            {'filter': {'description': description}})
        return result[0] if len(result) == 1 else result

    def mediatype_update(self, mediatype, media_args):
        updated = False
        self.warn("mediatype: %s" % mediatype)
        self.warn("media_args: %s" % media_args)
        for k, v in media_args.items():
            self.warn("processing %s" % (k))
            if k in ['smtp_server', 'smtp_email', 'smtp_helo']:
                # print(mediatype)
                # print(media_args)
                # print(k)
                if media_args[k] != mediatype[k]:
                    self.warn("%s old val was %s, new val is %s, v is %s" %
                              (k, mediatype[k], media_args[k], v))
                    updated = self.mediatype_update_attribute(mediatype['mediatypeid'],
                                                              k, v) or updated
            elif k in ['smtp_port', 'smtp_security', 'smtp_verify_peer',
                       'smtp_verify_host']:
                if int(media_args[k]) != int(mediatype[k]):
                    self.warn("%s old val was %s, new val is %s, v is %s" %
                              (k, mediatype[k], media_args[k], v))
                    updated = self.mediatype_update_attribute(mediatype['mediatypeid'],
                                                              k, v) or updated
            elif k in ['smtp_authentication']:
                if int(media_args[k]) != int(mediatype[k]) or media_args['username'] != mediatype['username']:
                    updated = True
                self.mediatype_update_authentication(
                    mediatype['mediatypeid'],
                    v,
                    media_args['username'],
                    media_args['passwd'])

        mediatype = self.get_mediatype_by_description(
            mediatype['description'])
        return updated, mediatype, self.warnings

    def mediatype_update_attribute(self, id, key, val):
        self.warn("updating key: %s with value: %s for id %s" % (key, val, id))
        # try:
        ret1 = self._zapi.mediatype.update(
            {'mediatypeid': id, key: val})
        self.warn(repr(ret1))
        # except Exception as e:
        #     self.warn("updating failed with exception: %s" % e)
        return True

    def mediatype_update_authentication(self, id, auth, username, password):
        self.warn("updating auth key: %s  %s %s" %
                  (auth, username, password))
        try:
            self._zapi.mediatype.update(
                {'mediatypeid': id, 'smtp_authentication': auth,
                 'username': username, 'passwd': password})
        except Exception as e:
            self.warn("updating failed with exception: %s" % e)
        return False

    def user_update_media(self, userid, email):
        user = self._zapi.user.get(
            {'userids': userid, 'selectMedias': 'extend'})

        try:
            if len(user) == 1 and len(user[0]['medias']) == 1:
                medias = user[0]['medias'][0]
                if medias['sendto'] != email:
                    medias.pop('mediaid', None)
                    medias.pop('userid', None)
                    medias['sendto'] = email
                    self._zapi.user.updatemedia(dict(users=[{'userid': userid}],
                                                     medias=medias))
                else:
                    self.warn("media sendto == email (%s,%s)" %
                              (email, medias['sendto']))
        except Exception as e:
            self.warn("user with medias is %s : %s" % (medias, e))
            raise

        # self.warn("user with medias is %s" % user)
        # self._zapi.user.update(
        #     [{'userid': userid, 'passwd': user_args['passwd']}])
        # can't know whether passwd was updated
        return False

    def user_get_groups(self, userid):
        result = self._zapi.usergroup.get({'userids': [userid]})
        return result

    def remove_userid_from_groupname(self, userid, groupname):
        dis_grpid = self.get_group_by_groupname(groupname)
        if not dis_grpid:
            raise ValueError("The group doesn't exist (%s)" % groupname)
        grps = self.user_get_groups(userid)
        if not any(dis_grpid['usrgrpid'] == d['usrgrpid'] for d in grps):
            self.warn("userid %s not found in group %s" %
                      (userid, dis_grpid['name']))
            return False
        grps = [dict(usrgrpid=i['usrgrpid'])
                for i in grps if i['usrgrpid'] != dis_grpid['usrgrpid']]
        if len(grps) == 0:
            self.warn("Cannot remove user from all groups,"
                      " current groups (%s)" % [dict(name=i['name'])
                                                for i in grps])
            return False
        parameters = {'userid': userid,
                      'usrgrps': grps}
        self.warn("parameters is %s" % parameters)
        user_list = self._zapi.user.update(parameters)
        return True

    def add_userid_to_groupname(self, userid, groupname):
        grp = self.get_group_by_groupname(groupname)
        if not grp:
            raise ValueError("The group doesn't exist (%s)" % groupname)
        grps = self.user_get_groups(userid)
        if any(grp['usrgrpid'] == d['usrgrpid'] for d in grps):
            self.warn("userid %s is already found in group %s" %
                      (userid, grp['usrgrpid']))
            return False
        grps.append(grp)
        grps = [dict(usrgrpid=i['usrgrpid'])
                for i in grps]

        parameters = {'userid': userid,
                      'usrgrps': grps}
        self.warn("parameters is %s" % parameters)
        user_list = self._zapi.user.update(parameters)
        return True

    def get_group_by_groupname(self, groupname):
        result = self._zapi.usergroup.get({'filter': {'name': groupname}})
        return result[0]

    def warn(self, msg):
        self.warnings.append(msg)


class ZabbixBase:
    def __init__(self, module, zbx):
        pass


class User(ZabbixBase):
    def __init__(self, module, zbx):

        pass


class UserGroup(ZabbixBase):
    def __init__(self, module, zbx):

        pass


class Media(ZabbixBase):
    def __init__(self, module, zbx):

        pass
