import requests

import time

from datetime import datetime

API_URL = "https://blockstream.info/api"

def investigate_address(address):

    address = address.strip()

    if not address:

        return None

    print(f"\nInvestigating: {address}")

    try:

        # Get address statistics

        response = requests.get(

            f"{API_URL}/address/{address}",

            timeout=20

        )

        if response.status_code != 200:

            print("Could not retrieve this address.")

            return None

        data = response.json()

        confirmed = data["chain_stats"]

        mempool = data["mempool_stats"]

        received = confirmed["funded_txo_sum"] / 100000000

        sent = confirmed["spent_txo_sum"] / 100000000

        balance = received - sent

        unconfirmed = (

            mempool["funded_txo_sum"] -

            mempool["spent_txo_sum"]

        ) / 100000000

        transactions = confirmed["tx_count"]

        # Retrieve recent transactions

        tx_response = requests.get(

            f"{API_URL}/address/{address}/txs",

            timeout=20

        )

        tx_response.raise_for_status()

        tx_data = tx_response.json()

        latest_activity = "Unknown"

        for tx in tx_data:

            if tx["status"]["confirmed"]:

                timestamp = tx["status"]["block_time"]

                latest_activity = datetime.fromtimestamp(

                    timestamp

                ).strftime("%d %B %Y")

                break

        return {

            "address": address,

            "received": received,

            "sent": sent,

            "balance": balance,

            "unconfirmed": unconfirmed,

            "transactions": transactions,

            "latest_activity": latest_activity

        }

    except requests.exceptions.RequestException as error:

        print(f"Connection problem: {error}")

        return None

    except (KeyError, ValueError, TypeError) as error:

        print(f"Unexpected data received: {error}")

        return None

def main():

    print("\n===================================")

    print("       PROJECT LOST BITCOIN")

    print("   MULTIPLE ADDRESS INVESTIGATOR")

    print("===================================")

    print("\nEnter Bitcoin addresses below.")

    print("Enter one address per line.")

    print("Press ENTER on an empty line when finished.\n")

    addresses = []

    while True:

        address = input("Bitcoin address: ").strip()

        if not address:

            break

        addresses.append(address)

    if not addresses:

        print("\nNo addresses entered. Investigation cancelled.")

        return

    results = []

    print(f"\nStarting investigation of {len(addresses)} address(es)...")

    for address in addresses:

        result = investigate_address(address)

        if result:

            results.append(result)

        time.sleep(0.5)

    print("\n\n===================================")

    print("       INVESTIGATION REPORT")

    print("===================================")

    if not results:

        print("\nNo addresses could be investigated.")

        return

    total_balance = sum(item["balance"] for item in results)

    for number, item in enumerate(results, start=1):

        print(f"\nADDRESS #{number}")

        print("-----------------------------------")

        print(f"Address: {item['address']}")

        print(f"Total received: {item['received']:.8f} BTC")

        print(f"Total sent: {item['sent']:.8f} BTC")

        print(f"Confirmed balance: {item['balance']:.8f} BTC")

        print(f"Unconfirmed change: {item['unconfirmed']:.8f} BTC")

        print(f"Transactions: {item['transactions']}")

        print(f"Latest confirmed activity: {item['latest_activity']}")

        if item["balance"] > 0:

            print("FINDING: Positive confirmed balance.")

        else:

            print("FINDING: No confirmed balance remains.")

    print("\n===================================")

    print("       INVESTIGATION SUMMARY")

    print("===================================")

    print(f"\nAddresses successfully investigated: {len(results)}")

    print(f"Combined confirmed balance: {total_balance:.8f} BTC")

    positive = sum(1 for item in results if item["balance"] > 0)

    print(f"Addresses with positive balances: {positive}")

    print("\nIMPORTANT:")

    print("A blockchain balance does not prove ownership")

    print("or that the Bitcoin can be accessed.")

    print("Unconfirmed transactions are not included")

    print("in confirmed balances.")

    print("\nInvestigation complete.")

if __name__ == "__main__":

    main()