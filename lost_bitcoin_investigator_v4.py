
print("\n======================================")

print("       LOST BITCOIN INVESTIGATOR")

print("======================================")

print("\nLet's investigate what may have happened to your Bitcoin.")

print("Answer as accurately as you can. It's okay if you don't know.\n")

def ask(question, options=None):

    print("\n" + question)

    if options:

        for number, option in enumerate(options, 1):

            print(f"  {number}. {option}")

        while True:

            answer = input("\nEnter the number of your answer: ").strip()

            if answer.isdigit() and 1 <= int(answer) <= len(options):

                return options[int(answer) - 1]

            print("Please enter one of the listed numbers.")

    return input("\nYour answer: ").strip()

answers = {}

answers["starting_point"] = ask(

    "Where do you think your Bitcoin originally came from?",

    [

        "I bought it through an exchange",

        "I stored it in a wallet on a computer",

        "I stored it in a mobile or online wallet",

        "Someone sent Bitcoin to me",

        "I mined Bitcoin",

        "I'm really not sure"

    ]

)

if answers["starting_point"] == "I bought it through an exchange":

    print("\n--- EXCHANGE INVESTIGATION ---")

    answers["exchange"] = ask(

        "What was the name of the exchange or website?"

    )

    answers["year"] = ask(

        "Approximately when did you use this exchange?",

        [

            "2009–2011",

            "2012–2013",

            "2014–2015",

            "2016–2017",

            "2018–2020",

            "2021 or later",

            "I don't remember"

        ]

    )

    answers["purchase_type"] = ask(

        "How did Bitcoin first enter your exchange account?",

        [

            "I bought Bitcoin directly using money",

            "Someone transferred Bitcoin to me",

            "Both",

            "I don't remember"

        ]

    )

    answers["email_access"] = ask(

        "Can you still access the email account you used with this exchange?",

        [

            "Yes, I can access it",

            "I remember the email address but cannot access it",

            "No, I don't remember which email I used",

            "I'm not sure"

        ]

    )

    answers["email_evidence"] = ask(

        "Do you remember receiving emails from the exchange?",

        [

            "Yes, purchase confirmations or transaction emails",

            "Yes, but mostly newsletters or account notifications",

            "I might have",

            "No, I don't remember receiving any"

        ]

    )

    answers["withdrawal"] = ask(

        "Do you remember ever moving Bitcoin OUT of this exchange?",

        [

            "Yes, I withdrew it to another wallet",

            "No, I believe it stayed on the exchange",

            "I may have, but I'm not sure",

            "I don't remember"

        ]

    )

    answers["account_access"] = ask(

        "Can you still log in to the exchange account?",

        [

            "Yes",

            "I can access the email but not the account",

            "I remember the account but cannot access it",

            "The website appears to be gone or unavailable",

            "I don't know"

        ]

    )

    answers["records"] = ask(

        "Do you have any old records that might relate to the purchase?",

        [

            "Bank or credit card statements",

            "Old transaction records or screenshots",

            "Old computer, hard drive, or USB backup",

            "Several of these",

            "None that I know of"

        ]

    )

    print("\n\n======================================")

    print("       YOUR INVESTIGATION PLAN")

    print("======================================")

    print(f"\nExchange remembered: {answers['exchange']}")

    print(f"Approximate period: {answers['year']}")

    priorities = []

    if answers["email_access"] == "Yes, I can access it":

        priorities.append((

            "1. SEARCH YOUR OLD EMAIL",

            "Search for the exchange name, its old website domain, "

            "'Bitcoin', 'BTC', 'deposit', 'withdrawal', 'purchase', "

            "and 'verification'. Look for dated account and transaction "

            "records. Do not share your email password."

        ))

    elif answers["email_access"] != "I'm not sure":

        priorities.append((

            "1. IDENTIFY YOUR ORIGINAL EMAIL ACCOUNT",

            "Work out which email address you used and whether the "

            "provider has a legitimate account-recovery process. "

            "Do not give your password to a recovery service."

        ))

    if answers["account_access"] == "Yes":

        priorities.append((

            "2. CHECK THE EXCHANGE ACCOUNT",

            "Visit the exchange using a verified official website. "

            "Check account history, balances, deposits, withdrawals, "

            "and any available transaction statements."

        ))

    else:

        priorities.append((

            "2. INVESTIGATE THE EXCHANGE'S ACCOUNT STATUS",

            "Identify the exchange's historical website and current "

            "status. Find its legitimate account-recovery or claims "

            "information, if one exists. Do not assume an old exchange "

            "still operates or can return funds."

        ))

    if answers["withdrawal"] == "Yes, I withdrew it to another wallet":

        priorities.append((

            "3. TRACE THE WITHDRAWAL",

            "Look for the withdrawal confirmation and destination "

            "Bitcoin address. A transaction ID or address can help "

            "establish where the Bitcoin went. Never share a seed phrase "

            "or private key."

        ))

    elif answers["withdrawal"] in ["I may have, but I'm not sure",

                                    "I don't remember"]:

        priorities.append((

            "3. ESTABLISH WHETHER BITCOIN LEFT THE EXCHANGE",

            "Search old emails and account records for withdrawal "

            "confirmations. This is important because Bitcoin may have "

            "been moved to a separate wallet."

        ))

    else:

        priorities.append((

            "3. CHECK WHETHER BITCOIN REMAINED ON THE EXCHANGE",

            "Look for account balances, transaction history, and "

            "withdrawal records. Do not assume a historical purchase "

            "means Bitcoin is still held there."

        ))

    if answers["records"] != "None that I know of":

        priorities.append((

            "4. COLLECT YOUR OLD RECORDS",

            "Preserve relevant bank statements, screenshots, computer "

            "backups, and transaction records. Work from copies where "

            "possible; do not modify original files."

        ))

    if answers["purchase_type"] in [

        "I bought Bitcoin directly using money", "Both"

    ]:

        priorities.append((

            "5. VERIFY THE ORIGINAL PURCHASE",

            "Look for bank or card payments and matching exchange "

            "purchase records. A payment to an exchange is useful "

            "evidence, but does not by itself prove a Bitcoin balance."

        ))

    print("\nBased on your answers, here's where I would start:\n")

    for title, detail in priorities:

        print(title)

        print(detail + "\n")

    print("IMPORTANT:")

    print("This investigation can help locate evidence and identify "

          "possible recovery routes. It cannot guarantee that Bitcoin "

          "still exists or can be recovered.")

    print("\nNever enter or share your seed phrase or private keys "

          "with this investigator or an unknown recovery service.")

