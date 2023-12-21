from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import pymongo
from elasticsearch import Elasticsearch
from hazelcast import HazelcastClient
from station_route_service import StationRouteService
from train_service import TrainService
from ticket_service import TicketService
from elastic_search_service import ElasticSearchService

app = Flask(__name__)

# Конфигурация для MongoDB
mongodb_client = pymongo.MongoClient('mongodb://localhost:27017')
database_name = 'railway_ticket_system'
station_route_service = StationRouteService(mongodb_client, database_name)
train_service = TrainService(mongodb_client, database_name)

# Конфигурация для Hazelcast
hazelcast_client = HazelcastClient(
    cluster_name="dev",
    cluster_members=["192.168.1.66:5701"]
)
#my_map = hazelcast_client.get_map("my-distributed-map").blocking()
#print(my_map)
ticket_service = TicketService(mongodb_client, database_name, hazelcast_client)

# Конфигурация для Elasticsearch
elastic_search_url = 'http://localhost:9200'
elastic_search_index_name = 'railway_tickets'
elastic_search_service = ElasticSearchService(elastic_search_url, elastic_search_index_name)

@app.route('/initialize', methods=['POST'])
@cross_origin()
def initialize_data():
    data = request.json
    stations_data = data.get('stations', [])
    routes_data = data.get('routes', [])
    trains_data = data.get('trains', [])

    station_route_service.initialize_stations(stations_data)
    station_route_service.initialize_routes(routes_data)
    train_service.initialize_trains(trains_data)

    elastic_search_service.create_index()
    elastic_search_service.index_data(trains_data)

    return jsonify({"message": "Data initialized successfully"})

@app.route('/search', methods=['GET'])
@cross_origin()
def search_trains_and_tickets():
    departure_station = request.args.get('departure_station')
    arrival_station = request.args.get('arrival_station')
    departure_date = request.args.get('departure_date')

    #print('QUERY PARAMS')
    #print(departure_station)
    #print(arrival_station)
    #print(departure_date)
    if not departure_station or not arrival_station or not departure_date:
        return jsonify({"error": "Invalid request parameters"})

    results = elastic_search_service.search_trains_and_tickets(departure_station, arrival_station, departure_date)
    #print('RESULTS')
    #print(results)
    return jsonify(results)

@app.route('/buy', methods=['POST'])
@cross_origin()
def buy_ticket():
    data = request.json
    train_id = data.get('train_id')
    seat_number = data.get('seat_number')
    user_id = data.get('user_id')

    if not train_id or not seat_number or not user_id:
        return jsonify({"error": "Invalid request parameters"})

    ticket = ticket_service.buy_ticket(train_id, seat_number, user_id)

    if ticket:
        return jsonify({"message": "Ticket purchased successfully", "ticket": ticket})
    else:
        return jsonify({"error": "Failed to purchase ticket"})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
    cors = CORS(app)
    app.config['CORS_HEADERS'] = 'Content-Type'