
from pathlib import Path

from datetime import datetime

import csv

PROJECT_DIR = Path.home() / "lost-bitcoin-project"

TEST_DIR = PROJECT_DIR / "test_files"

REPORT_FILE = PROJECT_DIR / "lost_bitcoin_report.csv"

# Filename clues only. These are leads, not proof of a wallet.

WALLET_KEYWORDS = [

    "wallet.dat",

    "wallet",

    "bitcoin",

    "bitcoin-core",

    "multibit",

    "electrum",

    "armory",

    "blockchain",

    "btc",

]

def main():

    TEST_DIR.mkdir(parents=True, exist_ok=True)

    findings = []

    print("\nPROJECT LOST BITCOIN")

    print("Initial Wallet File Scanner")

    print("-" * 40)

    print(f"Test folder: {TEST_DIR}\n")

    for path in TEST_DIR.rglob("*"):

        if not path.is_file():

            continue

        filename = path.name.lower()

        if not any(word in filename for word in WALLET_KEYWORDS):

            continue

        try:

            stat = path.stat()

            findings.append({

                "filename": path.name,

                "location": str(path.relative_to(TEST_DIR)),

                "size_bytes": stat.st_size,

                "last_modified": datetime.fromtimestamp(

                    stat.st_mtime

                ).isoformat(timespec="seconds"),

                "finding": (

                    "Filename matches a search clue; "

                    "contents have not been examined."

                ),

            })

            print(f"Potential lead: {path.name}")

            print(f"  Size: {stat.st_size:,} bytes")

            print(f"  Location: {path.relative_to(TEST_DIR)}\n")

        except OSError as error:

            print(f"Could not inspect {path.name}: {error}")

    with REPORT_FILE.open("w", newline="", encoding="utf-8") as file:

        columns = [

            "filename",

            "location",

            "size_bytes",

            "last_modified",

            "finding",

        ]

        writer = csv.DictWriter(file, fieldnames=columns)

        writer.writeheader()

        writer.writerows(findings)

    print("-" * 40)

    print(f"Scan complete. Potential leads found: {len(findings)}")

    print(f"Report saved to: {REPORT_FILE}")

    print("\nImportant: A matching filename does not prove")

    print("that a wallet or recoverable Bitcoin exists.")

if __name__ == "__main__":

    main()

