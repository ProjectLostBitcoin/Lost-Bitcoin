import json

import urllib.request

from urllib.error import HTTPError, URLError

from datetime import datetime, timezone

BASE_URL = "https://blockstream.info/api"

def api_request(endpoint):

    url = f"{BASE_URL}{endpoint}"

    request = urllib.request.Request(

        url,

        headers={"User-Agent": "LostBitcoinInvestigator/1.0"}

    )

    with urllib.request.urlopen(request, timeout=20) as response:

        return json.loads(response.read().decode("utf-8"))

def format_date(timestamp):

    if not timestamp:

        return "Not available"

    date = datetime.fromtimestamp(

        timestamp, tz=timezone.utc

    )

    return date.strftime("%d %B %Y")

def investigate_address(address):

    print("\nConnecting to Bitcoin blockchain...")

    # Request 1: Get address statistics

    data = api_request(f"/address/{address}")

    chain = data["chain_stats"]

    mempool = data["mempool_stats"]

    received = chain["funded_txo_sum"]

    spent = chain["spent_txo_sum"]

    pending_received = mempool["funded_txo_sum"]

    pending_spent = mempool["spent_txo_sum"]

    balance = received - spent

    pending_balance = pending_received - pending_spent

    # Request 2: Get recent transaction history

    print("Checking recent transaction activity...")

    history = api_request(f"/address/{address}/txs")

    latest_date = None

    if history:

        for tx in history:

            status = tx.get("status", {})

            if status.get("confirmed"):

                latest_date = status.get("block_time")

                break

    print("\n" + "=" * 50)

    print("PROJECT LOST BITCOIN")

    print("ADDRESS INVESTIGATION")

    print("=" * 50)

    print("\nAddress:", address)

    print(f"\nTotal BTC received: {received / 100000000:.8f}")

    print(f"Total BTC sent:     {spent / 100000000:.8f}")

    print(f"\nConfirmed balance:  {balance / 100000000:.8f}")

    print(

        f"Unconfirmed change: {pending_balance / 100000000:.8f}"

    )

    print("\nConfirmed transactions:", chain["tx_count"])

    print("Latest confirmed activity:", format_date(latest_date))

    print("\n" + "=" * 50)

    print("INVESTIGATION NOTES")

    print("=" * 50)

    if chain["tx_count"] == 0:

        print("No confirmed transactions found.")

    else:

        print("This address has confirmed blockchain activity.")

        if balance > 0:

            print("A positive balance remains at this address.")

        else:

            print("The confirmed balance is currently zero.")

        if spent > 0:

            print("Bitcoin has previously been spent from this address.")

        else:

            print("No confirmed spending recorded.")

    print("\nIMPORTANT:")

    print("A blockchain balance does not prove ownership")

    print("or that the Bitcoin can be accessed.")

    print("\nInvestigation complete.")

def main():

    print("\nWELCOME TO PROJECT LOST BITCOIN")

    address = input(

        "\nEnter a Bitcoin address to investigate: "

    ).strip()

    if not address:

        print("No address entered.")

        return

    try:

        investigate_address(address)

    except HTTPError as error:

        print("\nBlockchain API error:", error.code)

    except URLError:

        print("\nCould not connect to the Bitcoin blockchain.")

    except Exception as error:

        print("\nInvestigation error:", error)

if __name__ == "__main__":

    main()