
def ask_question(question, options):

    print("\n" + question)

    for number, option in enumerate(options, start=1):

        print(f"  {number}. {option}")

    while True:

        answer = input("\nEnter the number of your answer: ").strip()

        if answer.isdigit() and 1 <= int(answer) <= len(options):

            return options[int(answer) - 1]

        print("Please enter one of the listed numbers.")

def main():

    print("\n" + "=" * 45)

    print("       PROJECT LOST BITCOIN")

    print("       Guided Investigation")

    print("=" * 45)

    print(

        "\nWe'll use what you remember to suggest "

        "where to investigate first."

    )

    history = ask_question(

        "1. What do you remember about your Bitcoin?",

        [

            "I bought it through a website or exchange",

            "I stored it in a computer wallet",

            "Someone sent it to me",

            "I mined it",

            "I bought it but cannot remember how",

            "I'm not sure",

        ],

    )

    year = ask_question(

        "\n2. Approximately when did this happen?",

        [

            "Before 2012",

            "2012–2015",

            "2016–2019",

            "2020 or later",

            "I don't remember",

        ],

    )

    access = ask_question(

        "3. What do you still have access to?",

        [

            "My old email account",

            "An old computer, hard drive, or USB drive",

            "An old wallet file or backup",

            "An exchange account",

            "Several of these",

            "None of these or I'm unsure",

        ],

    )

    print("\n" + "=" * 45)

    print("       YOUR INVESTIGATION PLAN")

    print("=" * 45)

    print(f"\nWhat you remember: {history}")

    print(f"Approximate period: {year}")

    print(f"Available evidence: {access}")

    print("\nRECOMMENDED NEXT STEPS\n")

    if "website or exchange" in history:

        print("1. Search old emails for exchange account evidence.")

    elif "computer wallet" in history:

        print("1. Look for wallet files and backups on your own devices.")

    elif "mined it" in history:

        print("1. Investigate any old mining software, wallet files,")

        print("   and records of where mining payouts were sent.")

    elif "sent it" in history:

        print("1. Look for the receiving wallet or transaction records.")

    else:

        print("1. Start by searching historical email and purchase records.")

    if "email" in access or "Several" in access:

        print("2. Email investigation may help identify historical exchanges.")

    if any(word in access for word in ["computer", "drive", "USB", "wallet", "backup", "Several"]):

        print("3. Inspect relevant files and backups for wallet evidence.")

    if "None" in access:

        print("2. Make a list of old email addresses, devices,")

        print("   exchanges, and people who may help you remember.")

    print("\nIMPORTANT")

    print(

        "These recommendations are starting points, not proof "

        "that Bitcoin exists or can be recovered."

    )

    print(

        "\nNever share your wallet recovery phrase, private keys, "

        "or email password with this program or another person."

    )

    print("\nThank you for trying Project Lost Bitcoin!")

if __name__ == "__main__":

    main()

