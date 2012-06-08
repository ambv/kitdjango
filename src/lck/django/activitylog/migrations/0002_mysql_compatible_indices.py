# -*- coding: utf-8 -*-
import zlib

from south.creator.freezer import freeze_apps
from south.db import db
from south.v2 import SchemaMigration

from django.conf import settings


ACTIVITYLOG_PROFILE_MODEL = getattr(settings, 'ACTIVITYLOG_PROFILE_MODEL',
    getattr(settings, 'AUTH_PROFILE_MODULE', 'auth.User'))
apm_key = ACTIVITYLOG_PROFILE_MODEL.lower()
apm_app = ACTIVITYLOG_PROFILE_MODEL.split('.')[0]


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Backlink', fields ['url', 'referrer', 'site']
        db.delete_unique('activitylog_backlink', ['url', 'referrer', 'site_id'])

        # Removing unique constraint on 'UserAgent', fields ['name']
        db.delete_unique('activitylog_useragent', ['name'])

        # Adding field 'UserAgent.hash'
        db.add_column('activitylog_useragent', 'hash',
                      self.gf('django.db.models.fields.IntegerField')(null=True, unique=True, db_index=True),
                      keep_default=False)
        if not db.dry_run:
            for ua in orm.UserAgent.objects.all():
                ua.hash = self.hash_for_name(ua.name)
                ua.save()
        db.alter_column('activitylog_useragent', 'hash',
                        self.gf('django.db.models.fields.IntegerField')(unique=True, db_index=True))
        db.alter_column('activitylog_useragent', 'hash',
                        self.gf('django.db.models.fields.IntegerField')(unique=True, db_index=True))


        # Changing field 'UserAgent.name'
        db.alter_column('activitylog_useragent', 'name', self.gf('django.db.models.fields.TextField')())

        # Adding field 'Backlink.hash'
        db.add_column('activitylog_backlink', 'hash',
                      self.gf('django.db.models.fields.IntegerField')(default=None, null=True, unique=True, db_index=True),
                      keep_default=False)
        if not db.dry_run:
            for ua in orm.Backlink.objects.all():
                ua.hash = self.hash_for_triple(ua.site, ua.url, ua.referrer)
                ua.save()
        db.alter_column('activitylog_backlink', 'hash',
                        self.gf('django.db.models.fields.IntegerField')(unique=True, db_index=True))


        # Changing field 'Backlink.url'
        db.alter_column('activitylog_backlink', 'url', self.gf('django.db.models.fields.URLField')(max_length=500))

        # Changing field 'Backlink.referrer'
        db.alter_column('activitylog_backlink', 'referrer', self.gf('django.db.models.fields.URLField')(max_length=500))

    def backwards(self, orm):
        # Deleting field 'UserAgent.hash'
        db.delete_column('activitylog_useragent', 'hash')


        # Changing field 'UserAgent.name'
        db.alter_column('activitylog_useragent', 'name', self.gf('django.db.models.fields.CharField')(max_length=255, unique=True))
        # Adding unique constraint on 'UserAgent', fields ['name']
        db.create_unique('activitylog_useragent', ['name'])

        # Deleting field 'Backlink.hash'
        db.delete_column('activitylog_backlink', 'hash')


        # Changing field 'Backlink.url'
        db.alter_column('activitylog_backlink', 'url', self.gf('django.db.models.fields.URLField')(max_length=100))

        # Changing field 'Backlink.referrer'
        db.alter_column('activitylog_backlink', 'referrer', self.gf('django.db.models.fields.URLField')(max_length=100))
        # Adding unique constraint on 'Backlink', fields ['url', 'referrer', 'site']
        db.create_unique('activitylog_backlink', ['url', 'referrer', 'site_id'])

    @classmethod
    def hash_for_name(cls, name):
        return zlib.adler32(name)

    @classmethod
    def hash_for_triple(cls, site, url, referrer):
        return zlib.adler32(u'\n'.join((str(site.id), url, referrer)).encode('utf8'))

    models = {
        apm_key: freeze_apps(apm_app)[apm_key],
        'activitylog.backlink': {
            'Meta': {'object_name': 'Backlink'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'hash': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'referrer': ('django.db.models.fields.URLField', [], {'max_length': '500'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '500'}),
            'visits': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'})
        },
        'activitylog.ip': {
            'Meta': {'object_name': 'IP'},
            'address': ('django.db.models.fields.IPAddressField', [], {'null': 'True', 'default': 'None', 'max_length': '15', 'blank': 'True', 'unique': 'True', 'db_index': 'True'}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'hostname': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'number': ('django.db.models.fields.BigIntegerField', [], {'default': 'None', 'unique': 'True', 'null': 'True', 'blank': 'True'}),
            'profiles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['{ACTIVITYLOG_PROFILE_MODEL}']".format(ACTIVITYLOG_PROFILE_MODEL=ACTIVITYLOG_PROFILE_MODEL), 'through': "orm['activitylog.ProfileIP']", 'symmetrical': 'False'})
        },
        'activitylog.profileip': {
            'Meta': {'unique_together': "((u'ip', u'user'), (u'ip', u'profile'))", 'object_name': 'ProfileIP'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['activitylog.IP']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['{ACTIVITYLOG_PROFILE_MODEL}']".format(ACTIVITYLOG_PROFILE_MODEL=ACTIVITYLOG_PROFILE_MODEL)}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'activitylog.profileuseragent': {
            'Meta': {'unique_together': "((u'agent', u'user'), (u'agent', u'profile'))", 'object_name': 'ProfileUserAgent'},
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['activitylog.UserAgent']"}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['{ACTIVITYLOG_PROFILE_MODEL}']".format(ACTIVITYLOG_PROFILE_MODEL=ACTIVITYLOG_PROFILE_MODEL)}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'activitylog.useragent': {
            'Meta': {'object_name': 'UserAgent'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'hash': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.TextField', [], {}),
            'profiles': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['{ACTIVITYLOG_PROFILE_MODEL}']".format(ACTIVITYLOG_PROFILE_MODEL=ACTIVITYLOG_PROFILE_MODEL), 'through': "orm['activitylog.ProfileUserAgent']", 'symmetrical': 'False'})
        },
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['activitylog']
