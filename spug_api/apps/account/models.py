# Copyright: (c) OpenSpug Organization. https://github.com/openspug/spug
# Copyright: (c) <spug.dev@gmail.com>
# Released under the AGPL-3.0 License.
from django.db import models
from django.core.cache import cache
from libs import ModelMixin
from django.contrib.auth.hashers import make_password, check_password
import json


def load_json(value, default):
    """把权限字段的值统一成 Python 对象。

    Role 的 page_perms/deploy_perms/group_perms 自 4.0 起为 JSONField，ORM 直接返回 dict/list，
    不能再 json.loads；但从 3.x 升级、手工 SQL 或旧代码写入的库里仍可能是 JSON 字符串
    （甚至被二次编码），这里统一兜底，避免非超管账户一登录就抛 TypeError。
    """
    if isinstance(value, (bytes, bytearray)):
        value = value.decode()
    for _ in range(2):  # 最多解两层，兼容被 json.dumps 二次编码的历史数据
        if not isinstance(value, str):
            break
        if not value.strip():
            return default
        try:
            value = json.loads(value)
        except ValueError:
            return default
    return value if isinstance(value, type(default)) else default


class User(models.Model, ModelMixin):
    username = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100)
    password_hash = models.CharField(max_length=100)  # hashed password
    type = models.CharField(max_length=20, default='default')
    is_supper = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    access_token = models.CharField(max_length=32)
    token_expired = models.IntegerField(null=True)
    last_login = models.CharField(max_length=20)
    last_ip = models.CharField(max_length=50)
    wx_token = models.CharField(max_length=50, null=True)
    roles = models.ManyToManyField('Role', db_table='user_role_rel')
    created_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def make_password(password):
        return make_password(password, hasher='pbkdf2_sha256')

    def verify_password(self, password):
        return check_password(password, self.password_hash)

    def get_perms_cache(self):
        return cache.get(f'perms_{self.id}', set())

    def set_perms_cache(self, value=None):
        cache.set(f'perms_{self.id}', value or set())

    @property
    def page_perms(self):
        data = self.get_perms_cache()
        if data:
            return data
        for item in self.roles.all():
            for m, v in item.get_page_perms().items():
                for p, d in v.items():
                    data.update(f'{m}.{p}.{x}' for x in d)
        self.set_perms_cache(data)
        return data

    @property
    def deploy_perms(self):
        data = {'apps': set(), 'envs': set()}
        for item in self.roles.all():
            perms = item.get_deploy_perms()
            data['apps'].update(perms.get('apps', []))
            data['envs'].update(perms.get('envs', []))
        data['apps'].update(x.id for x in self.app_set.all())
        return data

    @property
    def group_perms(self):
        data = set()
        for item in self.roles.all():
            data.update(item.get_group_perms())
        return list(data)

    def has_perms(self, codes):
        if self.is_supper:
            return True
        return self.page_perms.intersection(codes)

    def __repr__(self):
        return '<User %r>' % self.username

    class Meta:
        db_table = 'users'
        ordering = ('-id',)


class Role(models.Model, ModelMixin):
    name = models.CharField(max_length=50)
    desc = models.CharField(max_length=255, null=True)
    page_perms = models.JSONField(default=dict)
    deploy_perms = models.JSONField(default=dict)
    group_perms = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    def get_page_perms(self):
        return load_json(self.page_perms, {})

    def get_deploy_perms(self):
        return load_json(self.deploy_perms, {})

    def get_group_perms(self):
        return load_json(self.group_perms, [])

    def to_dict(self, *args, **kwargs):
        tmp = super().to_dict(*args, **kwargs)
        tmp['page_perms'] = self.get_page_perms()
        tmp['deploy_perms'] = self.get_deploy_perms()
        tmp['group_perms'] = self.get_group_perms()
        tmp['used'] = self.user_set.filter(is_deleted=False).count()
        return tmp

    def add_deploy_perm(self, target, value):
        perms = {'apps': [], 'envs': []}
        perms.update(self.get_deploy_perms())
        perms.setdefault(target, []).append(value)
        self.deploy_perms = perms
        self.save()

    def clear_perms_cache(self):
        for item in self.user_set.all():
            item.set_perms_cache()

    def __repr__(self):
        return '<Role name=%r>' % self.name

    class Meta:
        db_table = 'roles'
        ordering = ('-id',)


class History(models.Model, ModelMixin):
    username = models.CharField(max_length=100, null=True)
    type = models.CharField(max_length=20, default='default')
    ip = models.CharField(max_length=50)
    agent = models.CharField(max_length=255, null=True)
    message = models.CharField(max_length=255, null=True)
    is_success = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'login_histories'
        ordering = ('-id',)
