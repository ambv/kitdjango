# -*- coding: utf-8 -*-
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
        # Removing unique constraint on 'ProfileUserAgent', fields ['user', 'agent']
        db.delete_unique('activitylog_profileuseragent', ['user_id', 'agent_id'])

        # Removing unique constraint on 'ProfileIP', fields ['ip', 'user']
        db.delete_unique('activitylog_profileip', ['ip_id', 'user_id'])

        # Deleting field 'ProfileIP.user'
        db.delete_column('activitylog_profileip', 'user_id')

        # Deleting field 'ProfileUserAgent.user'
        db.delete_column('activitylog_profileuseragent', 'user_id')


    def backwards(self, orm):

        # User chose to not deal with backwards NULL issues for 'ProfileIP.user'
        raise RuntimeError("Cannot reverse this migration. 'ProfileIP.user' and its values cannot be restored.")
        # Adding unique constraint on 'ProfileIP', fields ['ip', 'user']
        db.create_unique('activitylog_profileip', ['ip_id', 'user_id'])


        # User chose to not deal with backwards NULL issues for 'ProfileUserAgent.user'
        raise RuntimeError("Cannot reverse this migration. 'ProfileUserAgent.user' and its values cannot be restored.")
        # Adding unique constraint on 'ProfileUserAgent', fields ['user', 'agent']
        db.create_unique('activitylog_profileuseragent', ['user_id', 'agent_id'])


    models = {
        apm_key: freeze_apps(apm_app)[apm_key],
        'activitylog.backlink': {
            'Meta': {'object_name': 'Backlink'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'hash': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'referrer': ('django.db.models.fields.URLField', [], {'default': "u''", 'max_length': '500', 'blank': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['sites.Site']", 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'url': ('django.db.models.fields.URLField', [], {'default': "u''", 'max_length': '500', 'blank': 'True'}),
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
            'Meta': {'unique_together': "((u'ip', u'profile'),)", 'object_name': 'ProfileIP'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['activitylog.IP']"}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['{ACTIVITYLOG_PROFILE_MODEL}']".format(ACTIVITYLOG_PROFILE_MODEL=ACTIVITYLOG_PROFILE_MODEL)})
        },
        'activitylog.profileuseragent': {
            'Meta': {'unique_together': "((u'agent', u'profile'),)", 'object_name': 'ProfileUserAgent'},
            'agent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['activitylog.UserAgent']"}),
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'profile': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['{ACTIVITYLOG_PROFILE_MODEL}']".format(ACTIVITYLOG_PROFILE_MODEL=ACTIVITYLOG_PROFILE_MODEL)})
        },
        'activitylog.useragent': {
            'Meta': {'object_name': 'UserAgent'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'hash': ('django.db.models.fields.IntegerField', [], {'unique': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
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