elif answers["starting_point"] == "I stored it in a wallet on a computer":

    print("\n--- COMPUTER WALLET INVESTIGATION ---")

    answers["computer"] = ask(

        "Which computer did you originally use?",

        ["Mac", "Windows PC", "Linux", "I don't remember"]

    )

    answers["wallet"] = ask(

        "Do you remember the wallet software?",

        ["Bitcoin Core", "Electrum", "MultiBit", "Armory",

         "Another wallet", "I don't remember"]

    )

    answers["device"] = ask(

        "Do you still have the original computer or its hard drive?",

        ["Yes", "I have a backup or external drive",

         "No", "I'm not sure"]

    )

    answers["backup"] = ask(

        "Do you remember making a wallet backup?",

        ["Yes", "No", "Maybe"]

    )

    print("\n--- YOUR FIRST INVESTIGATION STEPS ---")

    print("1. Identify the original computer and wallet software.")

    print("2. Preserve the original drive. Avoid reinstalling or resetting it.")

    print("3. Search for wallet files and backups using a read-only process.")

    print("4. Look for old emails, notes, and records that identify the wallet.")

    print("5. Never upload wallet files, seed phrases, or private keys "

          "to an unknown service.")

elif answers["starting_point"] == "I stored it in a mobile or online wallet":

    print("\n--- MOBILE / ONLINE WALLET INVESTIGATION ---")

    answers["wallet"] = ask("Do you remember the wallet app or website?")

    answers["phone"] = ask(

        "Do you still have the original phone or device?",

        ["Yes", "No", "I have a backup", "I'm not sure"]

    )

    answers["backup"] = ask(

        "Do you remember saving a recovery phrase or wallet backup?",

        ["Yes", "No", "Maybe"]

    )

    print("\n--- YOUR FIRST INVESTIGATION STEPS ---")

    print("1. Identify the original wallet app or service.")

    print("2. Check whether the original device or backup still exists.")

    print("3. Search email and records for account setup or transactions.")

    print("4. Use only verified official recovery instructions.")

    print("5. Never share your recovery phrase or private keys.")

else:

    print("\n--- LET'S NARROW DOWN THE SEARCH ---")

    answers["period"] = ask(

        "When do you think you first encountered Bitcoin?",

        ["2009–2012", "2013–2015", "2016–2018",

         "2019 or later", "I don't know"]

    )

    answers["evidence"] = ask(

        "What might you still have access to?",

        ["Old email", "Old computer or hard drive",

         "Wallet backup", "Bank records", "Several of these", "None"]

    )

    print("\nYour next step is to identify the strongest surviving evidence.")

    print("We'll use that to narrow down whether to investigate an "

          "exchange, a wallet, or a transaction history.")

print("\n======================================")

print("Investigation session complete.")

print("Your answers have not been uploaded or sent anywhere.")

print("======================================\n")

