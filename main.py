from api_client import Client
from pprint import pprint

client = Client("719003:7133379a09485d11325fca0b7a93f3c3")

# data = client.get_transactions("2025-05-15")
# data = client.get_client_by_id(1)
# data = client.get_item_by_id(6)
# data = client.create_new_client("Maksim test", "+380978766776")
# data = client.get_client_by_phone("+380974278613")
# data = client.modify_existing_client(21, "55555")
pprint(data)