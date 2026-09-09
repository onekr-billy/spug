# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <spug.dev@gmail.com>
# Released under the AGPL-3.0 License.
import ldap
from ldap.filter import escape_filter_chars


class LDAP:
    REQUIRED_KEYS = ('server', 'admin_dn', 'admin_password', 'user_ou', 'user_filter', 'map_username', 'map_nickname')

    def __init__(self, server, admin_dn, admin_password, user_ou, user_filter, map_username, map_nickname):
        self.server = server
        self.admin_dn = admin_dn
        self.admin_password = admin_password
        self.user_ou = user_ou
        self.user_filter = user_filter
        self.map_username = map_username
        self.map_nickname = map_nickname

    @classmethod
    def normalize_config(cls, config):
        """把系统设置里的 ldap_service 整理成 4.0 的参数格式，返回 None 表示尚未配置或配置不完整。

        3.x 存的是 {server, port, rules, admin_dn, password, base_dn}，从 3.x 升级后直接 LDAP(**config)
        会因为多出来的 port 等参数抛 TypeError，导致 LDAP 登录报 Exception。这里按 3.x 的语义自动换算：
        server:port -> ldap://server:port，base_dn -> 用户 OU，rules（搜索属性）-> 登录名/姓名映射，
        这样升级后不重新配置也能登录；用户在系统设置里重新保存后即为 4.0 格式。
        """
        if not isinstance(config, dict) or not config:
            return None
        if 'admin_password' not in config and any(k in config for k in ('port', 'rules', 'base_dn')):
            server = str(config.get('server') or '').strip()
            if server and '://' not in server:
                server = f'ldap://{server}:{config.get("port") or 389}'
            attr = str(config.get('rules') or 'cn').strip()
            config = {
                'server': server,
                'admin_dn': config.get('admin_dn'),
                'admin_password': config.get('password'),
                'user_ou': config.get('base_dn'),
                'user_filter': f'({attr}=*)',
                'map_username': attr,
                'map_nickname': attr,
            }
        if not all(config.get(k) for k in cls.REQUIRED_KEYS):
            return None
        return {k: config[k] for k in cls.REQUIRED_KEYS}

    def connect(self):
        try:
            conn = ldap.initialize(f'{self.server}', bytes_mode=False)
            conn.set_option(ldap.OPT_TIMEOUT, 3)
            conn.set_option(ldap.OPT_NETWORK_TIMEOUT, 3)
            conn.simple_bind_s(self.admin_dn, self.admin_password)
            return True, conn
        except Exception as error:
            return False, error.args[0].get('desc')

    
    def all_user(self):
        status, conn = self.connect()
        if status:
            try:
                # user_filter = '(cn=*)'
                # map = ['cn', 'sn']
                # user_map = list(self.user_map.values())
                user_filter = "({}=*)".format(self.user_filter.split('=')[0][1:])
                user_map = [self.map_username, self.map_nickname]
                ldap_result = conn.search_s(self.user_ou, ldap.SCOPE_SUBTREE, user_filter, user_map)
                ldap_users = []
                for dn,entry in ldap_result:
                    if dn == self.user_ou:
                        continue
                    tmp_user = {}
                    for k,v in entry.items():
                        tmp_user.update({k: v[0].decode()})
                    
                    ldap_users.append(tmp_user)
                return True, ldap_users

            except Exception as error:
                return False, error.args[0].get('desc')
        else:
            return False, conn

    def verify_user(self, username, password):
        # 带 DN 的空密码 simple bind 会被多数目录服务视为匿名绑定并返回成功
        # （RFC 4513 unauthenticated bind），必须在绑定前拒绝。
        # 注意不能只判空串：parser 的判空发生在 strip 之前，纯空白密码到这里已是空串。
        if not password or not password.strip():
            return False, '密码不能为空'
        status, conn = self.connect()
        if status:
            try:
                user_filter = f'({self.map_username}={escape_filter_chars(username)})'
                ldap_result_id = conn.search(self.user_ou, ldap.SCOPE_SUBTREE, user_filter, [self.map_username])
                _, result_data = conn.result(ldap_result_id, 0)
                if result_data:
                    conn.simple_bind_s(result_data[0][0], password)
                    return True, True
                else:
                    return False, '账户未找到'
            except Exception as error:
                return False, error.args[0].get('desc')
        else:
            return False, conn

