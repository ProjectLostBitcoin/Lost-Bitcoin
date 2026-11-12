import requests

from datetime import datetime

API_URL = "https://blockstream.info/api"

SATOSHIS_PER_BTC = 100_000_000

def btc(satoshis):

    return satoshis / SATOSHIS_PER_BTC

def get_address_summary(address):

    """Retrieve confirmed address statistics from the blockchain."""

    response = requests.get(

        f"{API_URL}/address/{address}",

        timeout=20

    )

    response.raise_for_status()

    data = response.json()

    stats = data["chain_stats"]

    received = btc(stats["funded_txo_sum"])

    transferred_out = btc(stats["spent_txo_sum"])

    balance = received - transferred_out

    return {

        "received": received,

        "transferred_out": transferred_out,

        "balance": balance,

        "transactions": stats["tx_count"]

    }

def get_recent_transactions(address):

    """Retrieve the most recent transactions returned by the API."""

    response = requests.get(

        f"{API_URL}/address/{address}/txs",

        timeout=20

    )

    response.raise_for_status()

    return response.json()

def display_transaction_details(transactions):

    """Display transaction inputs and outputs when requested."""

    print("\n" + "=" * 55)

    print("TRANSACTION HISTORY")

    print("=" * 55)

    if not transactions:

        print("\nNo transactions were returned.")

        return

    for number, tx in enumerate(transactions, start=1):

        status = tx.get("status", {})

        if status.get("confirmed"):

            timestamp = status.get("block_time")

            if timestamp:

                date = datetime.fromtimestamp(

                    timestamp

                ).strftime("%d %b %Y")

            else:

                date = "Date unavailable"

        else:

            date = "Unconfirmed"

        print(f"\nTRANSACTION #{number}")

        print("-" * 45)

        print(f"Date: {date}")

        print(f"Transaction ID: {tx.get('txid', 'Unknown')}")

        print("\nINPUTS:")

        for item in tx.get("vin", []):

            previous_output = item.get("prevout") or {}

            value = btc(previous_output.get("value", 0))

            source = previous_output.get("scriptpubkey_address")

            print(f"  Amount: {value:.8f} BTC")

            print(f"  Source address: {source or 'Not available'}")

        print("\nOUTPUTS:")

        for item in tx.get("vout", []):

            value = btc(item.get("value", 0))

            destination = item.get("scriptpubkey_address")

            print(f"  Amount: {value:.8f} BTC")

            print(

                f"  Destination address: "

                f"{destination or 'Not available'}"

            )

def main():

    print("\n" + "=" * 55)

    print("PROJECT LOST BITCOIN")

    print("BITCOIN ADDRESS INVESTIGATION")

    print("=" * 55)

    address = input(

        "\nEnter a public Bitcoin address to investigate: "

    ).strip()

    if not address:

        print("No address entered. Investigation cancelled.")

        return

    try:

        print("\nRetrieving blockchain information...")

        summary = get_address_summary(address)

        print("\n" + "=" * 55)

        print("ACCOUNT SUMMARY")

        print("=" * 55)

        print(f"\nAddress: {address}")

        print(f"\nTotal BTC received:       {summary['received']:.8f} BTC")

        print(

            f"Total BTC transferred out: "

            f"{summary['transferred_out']:.8f} BTC"

        )

        print(

            f"Current confirmed balance: "

            f"{summary['balance']:.8f} BTC"

        )

        print(f"Confirmed transactions:    {summary['transactions']}")

        print("\n" + "-" * 55)

        print("INVESTIGATION FINDINGS")

        print("-" * 55)

        if summary["balance"] > 0:

            print("This address has a positive confirmed balance.")

            print(

                "Further investigation is needed to determine whether "

                "the funds are accessible to you."

            )

        elif summary["transactions"] > 0:

            print("This address has transaction history but no")

            print("confirmed balance remaining.")

            print(

                "Its history may contain useful leads for further "

                "investigation."

            )

        else:

            print("No confirmed transactions were reported for this address.")

            print("Double-check the address and any related records.")

        print("\n" + "-" * 55)

        print("Would you like to inspect the transaction history?")

        print(f"{summary['transactions']} confirmed transactions are recorded.")

        print("The public API returns up to 25 recent transactions at a time.")

        choice = input("\nView recent transaction details? (yes/no): ").strip().lower()

        if choice in ("yes", "y"):

            transactions = get_recent_transactions(address)

            display_transaction_details(transactions)

        else:

            print("\nTransaction details skipped.")

        print("\n" + "=" * 55)

        print("IMPORTANT NOTES")

        print("=" * 55)

        print(

            "These figures describe one Bitcoin address, not necessarily "

            "an entire wallet or exchange account."

        )

        print(

            "Bitcoin transferred out is not necessarily lost; it may have "

            "moved to another address controlled by the same person."

        )

        print(

            "Blockchain data alone cannot establish ownership or access."

        )

        print(

            "Unconfirmed transactions are not included in the confirmed "

            "balance shown above."

        )

        print("\nInvestigation complete.")

    except requests.exceptions.RequestException as error:

        print(f"\nNetwork or blockchain API error: {error}")

    except (KeyError, ValueError, TypeError) as error:

        print(f"\nCould not interpret the returned data: {error}")

if __name__ == "__main__":

    main()