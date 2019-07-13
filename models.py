# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ApiCrosesbystring(models.Model):
    original_number = models.CharField(max_length=30)
    cros_number = models.CharField(max_length=30)

    class Meta:
        managed = False
        db_table = 'api_crosesbystring'


class ApiEmail(models.Model):
    addres = models.CharField(max_length=100)
    data = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'api_email'


class ApiMark(models.Model):
    name = models.CharField(max_length=100)
    referred_id = models.IntegerField(primary_key=True)

    class Meta:
        managed = False
        db_table = 'api_mark'


class ApiModel(models.Model):
    name = models.CharField(max_length=100)
    terms = models.CharField(max_length=50)
    referred_id = models.IntegerField(primary_key=True)
    mark = models.ForeignKey(ApiMark, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_model'


class ApiPart(models.Model):
    part_number = models.CharField(max_length=30)
    prise = models.CharField(max_length=10)
    retail = models.CharField(max_length=10)
    brend = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)
    referred_id = models.CharField(primary_key=True, max_length=100)
    subgroup = models.ForeignKey('ApiSubgroup', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_part'


class ApiPartdescription(models.Model):
    number = models.CharField(max_length=30)
    prise = models.CharField(max_length=10)
    retail = models.CharField(max_length=10)
    brend = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=500)

    class Meta:
        managed = False
        db_table = 'api_partdescription'


class ApiSource(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'api_source'


class ApiSubgroup(models.Model):
    referred_id = models.CharField(primary_key=True, max_length=100)
    name_subgroup = models.CharField(max_length=150)
    code_subgroup = models.CharField(max_length=100)
    name_group = models.CharField(max_length=150)
    code_group = models.CharField(max_length=100)
    typecar = models.ForeignKey('ApiTypecar', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_subgroup'


class ApiTypecar(models.Model):
    name = models.CharField(max_length=150)
    vol = models.CharField(max_length=150)
    terms = models.CharField(max_length=50)
    referred_id = models.IntegerField(primary_key=True)
    body_type = models.CharField(max_length=150)
    cyl = models.CharField(max_length=5)
    drive = models.CharField(max_length=150)
    eng = models.CharField(max_length=150)
    fuel = models.CharField(max_length=50)
    hp = models.CharField(max_length=50)
    kw = models.CharField(max_length=50)
    model = models.ForeignKey(ApiModel, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'api_typecar'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
