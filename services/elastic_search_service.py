from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
import json
from flask import jsonify


class ElasticSearchService:
    def __init__(self, elastic_search_url, index_name):
        self.es = Elasticsearch([elastic_search_url])
        self.index_name = index_name


    def create_index(self):
        # Создание индекса Elasticsearch
        if not self.es.indices.exists(index=self.index_name):
            self.es.indices.create(index=self.index_name)

    def index_data(self, data):
        # Индексация данных в Elasticsearch
        bulk_data = []
        for doc_id, document in enumerate(data):
            #if '_id' in document:
            #    document['_id'] = str("123")
            #print(type(document))
            document.pop('_id')
            bulk_data.append({
                '_op_type': 'index',
                '_index': self.index_name,
                '_id': doc_id,
                '_source': document
            })
        #print(bulk_data)
        #print(data)
        #bulk_data = json.dumps(bulk_data)
        bulk(self.es, bulk_data)

    def search_trains_and_tickets(self, departure_station, arrival_station, departure_date):
        # Поиск поездов и билетов в Elasticsearch
        query = {
            "query": {
                "bool": {
                    "must": [
                        #{"match": {"stations": departure_station}},
                        #{"match": {"stations": arrival_station}},
                        {"match": {"departure_date": departure_date}},
                        {"range": {"available_tickets": {"gt": 0}}}
                    ]
                }
            }
        }
        response = self.es.search(index=self.index_name, body=query)
        #print(str(self.index_name))
        #print('RESPONSE')
        #print(response)
        return [hit['_source'] for hit in response['hits']['hits']]
