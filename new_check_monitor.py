from api_client import Client
from config import POSTER_TOKEN
import time
from datetime import date


def run_monitor(timeout: int, new_transaction_callback=None):
    client = Client(POSTER_TOKEN)
    processed_checks = set()
    # total_payed = 0
    while True:
        response = client.get_transactions(date.today().strftime("%Y-%m-%d"))
        response.reverse()
        for check in response:
            if check["transaction_id"] not in processed_checks:
                client_id = check["client_id"]
                payed_sum = check["payed_sum"]
                transaction_id = check["transaction_id"]
                print("----New transaction-----")
                print(transaction_id, payed_sum, client_id)

                # total_payed += float(payed_sum)

                # print("New Total ->", round(total_payed, 2))
                print("------------------------\n")

                if new_transaction_callback:
                    new_transaction_callback(client_id, payed_sum, transaction_id)

                processed_checks.add(transaction_id)
        time.sleep(timeout)


if __name__ == "__main__":
    run_monitor(2)
