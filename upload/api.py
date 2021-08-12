import os
import requests
import logging
from django.conf import settings
from elasticsearch_dsl import Search, Document
from elasticsearch_dsl.query import Q
from elasticsearch_dsl.connections import connections
from elasticsearch_dsl.utils import AttrList
from elasticsearch_dsl import (Document, Text, Keyword, Date, Nested, Boolean,
                               analyzer, Integer, Index)
from elasticsearch import Elasticsearch
from elasticsearch import TransportError
import logging
import six
import re
from celery import task
from django.conf import settings
from django.core.files import File
from django.utils import timezone


'''
Need indexes for the following classes:
project
sample
origin data
analysis data
datafile
non-image file 
image file 
advanced image file

Implement todict for each of these classes 
Use this function to send to the server each of the classes 
 
Need to write any basic search query functions ?

On the retrival side:
Write a view which in turn calls an API function which will search over an index 
which is present 

'''


logger = logging.getLogger(__name__)

es_settings = getattr(settings, 'ELASTIC_SEARCH', {})
index_dr = 'digitalrocks_new'

try:
    default_index = es_settings['default_index']
    cluster = es_settings['cluster']
    hosts = cluster['hosts']
except KeyError:
    logger.exception('ELASTIC_SEARCH missing required configuration')

connections.configure(
    default={
        'hosts': hosts,
        'sniff_on_start': True,
        'sniff_on_connection_fail': True,
        'sniffer_timeout': 60,
        'retry_on_timeout': True,
        'timeout:': 20,
    })

class ProjectMapping(Document):
    user = Keyword(analyzer='snowball')
    name = Keyword(analyzer='snowball')
    creation_date = Date()
    description = Keyword(analyzer='snowball')
    institution = Keyword(analyzer='snowball')
    doi = Keyword(analyzer='snowball')
    license = Keyword(analyzer='snowball')
    project_id = Keyword(index='not_analyzed')
    class Meta:
        index = index_dr
        doc_type = 'project'

    def save(self, ** kwargs):
        return super(ProjectMapping, self).save(** kwargs)

class SampleMapping(Document):
    user = Keyword(analyzer='snowball')
    name = Keyword(analyzer='snowball')
    project = Keyword(analyzer='snowball')
    description = Keyword(analyzer='snowball')
    porous_media_type = Keyword(analyzer='snowball')
    source = Keyword(analyzer='snowball')
    identifier = Keyword(analyzer='snowball')
    geographic_origin = Keyword(analyzer='snowball')
    location = Keyword(analyzer='snowball')
    project_id = Keyword(index='not_analyzed')
    sample_id = Keyword(index='not_analyzed')
    class Meta:
        index = index_dr
        doc_type = 'sample'

    def save(self, ** kwargs):
        return super(SampleMapping, self).save(** kwargs)
    
class OriginDataMapping(Document):
    name = Keyword(analyzer='snowball')
    project = Keyword(analyzer='snowball')
    sample = Keyword(analyzer='snowball')
    uploader = Keyword(analyzer='snowball')
    doi = Keyword(analyzer='snowball')
    project_id = Keyword(index='not_analyzed')
    origin_data_id = Keyword(index='not_analyzed')

    class Meta:
        index = index_dr
        doc_type = 'origindata'

    def save(self, ** kwargs):
        return super(OriginDataMapping, self).save(** kwargs)
    
class AnalysisDataMapping(Document):
    name = Keyword(analyzer='snowball')
    analysis_type = Keyword(analyzer='snowball')
    project = Keyword(analyzer='snowball')
    sample = Keyword(analyzer='snowball')
    uploader = Keyword(analyzer='snowball')
    base_origin_data = Keyword(analyzer='snowball')
    base_analysis_data = Keyword(analyzer='snowball')
    base_data_url = Keyword(analyzer='snowball')
    doi = Keyword(analyzer='snowball')
    project_id = Keyword(index='not_analyzed')
    analysis_data_id = Keyword(index='not_analyzed')


    class Meta:
        index = index_dr
        doc_type = 'analysisdata'

    def save(self, ** kwargs):
        return super(AnalysisDataMapping, self).save(** kwargs)
    
class DatafileMapping(Document):
    data_file_id = Keyword(index='not_analyzed')
    filename = Keyword(analyzer='snowball')
    analysis_data = Keyword(analyzer='snowball')
    origin_data = Keyword(analyzer='snowball')
    uploader = Keyword(analyzer='snowball')
    analysis_data_id = Keyword(index='not_analyzed')
    origin_data_id = Keyword(index='not_analyzed')
    class Meta:
        index = index_dr
        doc_type = 'datafile'

    def save(self, ** kwargs):
        return super(DatafileMapping, self).save(** kwargs)

