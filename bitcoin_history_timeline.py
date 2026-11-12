import requests

import time

from datetime import datetime, timezone

API_URL = "https://blockstream.info/api"

BATCH_SIZE = 25

MAX_PAGES = 200

def format_date(timestamp):

    if not timestamp:

        return "Unknown"

    return datetime.fromtimestamp(

        timestamp,

        tz=timezone.utc

    ).strftime("%d %B %Y")

def get_address_statistics(address):

    response = requests.get(

        f"{API_URL}/address/{address}",

        timeout=20

    )

    response.raise_for_status()

    data = response.json()

    return data["chain_stats"]["tx_count"]

def get_complete_history(address):

    print("\nRetrieving transaction history...")

    print("This may take a little while for addresses")

    print("with extensive transaction histories.\n")

    all_transactions = []

    seen_txids = set()

    response = requests.get(

        f"{API_URL}/address/{address}/txs",

        timeout=30

    )

    response.raise_for_status()

    batch = response.json()

    if not batch:

        return all_transactions, True

    page = 1

    while batch:

        new_transactions = []

        for tx in batch:

            txid = tx.get("txid")

            if txid and txid not in seen_txids:

                seen_txids.add(txid)

                new_transactions.append(tx)

        all_transactions.extend(new_transactions)

        print(

            f"Retrieved {len(all_transactions)} transactions..."

        )

        if len(batch) < BATCH_SIZE:

            return all_transactions, True

        if page >= MAX_PAGES:

            print("\nSafety limit reached.")

            return all_transactions, False

        last_txid = batch[-1]["txid"]

        time.sleep(0.2)

        response = requests.get(

            f"{API_URL}/address/{address}/txs/chain/{last_txid}",

            timeout=30

        )

        response.raise_for_status()

        batch = response.json()

        page += 1

    return all_transactions, True

def analyze_history(transactions):

    confirmed = []

    for tx in transactions:

        status = tx.get("status", {})

        if status.get("confirmed") and status.get("block_time"):

            confirmed.append(status["block_time"])

    if not confirmed:

        return None, None, []

    earliest = min(confirmed)

    latest = max(confirmed)

    years = sorted({

        datetime.fromtimestamp(

            timestamp,

            tz=timezone.utc

        ).year

        for timestamp in confirmed

    })

    return earliest, latest, years

def main():

    print("\n" + "=" * 55)

    print("PROJECT LOST BITCOIN")

    print("HISTORICAL BITCOIN TIMELINE")

    print("=" * 55)

    address = input(

        "\nEnter a public Bitcoin address: "

    ).strip()

    if not address:

        print("No address entered.")

        return

    try:

        print("\nChecking address statistics...")

        total_confirmed = get_address_statistics(address)

        print(

            f"Blockchain reports {total_confirmed} "

            "confirmed transactions."

        )

        transactions, complete = get_complete_history(address)

        earliest, latest, years = analyze_history(transactions)

        print("\n" + "=" * 55)

        print("BITCOIN HISTORY REPORT")

        print("=" * 55)

        print(f"\nAddress: {address}")

        print(

            f"\nTransactions retrieved: {len(transactions)}"

        )

        print(

            f"Transactions recorded by blockchain: "

            f"{total_confirmed}"

        )

        if complete and len(transactions) == total_confirmed:

            print("\nHistory coverage: COMPLETE")

        else:

            print("\nHistory coverage: INCOMPLETE")

            print(

                "Do not treat the earliest date below as "

                "the address's first-ever activity."

            )

        if earliest and latest:

            print("\n--- ACTIVITY TIMELINE ---")

            print(

                f"First confirmed activity: "

                f"{format_date(earliest)}"

            )

            print(

                f"Most recent confirmed activity: "

                f"{format_date(latest)}"

            )

            print("\n--- ACTIVE YEARS ---")

            for year in years:

                count = sum(

                    1 for tx in transactions

                    if tx.get("status", {}).get("confirmed")

                    and tx.get("status", {}).get("block_time")

                    and datetime.fromtimestamp(

                        tx["status"]["block_time"],

                        tz=timezone.utc

                    ).year == year

                )

                print(f"{year}: {count} confirmed transactions")

        else:

            print("\nNo confirmed transaction dates were found.")

        print("\n--- INVESTIGATION NOTES ---")

        if complete:

            print(

                "The retrieved history matches the blockchain's "

                "confirmed transaction count."

            )

        else:

            print(

                "The history scan did not retrieve every "

                "confirmed transaction."

            )

        print(

            "\nThis timeline describes one Bitcoin address, "

            "not necessarily an entire wallet or exchange account."

        )

        print(

            "Transaction activity does not establish who owns "

            "the address or whether funds are accessible."

        )

        print("\nInvestigation complete.")

    except requests.exceptions.RequestException as error:

        print(f"\nNetwork or API error: {error}")

    except (KeyError, ValueError, TypeError) as error:

        print(f"\nCould not interpret the returned data: {error}")

if __name__ == "__main__":

    main()

