# -*- coding: utf-8 -*-
import datetime
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
        # Adding model 'UserAgent'
        db.create_table('activitylog_useragent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255, db_index=True)),
        ))
        db.send_create_signal('activitylog', ['UserAgent'])

        # Adding model 'IP'
        db.create_table('activitylog_ip', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('address', self.gf('django.db.models.fields.IPAddressField')(null=True, default=None, max_length=15, blank=True, unique=True, db_index=True)),
            ('number', self.gf('django.db.models.fields.BigIntegerField')(default=None, unique=True, null=True, blank=True)),
            ('hostname', self.gf('django.db.models.fields.CharField')(default=None, max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal('activitylog', ['IP'])

        # Adding model 'Backlink'
        db.create_table('activitylog_backlink', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=100)),
            ('referrer', self.gf('django.db.models.fields.URLField')(max_length=100)),
            ('visits', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
            ('status', self.gf('django.db.models.fields.PositiveIntegerField')(default=1)),
        ))
        db.send_create_signal('activitylog', ['Backlink'])

        # Adding unique constraint on 'Backlink', fields ['site', 'url', 'referrer']
        db.create_unique('activitylog_backlink', ['site_id', 'url', 'referrer'])

        # Adding model 'ProfileIP'
        db.create_table('activitylog_profileip', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['{ACTIVITYLOG_PROFILE_MODEL}'.format(ACTIVITYLOG_PROFILE_MODEL=ACTIVITYLOG_PROFILE_MODEL)])),
            ('ip', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activitylog.IP'])),
        ))
        db.send_create_signal('activitylog', ['ProfileIP'])

        # Adding unique constraint on 'ProfileIP', fields ['ip', 'user']
        db.create_unique('activitylog_profileip', ['ip_id', 'user_id'])

        # Adding unique constraint on 'ProfileIP', fields ['ip', 'profile']
        db.create_unique('activitylog_profileip', ['ip_id', 'profile_id'])

        # Adding model 'ProfileUserAgent'
        db.create_table('activitylog_profileuseragent', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('profile', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['{ACTIVITYLOG_PROFILE_MODEL}'.format(ACTIVITYLOG_PROFILE_MODEL=ACTIVITYLOG_PROFILE_MODEL)])),
            ('agent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['activitylog.UserAgent'])),
        ))
        db.send_create_signal('activitylog', ['ProfileUserAgent'])

        # Adding unique constraint on 'ProfileUserAgent', fields ['agent', 'user']
        db.create_unique('activitylog_profileuseragent', ['agent_id', 'user_id'])

        # Adding unique constraint on 'ProfileUserAgent', fields ['agent', 'profile']
        db.create_unique('activitylog_profileuseragent', ['agent_id', 'profile_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'ProfileUserAgent', fields ['agent', 'profile']
        db.delete_unique('activitylog_profileuseragent', ['agent_id', 'profile_id'])

        # Removing unique constraint on 'ProfileUserAgent', fields ['agent', 'user']
        db.delete_unique('activitylog_profileuseragent', ['agent_id', 'user_id'])

        # Removing unique constraint on 'ProfileIP', fields ['ip', 'profile']
        db.delete_unique('activitylog_profileip', ['ip_id', 'profile_id'])

        # Removing unique constraint on 'ProfileIP', fields ['ip', 'user']
        db.delete_unique('activitylog_profileip', ['ip_id', 'user_id'])

        # Removing unique constraint on 'Backlink', fields ['site', 'url', 'referrer']
        db.delete_unique('activitylog_backlink', ['site_id', 'url', 'referrer'])

        # Deleting model 'UserAgent'
        db.delete_table('activitylog_useragent')

        # Deleting model 'IP'
        db.delete_table('activitylog_ip')

        # Deleting model 'Backlink'
        db.delete_table('activitylog_backlink')

        # Deleting model 'ProfileIP'
        db.delete_table('activitylog_profileip')

        # Deleting model 'ProfileUserAgent'
        db.delete_table('activitylog_profileuseragent')


    models = {
        apm_key: freeze_apps(apm_app)[apm_key],
        'activitylog.backlink': {
            'Meta': {'unique_together': "((u'site', u'url', u'referrer'),)", 'object_name': 'Backlink'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'referrer': ('django.db.models.fields.URLField', [], {'max_length': '100'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'status': ('django.db.models.fields.PositiveIntegerField', [], {'default': '1'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '100'}),
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
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255', 'db_index': 'True'}),
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
