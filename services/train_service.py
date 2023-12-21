class TrainService:
    def __init__(self, mongo_client, database_name):
        self.client = mongo_client
        self.db = self.client[database_name]
        self.trains_collection = self.db['trains']

    def initialize_trains(self, trains_data):
        # Инициализация данных о поездах
        self.trains_collection.insert_many(trains_data)

    def assign_train_to_route(self, train_data):
        # Назначение поезда на маршрут на указанную дату
        self.trains_collection.insert_one(train_data)

    def get_train_by_id(self, train_id):
        # Поиск поезда по идентификатору
        return self.trains_collection.find_one({'id': train_id})

    def get_trains_for_route(self, route_id, departure_date):
        # Поиск поездов для указанного маршрута и даты
        return list(self.trains_collection.find({
            'route_id': route_id,
            'departure_date': departure_date
        }))

    def decrease_available_tickets(self, train_id):
        # Уменьшение доступного количества билетов на поезде
        self.trains_collection.update_one(
            {'id': train_id},
            {'$inc': {'available_tickets': -1}}
        )

    def increase_available_tickets(self, train_id):
        # Увеличение доступного количества билетов на поезде (например, при отмене брони)
        self.trains_collection.update_one(
            {'id': train_id},
            {'$inc': {'available_tickets': 1}}
        )

    def drop_collection(self):
        # Очистка коллекции поездов (для тестирования)
        self.trains_collection.drop()
