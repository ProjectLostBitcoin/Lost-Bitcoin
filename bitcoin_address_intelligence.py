import requests

from datetime import datetime

API_URL = "https://blockstream.info/api"

# The Bitcoin Genesis address has a special, unspendable

# 50 BTC block reward. Its reported balance is not recoverable.

GENESIS_ADDRESS = "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa"

def investigate_address(address):

    address = address.strip()

    print("\n" + "=" * 55)

    print("PROJECT LOST BITCOIN — ADDRESS INTELLIGENCE")

    print("=" * 55)

    print(f"\nInvestigating: {address}")

    try:

        response = requests.get(

            f"{API_URL}/address/{address}",

            timeout=20

        )

        if response.status_code != 200:

            print("\nRESULT: Unable to investigate this address.")

            print("Check the address and try again.")

            return

        data = response.json()

        confirmed = data["chain_stats"]

        mempool = data["mempool_stats"]

        received = confirmed["funded_txo_sum"] / 100000000

        sent = confirmed["spent_txo_sum"] / 100000000

        balance = received - sent

        transactions = confirmed["tx_count"]

        unconfirmed = (

            mempool["funded_txo_sum"]

            - mempool["spent_txo_sum"]

        ) / 100000000

        # Retrieve recent transactions for the activity date.

        tx_response = requests.get(

            f"{API_URL}/address/{address}/txs",

            timeout=20

        )

        tx_response.raise_for_status()

        recent_transactions = tx_response.json()

        latest_activity = "No confirmed activity found"

        for tx in recent_transactions:

            if tx["status"]["confirmed"]:

                timestamp = tx["status"].get("block_time")

                if timestamp:

                    latest_activity = datetime.fromtimestamp(

                        timestamp

                    ).strftime("%d %B %Y")

                break

        # Classify the findings.

        if address == GENESIS_ADDRESS:

            classification = "SPECIAL WARNING"

            explanation = (

                "This is the Bitcoin Genesis address. Its original "

                "50 BTC block reward is permanently unspendable. "

                "The reported address balance must not be treated "

                "as recoverable Bitcoin."

            )

        elif balance > 0:

            classification = "POSITIVE CONFIRMED BALANCE"

            explanation = (

                "The blockchain reports a positive confirmed balance. "

                "This is a lead, not proof of ownership or access. "

                "Further investigation is needed."

            )

        elif transactions > 0:

            classification = "HISTORICAL ACTIVITY — NO BALANCE"

            explanation = (

                "This address has confirmed transaction history, "

                "but no confirmed balance remains. Its transaction "

                "history may provide useful leads for further research."

            )

        else:

            classification = "NO CONFIRMED TRANSACTION HISTORY"

            explanation = (

                "No confirmed transactions were reported for this "

                "address. Double-check the address and investigate "

                "other evidence if available."

            )

        # Display the report.

        print("\n--- BLOCKCHAIN FACTS ---")

        print(f"Total received:       {received:.8f} BTC")

        print(f"Total sent:           {sent:.8f} BTC")

        print(f"Confirmed balance:    {balance:.8f} BTC")

        print(f"Unconfirmed change:   {unconfirmed:.8f} BTC")

        print(f"Confirmed transactions: {transactions}")

        print(f"Latest confirmed activity: {latest_activity}")

        print("\n--- INTELLIGENCE ASSESSMENT ---")

        print(f"Classification: {classification}")

        print(f"\nWhat this means:\n{explanation}")

        print("\n--- NEXT INVESTIGATION STEP ---")

        if address == GENESIS_ADDRESS:

            print(

                "Do not treat the reported balance as recoverable. "

                "Investigate other addresses or wallet records."

            )

        elif balance > 0:

            print(

                "Look for evidence connecting this address to a wallet "

                "or account you owned. Never share private keys or "

                "recovery phrases."

            )

        elif transactions > 0:

            print(

                "Review transaction history for related addresses, "

                "old exchange records, or other evidence. A related "

                "address does not automatically belong to the same person."

            )

        else:

            print(

                "Verify the address and search for additional records."

            )

        print("\n--- IMPORTANT LIMITATIONS ---")

        print(

            "Blockchain data cannot identify the owner of an address "

            "by itself."

        )

        print(

            "A positive balance does not prove you control the funds."

        )

        print(

            "Unconfirmed transactions can change and are excluded "

            "from the confirmed balance."

        )

        print("\nInvestigation complete.")

    except requests.exceptions.RequestException as error:

        print(f"\nNetwork or API error: {error}")

    except (KeyError, ValueError, TypeError) as error:

        print(f"\nCould not interpret the returned data: {error}")

def main():

    print("\nPROJECT LOST BITCOIN")

    print("ADDRESS INTELLIGENCE ENGINE")

    print("-" * 35)

    address = input(

        "\nEnter a public Bitcoin address to investigate: "

    ).strip()

    if not address:

        print("No address entered. Investigation cancelled.")

        return

    investigate_address(address)

if __name__ == "__main__":

    main()