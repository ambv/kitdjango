# -*- coding: utf-8 -*-
import datetime
from south.creator.freezer import freeze_apps
from south.db import db
from south.v2 import SchemaMigration

from django.db import models
from django.conf import settings


EDITOR_TRACKABLE_MODEL = getattr(settings, 'EDITOR_TRACKABLE_MODEL',
    getattr(settings, 'AUTH_PROFILE_MODULE', 'auth.User'))
apm_key = EDITOR_TRACKABLE_MODEL.lower()
apm_app = EDITOR_TRACKABLE_MODEL.split('.')[0]


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'BadgeGroup'
        db.create_table('badges_badgegroup', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=75)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=75, primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
            ('callback', self.gf('django.db.models.fields.CharField')(default=u'', max_length=100, blank=True)),
            ('multiple_allowed', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('badges', ['BadgeGroup'])

        # Adding model 'BadgeIcon'
        db.create_table('badges_badgeicon', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100, db_index=True)),
            ('slug', self.gf('django.db.models.fields.SlugField')(unique=True, max_length=50)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('height', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('width', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=200)),
        ))
        db.send_create_signal('badges', ['BadgeIcon'])

        # Adding model 'BadgeType'
        db.create_table('badges_badgetype', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=75)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=75, primary_key=True)),
            ('description', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
            ('callback', self.gf('django.db.models.fields.CharField')(default=u'', max_length=100, blank=True)),
            ('group', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['badges.BadgeGroup'])),
            ('icon', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['badges.BadgeIcon'], null=True, blank=True)),
        ))
        db.send_create_signal('badges', ['BadgeType'])

        # Adding model 'Badge'
        db.create_table('badges_badge', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('created_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm[EDITOR_TRACKABLE_MODEL], blank=True, null=True)),
            ('modified_by', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'+', on_delete=models.SET_NULL, default=None, to=orm[EDITOR_TRACKABLE_MODEL], blank=True, null=True)),
            ('type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['badges.BadgeType'])),
            ('owner_ct', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'badges_badge_owned_received', to=orm['contenttypes.ContentType'])),
            ('owner_oid', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('subject_ct', self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name=u'badges_badge_badges_given', null=True, blank=True, to=orm['contenttypes.ContentType'])),
            ('subject_oid', self.gf('django.db.models.fields.IntegerField')(default=None, null=True, db_index=True, blank=True)),
            ('comment', self.gf('django.db.models.fields.TextField')(default=None, null=True, blank=True)),
        ))
        db.send_create_signal('badges', ['Badge'])


    def backwards(self, orm):
        # Deleting model 'BadgeGroup'
        db.delete_table('badges_badgegroup')

        # Deleting model 'BadgeIcon'
        db.delete_table('badges_badgeicon')

        # Deleting model 'BadgeType'
        db.delete_table('badges_badgetype')

        # Deleting model 'Badge'
        db.delete_table('badges_badge')


    models = {
        apm_key: freeze_apps(apm_app)[apm_key],
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
        'badges.badge': {
            'Meta': {'object_name': 'Badge'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'comment': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'created_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['{EDITOR_TRACKABLE_MODEL}']".format(EDITOR_TRACKABLE_MODEL=EDITOR_TRACKABLE_MODEL), 'blank': 'True', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'modified_by': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'+'", 'on_delete': 'models.SET_NULL', 'default': 'None', 'to': "orm['{EDITOR_TRACKABLE_MODEL}']".format(EDITOR_TRACKABLE_MODEL=EDITOR_TRACKABLE_MODEL), 'blank': 'True', 'null': 'True'}),
            'owner_ct': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'badges_badge_owned_received'", 'to': "orm['contenttypes.ContentType']"}),
            'owner_oid': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'subject_ct': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "u'badges_badge_badges_given'", 'null': 'True', 'blank': 'True', 'to': "orm['contenttypes.ContentType']"}),
            'subject_oid': ('django.db.models.fields.IntegerField', [], {'default': 'None', 'null': 'True', 'db_index': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['badges.BadgeType']"})
        },
        'badges.badgegroup': {
            'Meta': {'object_name': 'BadgeGroup'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'callback': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '100', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '75', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'multiple_allowed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '75'})
        },
        'badges.badgeicon': {
            'Meta': {'object_name': 'BadgeIcon'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'height': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '200'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50'}),
            'title': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100', 'db_index': 'True'}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'})
        },
        'badges.badgetype': {
            'Meta': {'object_name': 'BadgeType'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'callback': ('django.db.models.fields.CharField', [], {'default': "u''", 'max_length': '100', 'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'description': ('django.db.models.fields.TextField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'group': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['badges.BadgeGroup']"}),
            'icon': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['badges.BadgeIcon']", 'null': 'True', 'blank': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '75', 'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '75'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['badges']
