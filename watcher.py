import time
import json
import requests
from datetime import datetime

ETHERSCAN_API_KEY = 'YourEtherscanAPIKeyHere'
CHECK_INTERVAL = 60 * 60  # Проверка каждый час
WALLETS_FILE = 'wallets.txt'
LOG_FILE = 'activity_log.json'


def load_wallets():
    with open(WALLETS_FILE, 'r') as f:
        return [line.strip() for line in f if line.strip()]


def get_last_tx_time(wallet):
    url = f'https://api.etherscan.io/api?module=account&action=txlist&address={wallet}&sort=desc&apikey={ETHERSCAN_API_KEY}'
    try:
        response = requests.get(url)
        data = response.json()
        if data['status'] != '1' or not data['result']:
            return None
        last_tx = data['result'][0]
        return int(last_tx['timeStamp'])
    except Exception as e:
        print(f"Error fetching transactions for {wallet}: {e}")
        return None


def load_activity_log():
    try:
        with open(LOG_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_activity_log(log):
    with open(LOG_FILE, 'w') as f:
        json.dump(log, f, indent=2)


def notify(wallet, timestamp):
    dt = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
    print(f"[ALERT] Activity detected on wallet {wallet} at {dt}")


def main():
    wallets = load_wallets()
    activity_log = load_activity_log()

    for wallet in wallets:
        last_seen = activity_log.get(wallet)
        current_last_tx = get_last_tx_time(wallet)

        if current_last_tx and (last_seen is None or int(last_seen) < current_last_tx):
            notify(wallet, current_last_tx)
            activity_log[wallet] = current_last_tx

    save_activity_log(activity_log)


if __name__ == '__main__':
    while True:
        print(f"[{datetime.utcnow()}] Checking wallets...")
        main()
        print(f"Sleeping for {CHECK_INTERVAL // 60} minutes...\n")
        time.sleep(CHECK_INTERVAL)
