import logging
from requests import Session

# Настройка логгера
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Client:
    def __init__(self, token):
        self.token = token
        self.session = Session()

    def get_transactions(self, date: str, amount: int = 1000, page: int = 1):
        logger.info(f"Fetching transactions for date: {date}, page: {page}")
        response = self.session.get(
            "https://joinposter.com/api/transactions.getTransactions",
            params={
                "token": self.token,
                "date_from": date,
                "date_to": date,
                "page": page,
                "per_page": amount
            }
        )
        data = response.json()
        logger.debug(f"Transactions response: {data}")
        return data['response']['data']

    def get_client_by_id(self, client_id: int):
        logger.info(f"Fetching client by ID: {client_id}")
        response = self.session.get(
            "https://joinposter.com/api/clients.getClient",
            params={
                "token": self.token,
                "client_id": client_id
            }
        )
        data = response.json()
        logger.debug(f"Client by ID response: {data}")
        return data['response'][0]

    def get_item_by_id(self, item_id: int):
        logger.info(f"Fetching item by ID: {item_id}")
        response = self.session.get(
            "https://joinposter.com/api/menu.getProduct",
            params={
                "token": self.token,
                "product_id": item_id
            }
        )
        data = response.json()
        logger.debug(f"Item response: {data}")
        return data['response']

    def create_new_client(self, name: str, phone: str, card_number: str, group_id: int = 8):
        logger.info(f"Creating new client: {name}, phone: {phone}")
        response = self.session.post(
            "https://joinposter.com/api/clients.createClient",
            params={
                "token": self.token
            },
            json={
                "client_name": name,
                "client_groups_id_client": group_id,
                "phone": phone,
                "comment": "from telegram",
                "card_number": card_number
            }
        )
        data = response.json()
        logger.debug(f"Create client response: {data}")
        return data

    def modify_existing_client(self, client_id: int, card_number: str):
        logger.info(f"Modification of client {client_id}")
        response = self.session.post(
            "https://joinposter.com/api/clients.updateClient",
            params={
                "token": self.token
            },
            json={
                "client_id": client_id,
                "card_number": card_number
            }
        )
        data = response.json()
        logger.debug(f"Modify client response: {data}")
        return data

    def get_client_by_phone(self, phone: str):
        logger.info(f"Searching client by phone: {phone}")
        response = self.session.get(
            "https://joinposter.com/api/clients.getClients",
            params={
                "token": self.token,
                "phone": phone
            }
        )

        data = response.json().get('response', [])
        logger.debug(f"Client search response: {data}")
        return data[0] if data else None
