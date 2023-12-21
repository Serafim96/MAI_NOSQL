class StationRouteService:
    def __init__(self, mongo_client, database_name):
        self.client = mongo_client
        self.db = self.client[database_name]
        self.stations_collection = self.db['stations']
        self.routes_collection = self.db['routes']

    def initialize_stations(self, stations_data):
        # Инициализация справочника станций
        self.stations_collection.insert_many(stations_data)

    def initialize_routes(self, routes_data):
        # Инициализация справочника маршрутов
        self.routes_collection.insert_many(routes_data)

    def get_station_by_name(self, station_name):
        # Поиск станции по имени
        return self.stations_collection.find_one({'name': station_name})

    def get_route_by_id(self, route_id):
        # Поиск маршрута по идентификатору
        return self.routes_collection.find_one({'id': route_id})

    def get_routes_for_stations(self, departure_station, arrival_station):
        # Поиск маршрутов, включающих указанные станции
        return list(self.routes_collection.find({
            'stations': {
                '$all': [departure_station, arrival_station]
            }
        }))

    def get_all_stations(self):
        # Получение списка всех станций
        return list(self.stations_collection.find())

    def get_all_routes(self):
        # Получение списка всех маршрутов
        return list(self.routes_collection.find())

    def drop_collections(self):
        # Очистка коллекций станций и маршрутов (для тестирования)
        self.stations_collection.drop()
        self.routes_collection.drop()
