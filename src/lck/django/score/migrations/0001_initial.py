# -*- coding: utf-8 -*-
import datetime
from south.creator.freezer import freeze_apps
from south.db import db
from south.v2 import SchemaMigration

from django.conf import settings


SCORE_VOTER_MODEL = getattr(settings, 'SCORE_VOTER_MODEL',
    getattr(settings, 'AUTH_PROFILE_MODULE', 'auth.User'))
apm_key = SCORE_VOTER_MODEL.lower()
apm_app = SCORE_VOTER_MODEL.split('.')[0]


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'TotalScore'
        db.create_table('score_totalscore', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('value', self.gf('django.db.models.fields.IntegerField')(default=0, db_index=True)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(related_name=u'score_totalscore_scores', to=orm['contenttypes.ContentType'])),
            ('object_id', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
        ))
        db.send_create_signal('score', ['TotalScore'])

        # Adding model 'Vote'
        db.create_table('score_vote', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('total_score', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['score.TotalScore'])),
            ('voter', self.gf('django.db.models.fields.related.ForeignKey')(to=orm[SCORE_VOTER_MODEL])),
            ('value', self.gf('django.db.models.fields.IntegerField')(default=1, db_index=True)),
            ('reason', self.gf('django.db.models.fields.TextField')(default=u'', blank=True)),
        ))
        db.send_create_signal('score', ['Vote'])

        # Adding unique constraint on 'Vote', fields ['total_score', 'voter']
        db.create_unique('score_vote', ['total_score_id', 'voter_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'Vote', fields ['total_score', 'voter']
        db.delete_unique('score_vote', ['total_score_id', 'voter_id'])

        # Deleting model 'TotalScore'
        db.delete_table('score_totalscore')

        # Deleting model 'Vote'
        db.delete_table('score_vote')


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
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'score.totalscore': {
            'Meta': {'object_name': 'TotalScore'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'score_totalscore_scores'", 'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'})
        },
        'score.vote': {
            'Meta': {'unique_together': "([u'total_score', u'voter'],)", 'object_name': 'Vote'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'reason': ('django.db.models.fields.TextField', [], {'default': "u''", 'blank': 'True'}),
            'total_score': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['score.TotalScore']"}),
            'value': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'}),
            'voter': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['{SCORE_VOTER_MODEL}']".format(SCORE_VOTER_MODEL=SCORE_VOTER_MODEL)})
        }
    }

    complete_apps = ['score']