def search_query(search_phrase):
    q = Q('query_string', query='*%s*' % search_phrase)
    s = Search(index=index_dr, doc_type='project,sample,origindata,analysisdata').query(q)
    s = s.sort('_type')
    response = s.execute()
    return s, response

def index_project(project):
    q = Q({'term': {'project_id': str(project.id)}})
    s = ProjectMapping.search().query(q)
    response = s.execute()
    if not response.hits.total:
        index_object = ProjectMapping()
    else:
        index_object = response.hits[0]

    index_object.user = project.user.full_name()
    index_object.name = project.name
    index_object.creation_date = project.creation_date.isoformat()
    index_object.description = project.description
    index_object.doi = project.doi
    index_object.project_id = str(project.id)
    collabs = []
    for collab in project.collaborators.all():
        collabs.append({'first_name': collab.user.first_name,
                        'last_name': collab.user.last_name})
    index_object.collaborators = collabs
    index_object.save()

def index_sample(sample):
    q = Q({'term': {'sample_id': str(sample.id)}})
    s = SampleMapping.search().query(q)
    response = s.execute()
    if not response.hits.total:
        index_object = SampleMapping()
    else:
        index_object = response.hits[0]

    index_object.user = sample.uploader.full_name()
    index_object.name = sample.name
    index_object.project = sample.project.name
    index_object.description = sample.description
    index_object.porous_media_type = sample.porous_media_type
    index_object.source = sample.source
    index_object.porosity = sample.porosity
    index_object.identifier = sample.identifier
    index_object.geographic_origin = sample.geographic_origin
    index_object.location = sample.location
    index_object.sample_id = str(sample.id)
    index_object.project_id = (sample.project.id)
    index_object.save()

def index_origin_data(origin_data):
    q = Q({'term': {'origin_data_id': str(origin_data.id)}})
    s = OriginDataMapping.search().query(q)
    response = s.execute()
    if not response.hits.total:
        index_object = OriginDataMapping()
    else:
        index_object = response.hits[0]

    index_object.name = origin_data.name
    if index_object.project is not None:
        index_object.project = origin_data.project.name
        index_object.project_id = str(origin_data.project.id)
    if origin_data.sample is not None:
        index_object.sample = origin_data.sample.name
    index_object.uploader = origin_data.uploader.full_name()
    index_object.doi = origin_data.doi
    index_object.origin_data_id = str(origin_data.id)
    index_object.save()

def index_analysis_data(analysis_data):
    q = Q({'term': {'analysis_data_id': str(analysis_data.id)}})
    s = AnalysisDataMapping.search().query(q)
    response = s.execute()
    if not response.hits.total:
        index_object = AnalysisDataMapping()
    else:
        index_object = response.hits[0]
    
    index_object.name = analysis_data.name
    index_object.analysis_type = analysis_data.type
    index_object.project = analysis_data.project.name
    if analysis_data.sample is not None:
        index_object.sample = analysis_data.sample.name
    index_object.uploader = analysis_data.uploader.full_name()
    index_object.doi = analysis_data.doi
    if analysis_data.base_origin_data is not None:
        index_object.base_origin_data = analysis_data.base_origin_data.name
    if analysis_data.base_analysis_data is not None:
        index_object.base_analysis_data = analysis_data.base_analysis_data.name
    index_object.base_data_url = analysis_data.base_data_url
    index_object.analysis_data_id = str(analysis_data.id)
    index_object.project_id = str(analysis_data.project.id)

def index_data_file(data_file):
    q = Q({'term':
          {
              'data_file_id':
              '{cls}-{identifier}'.format(
                  cls=data_file.__class__.__name__,
                  identifier=str(data_file.id)
                  )
          }
          })
    s = DatafileMapping.search().query(q)
    response = s.execute()
    if not response.hits.total:
        index_object = DatafileMapping()
    else:
        index_object = response.hits[0]

    index_object.filename = data_file.file_name()
    index_object.analysis_data = (
        data_file.analysis_data.name
        if(data_file.analysis_data is not None) else ''
    )
    index_object.origin_data = (
        data_file.origin_data.name
        if(data_file.origin_data is not None) else ''
    )
    index_object.analysis_data_id = (
        data_file.analysis_data.id
        if(data_file.analysis_data is not None) else ''
    )
    index_object.origin_data_id = (
        data_file.origin_data.id
        if(data_file.origin_data is not None) else ''
    )
    index_object.uploader = data_file.uploader.full_name()
    index_object.data_file_id = '{cls}-{identifier}'.format(
            cls=data_file.__class__.__name__, identifier=data_file.id
    ) 
    index_object.save()

def init_index():
    index = Index(index_dr)
    if not index.exists():
        index.create()
        ProjectMapping.init()
        SampleMapping.init()
        OriginDataMapping.init()
        AnalysisDataMapping.init()
        DatafileMapping.init()
