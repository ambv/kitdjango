# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'FlatPage'
        db.create_table('flatpages_flatpage', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('modified', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('cache_version', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('language', self.gf('django.db.models.fields.PositiveIntegerField')(default=39)),
            ('url', self.gf('django.db.models.fields.CharField')(max_length=100, db_index=True)),
            ('content', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('enable_comments', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('template_name', self.gf('django.db.models.fields.CharField')(max_length=70, blank=True)),
            ('registration_required', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('flatpages', ['FlatPage'])

        # Adding unique constraint on 'FlatPage', fields ['url', 'language']
        db.create_unique('flatpages_flatpage', ['url', 'language'])

        # Adding M2M table for field sites on 'FlatPage'
        db.create_table('flatpages_flatpage_sites', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('flatpage', models.ForeignKey(orm['flatpages.flatpage'], null=False)),
            ('site', models.ForeignKey(orm['sites.site'], null=False))
        ))
        db.create_unique('flatpages_flatpage_sites', ['flatpage_id', 'site_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'FlatPage', fields ['url', 'language']
        db.delete_unique('flatpages_flatpage', ['url', 'language'])

        # Deleting model 'FlatPage'
        db.delete_table('flatpages_flatpage')

        # Removing M2M table for field sites on 'FlatPage'
        db.delete_table('flatpages_flatpage_sites')


    models = {
        'flatpages.flatpage': {
            'Meta': {'ordering': "(u'url', u'language')", 'unique_together': "((u'url', u'language'),)", 'object_name': 'FlatPage'},
            'cache_version': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            'content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'enable_comments': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'language': ('django.db.models.fields.PositiveIntegerField', [], {'default': '39'}),
            'modified': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'registration_required': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'sites': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['sites.Site']", 'symmetrical': 'False'}),
            'template_name': ('django.db.models.fields.CharField', [], {'max_length': '70', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '100', 'db_index': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['flatpages']