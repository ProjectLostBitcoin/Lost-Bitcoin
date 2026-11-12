
import json

import urllib.request

from datetime import datetime, timezone

BASE_URL = "https://blockstream.info/api"

def get_block_height(height):

    url = f"{BASE_URL}/block-height/{height}"

    with urllib.request.urlopen(url, timeout=20) as response:

        return response.read().decode("utf-8").strip()

def get_block_details(block_hash):

    url = f"{BASE_URL}/block/{block_hash}"

    with urllib.request.urlopen(url, timeout=20) as response:

        return json.loads(response.read().decode("utf-8"))

def main():

    print("=" * 50)

    print("PROJECT LOST BITCOIN")

    print("Historical Blockchain Research")

    print("=" * 50)

    sample_heights = [0, 1, 100, 1000, 10000]

    for height in sample_heights:

        try:

            block_hash = get_block_height(height)

            block = get_block_details(block_hash)

            timestamp = datetime.fromtimestamp(

                block["timestamp"], tz=timezone.utc

            )

            print(f"\nBlock height: {block['height']}")

            print(f"Date (UTC):   {timestamp}")

            print(f"Block hash:   {block['id']}")

            print(f"Transactions: {block['tx_count']}")

        except Exception as error:

            print(f"\nCould not retrieve block {height}: {error}")

    print("\nResearch experiment complete.")

if __name__ == "__main__":

    main()

