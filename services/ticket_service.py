class TicketService:
    def __init__(self, mongo_client, database_name, hazelcast_instance):
        self.client = mongo_client
        self.db = self.client[database_name]
        self.tickets_collection = self.db['tickets']
        self.hazelcast = hazelcast_instance

    def initialize_tickets(self, tickets_data):
        # Инициализация данных о билетах
        self.tickets_collection.insert_many(tickets_data)

    def buy_ticket(self, train_id, seat_number, user_id):
        # Покупка билета
        ticket = {
            'train_id': train_id,
            'seat_number': seat_number,
            'user_id': user_id,
            'status': 'blocked'
        }

        # Попытка блокировки места
        if self.block_ticket(train_id, seat_number):
            print('before insert')
            self.tickets_collection.insert_one(ticket)
            print('after_insert ')
            return ticket

        return None  # Не удалось заблокировать место

    def block_ticket(self, train_id, seat_number):
        # Блокировка места на поезде
        lock_key = f'{train_id}:{seat_number}'
        if self.hazelcast.get_lock(lock_key).try_lock():
            return True
        return False  # Место уже заблокировано

    def unlock_ticket(self, train_id, seat_number):
        # Снятие блокировки с места
        lock_key = f'{train_id}:{seat_number}'
        self.hazelcast.get_lock(lock_key).unlock()

    def pay_ticket(self, ticket_id):
        # Оплата билета и изменение его статуса
        ticket = self.tickets_collection.find_one({'_id': ticket_id})
        if ticket and ticket['status'] == 'blocked':
            self.tickets_collection.update_one(
                {'_id': ticket_id},
                {'$set': {'status': 'paid'}}
            )
            self.unlock_ticket(ticket['train_id'], ticket['seat_number'])
            return True
        return False  # Билет не найден или уже оплачен

    def get_tickets_for_user(self, user_id):
        # Получение списка билетов для пользователя
        return list(self.tickets_collection.find({'user_id': user_id}))

    def drop_collection(self):
        # Очистка коллекции билетов (для тестирования)
        self.tickets_collection.drop()
