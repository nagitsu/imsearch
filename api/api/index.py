from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

from . import settings


DOC_TYPE = 'image'
ES_MAPPING = {
    'settings': {
        'index': {
            'mapper': {'dynamic': False},
            'number_of_shards': 5,
            'number_of_replicas': 0,
        }
    },
    'mappings': {
        DOC_TYPE: {
            '_all': {'enabled': False},
            'properties': {
                'image_name': {'type': 'keyword'},
                'image_id': {'type': 'keyword'},
                'objects': {
                    'type': 'nested',
                    'properties': {
                        'label': {'type': 'text'},
                        'width': {'type': 'integer'},
                        'height': {'type': 'integer'},
                        'x': {'type': 'integer'},
                        'y': {'type': 'integer'},
                    }
                },
            }
        }
    }
}


def check_configuration():
    if not es.indices.exists(index=settings.ES_INDEX):
        es.indices.create(
            index=settings.ES_INDEX, body=ES_MAPPING
        )


def store_doc(doc):
    es.index(index=settings.ES_INDEX, doc_type=DOC_TYPE, body=doc)


def search():
    return Search(using=es, index=settings.ES_INDEX, doc_type=DOC_TYPE)


# Check everything is correctly configured when importing the module.
es = Elasticsearch([settings.ES_HOST], retry_on_timeout=True)
check_configuration()
