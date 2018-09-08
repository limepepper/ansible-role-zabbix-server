#!/usr/bin/python
# -*- coding: utf-8 -*-

__author__ = 'testy mctestface'

from ansible.errors import AnsibleError

import re
import os.path
from six import string_types
import datetime
from urlparse import urlparse

# http://www.dasblinkenlichten.com/creating-ansible-filter-plugins/


class FilterModule(object):
    def filters(self):
        return {
            'check_complex': self.check_complexity,
            'date_now': self.date_now,
            'fixup_file_list': self.fixup_file_list,
            'fix_sites': self.fix_sites,
            'modify_list': modify_list,
            'append_to_list': append_to_list,
            'filter_reserved': filter_reserved,
            'array_to_str': array_to_str,
            'extract_role_users': extract_role_users,
            'remove_reserved': remove_reserved,
            'filename': filename,
            'create_sitename': create_sitename,
            'strip_fieldattributes': strip_fieldattributes,
            'buildCombo': buildCombo,
            "parse_url": parse_url
        }

    def check_complexity(self, a_variable):
        """check the passed string matches alphanumeric complexity"""
        if (
                re.search('[0-9]', a_variable) and
                re.search('[a-z]', a_variable) and
                re.search('[A-Z]', a_variable) and
                re.search('[^0-9a-zA-Z]', a_variable)):

            # print("found PUNC AND UPPER AND LOWER AND DIGIT")
            return "found PUNC AND UPPER AND LOWER AND DIGIT"
        else:
            return "bad string was {}".format(a_variable)

    def date_now(self, arg=""):
        return datetime.datetime.utcnow()

    def fixup_file_list(self, paths=[], prepath=''):
        tmps = []
        for path in paths:
            try:
                if isinstance(path, dict):
                    tmps.append(merge_dicts(path,
                                            {'path': os.path.join(prepath, path['path'])}))
                elif isinstance(path, str):
                    tmps.append({'path': os.path.join(prepath, path)})
            except AttributeError as e:
                print(e.args)
                print(repr(e))
                tmps.append({'error': e.args})
        return tmps

    def fix_sites(self, sites, hostname=""):
        sites_out = []
        if type(sites) is list:
            for site in sites:
                sites_out.append(parse_site(site, hostname))
        # attempt to handle being passed a single wp_site as a dict
        elif type(sites) is dict:
            sites_out.append(parse_site(sites, hostname))
        else:
            raise AnsibleError(
                "not a wp_site, or anything that looks like a wp_site")

        return sites_out


def get_publicIpv4(hostvars):

    for ip in hostvars['ansible_all_ipv4_addresses']:
        if ip.startswith('172.'):
            return ip

    return hostvars['ansible_all_ipv4_addresses'][-1:]


def parse_site(sitetmp, hostvars):
    site_temp = {}
    print(repr(sitetmp))

    # config passed site, which we will use directly
    if 'site' in sitetmp:
        site_temp = sitetmp

    # config passed subdomain, so we need to construct a dev url
    elif 'site_subdomain' in sitetmp:
        site_tld = ''
        print(hostvars)
        # www.xxx.yyy.zzz.nip.io types domains resolve to www.xxx.yyy.zzz
        # so we want to prefix the public_ipv4 to the tld part
        if sitetmp['site_tld'] and sitetmp['site_tld'] in ('nip.io', 'xip.io'):
            site_tld = get_publicIpv4(hostvars) + '.' + sitetmp['site_tld']
        else:
            site_tld = sitetmp['site_tld']

        site_temp['site'] = "{0}.{1}.{2}".format(
            sitetmp['site_subdomain'],
            sitetmp['site_domain'] if 'site_domain' in sitetmp
            else hostvars['ansible_hostname'],
            site_tld
        )
        site_temp['plugins'] = sitetmp.get('plugins', [])
        site_temp['theme'] = sitetmp.get('theme', None)
        site_temp['themes'] = sitetmp.get('themes', [])
        site_temp['multisite'] = sitetmp.get('multisite', False)

    return site_temp


