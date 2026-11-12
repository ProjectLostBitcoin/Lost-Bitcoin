
def question(prompt, options):

    print("\n" + prompt)

    for i, option in enumerate(options, 1):

        print(f"{i}. {option}")

    while True:

        answer = input("\nChoose a number: ").strip()

        if answer.isdigit() and 1 <= int(answer) <= len(options):

            return int(answer)

        print("Please choose one of the listed numbers.")

def main():

    print("\n" + "=" * 50)

    print("       PROJECT LOST BITCOIN")

    print("       YOUR PERSONAL INVESTIGATOR")

    print("=" * 50)

    print("\nLet's investigate what happened to your Bitcoin.")

    print("I'll guide you through this one step at a time.")

    history = question(

        "What do you remember about your Bitcoin?",

        [

            "I stored it in a computer wallet",

            "I bought it through a website or exchange",

            "I received Bitcoin from someone",

            "I mined Bitcoin",

            "I bought Bitcoin but don't remember how",

        ],

    )

    print("\n" + "-" * 50)

    print("INVESTIGATION STEP 1: PRESERVE YOUR CLUES")

    print("-" * 50)

    print("\nBefore we search, let's protect any evidence.")

    print("Do not delete, rename, or modify old wallet files.")

    print("Never share private keys or recovery phrases.")

    if history == 1:

        print("\nYou remember using a computer wallet.")

        print("Our first goal is to identify which wallet software")

        print("you may have used.")

        wallet = question(

            "Does any of this sound familiar?",

            [

                "I remember downloading Bitcoin software",

                "I remember using a named wallet application",

                "I remember saving a wallet or backup file",

                "I don't remember the software",

            ],

        )

        if wallet == 1 or wallet == 2:

            print("\nNEXT ACTION:")

            print("Let's use your memories and old computer records")

            print("to identify the wallet software.")

        elif wallet == 3:

            print("\nNEXT ACTION:")

            print("Let's locate and safely preserve the original")

            print("wallet or backup file before examining it.")

        else:

            print("\nNEXT ACTION:")

            print("Let's search for clues in your old emails and")

            print("computer records to identify the wallet.")

    elif history == 2:

        print("\nYou remember purchasing through a website or exchange.")

        exchange = question(

            "What do you remember about the website?",

            [

                "I remember its name",

                "I remember receiving emails from it",

                "I remember buying Bitcoin but not the website",

                "I may still have access to the account",

            ],

        )

        print("\nNEXT ACTION:")

        if exchange == 1:

            print("Let's identify the exchange and its legitimate")

            print("account-recovery process.")

        elif exchange == 2 or exchange == 3:

            print("Let's investigate old email records for account")

            print("registrations, purchase receipts and transactions.")

        else:

            print("Let's establish whether the account is still")

            print("accessible and identify the official recovery route.")

    else:

        print("\nWe need to establish where your Bitcoin may have gone.")

        print("Our next investigation will focus on historical")

        print("emails, computer records and transaction evidence.")

    print("\n" + "=" * 50)

    print("YOUR INVESTIGATION IS UNDERWAY")

    print("=" * 50)

    print("\nThis is your first recommended action, not a")

    print("confirmation that Bitcoin exists or is recoverable.")

    print("\nProject Lost Bitcoin will help you work through")

    print("the evidence one step at a time.")

    print("\nNever give anyone your wallet recovery phrase,")

    print("private keys or email password.")

if __name__ == "__main__":

    main()