def modify_list(values=[], pattern='', replacement='', ignorecase=False):
    ''' Perform a `re.sub` on every item in the list'''
    if ignorecase:
        flags = re.I
    else:
        flags = 0
    _re = re.compile(pattern, flags=flags)
    return [_re.sub(replacement, value) for value in values]


def append_to_list(values=[], suffix=''):
    if isinstance(values, string_types):
        values = values.split(',')
    return [str(value+suffix) for value in values]


def array_to_str(values=[], separator=','):
    return separator.join(values)


def extract_role_users(users={}, exclude_users=[]):
    role_users = []
    for user, details in users.iteritems():
        if user not in exclude_users and "roles" in details:
            for role in details["roles"]:
                role_users.append("%s:%s" % (role, user))
    return role_users


def filename(filename=''):
    return os.path.splitext(os.path.basename(filename))[0]


def remove_reserved(user_roles={}):
    not_reserved = []
    for user_role, details in user_roles.items():
        if "metadata" not in details or "_reserved" not in details["metadata"] or not details["metadata"]["_reserved"]:
            not_reserved.append(user_role)
    return not_reserved


def filter_reserved(users_role={}):
    reserved = []
    for user_role, details in users_role.items():
        if "metadata" in details and "_reserved" in details["metadata"] and details["metadata"]["_reserved"]:
            reserved.append(user_role)
    return reserved


def create_sitename(sites=[]):
    reserved = []
    for site in sites:
        try:
            len(site['site'])
        except AttributeError as e:
            print('Failed: ' + str(e))
        if site['site'] and len(site['site']) > 5:
            site['site2222'] = "trtrg"
        else:
            site['processed'] = True
        reserved.append(site)

    return reserved


def strip_fieldattributes(obj=""):

    # print("processing {0} ".format(type(obj)))

    if isinstance(obj, str):
        return unicode(obj, "utf-8")
    elif isinstance(obj, unicode):
        return obj
    # if isinstance(obj, basestring):
    #
    # if isinstance(obj, (bool, int, float)):
    #   return obj
    # elif obj is None:
    #   return ""
    elif isinstance(obj, dict):
        tmp = {}
        for k, v in obj.items():
            tmp[k] = strip_fieldattributes(v)
        return tmp
    elif isinstance(obj, (list, tuple)) and not isinstance(obj, basestring):
        tmp = []
        for foo in obj:
            tmp.append(strip_fieldattributes(foo))

        return tmp

    # str(type(MyClassicClass)) == "<type 'classobj'>"

    elif str(type(obj)) == "<class 'ansible.playbook.attribute.FieldAttribute'>":
        return "field attribute unserializable"
    elif str(type(obj)) == "<class 'ansible.playbook.role.Role'>":
        return "ansible.playbook.role.Role"
    elif str(type(obj)) == "<class 'ansible.vars.hostvars.HostVarsVars'>":
        # print("here")
        tmp = {}
        for k, v in obj.items():
            tmp[k] = strip_fieldattributes(v)
        return tmp
    else:
        # print("processing here {0} ".format(type(obj)))
        return obj

    return []


def buildCombo(reponame, platforms, suites):
    tmp = []
    for platform in platforms:
        for suite in suites:
            tmp.append("{0}_{1}_{2}".format(reponame, platform, suite))

    return tmp


def prepend_path(paths=[], prepath=''):
    return [os.path.join(prepath, path) for path in paths]


def merge_dicts(x, y):
    z = x.copy()   # start with x's keys and values
    z.update(y)    # modifies z with y's keys and values & returns None
    return z


def parse_url(url):
    """return a dict, of the parsed elements"""
    result = {}

    o = urlparse(url)

    result['scheme'] = o.scheme
    result['port'] = o.port
    result['url'] = o.geturl()
    result['path'] = o.path
    result['netloc'] = o.netloc
    result['query'] = o.query
    result['hostname'] = o.hostname

    return result
