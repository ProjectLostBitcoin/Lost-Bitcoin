
print("\n======================================")

print("       LOST BITCOIN INVESTIGATOR")

print("          INVESTIGATION V5")

print("======================================")

print("\nWelcome! I'm your personal Bitcoin investigator.")

print("We'll work through this together, one step at a time.")

print("You don't need to understand Bitcoin technology.\n")

# Customer investigation profile

profile = {}

profile["exchange"] = input(

    "First, what was the name of the exchange where you bought Bitcoin?\n> "

).strip()

profile["year"] = input(

    "\nApproximately what year did you use it?\n> "

).strip()

profile["email"] = input(

    "\nCan you still access the email account you used back then?\n"

    "1. Yes\n2. No\n3. I'm not sure\n> "

).strip()

profile["withdrawal"] = input(

    "\nDo you remember ever withdrawing Bitcoin from that exchange?\n"

    "1. Yes\n2. No\n3. I'm not sure\n> "

).strip()

print("\n======================================")

print("       INVESTIGATION PROFILE")

print("======================================")

print("Exchange:", profile["exchange"])

print("Approximate year:", profile["year"])

print("Old email access:", profile["email"])

print("Bitcoin withdrawal:", profile["withdrawal"])

# Choose the first investigation task

if profile["email"] == "1":

    print("\n======================================")

    print("       YOUR FIRST INVESTIGATION")

    print("======================================")

    print("\nI recommend starting with your old email account.")

    print("This may help us establish whether you bought Bitcoin,")

    print("received deposits, or withdrew Bitcoin later.")

    print("\nSTEP 1: Open your old email account.")

    print("\nSTEP 2: In the search box, try searching for:")

    print(profile["exchange"])

    print("\nSTEP 3: Look for emails from around", profile["year"])

    print("that mention:")

    print("- Bitcoin or BTC")

    print("- Purchase or order confirmation")

    print("- Deposit")

    print("- Withdrawal")

    print("- Transaction ID")

    print("\nYou don't need to understand what you find.")

    print("Just come back here and tell me in your own words.")

else:

    print("\nLet's first establish whether you can recover access")

    print("to the original email account.")

    print("That may give us an important starting point.")

print("\n======================================")

print("       INVESTIGATOR CHAT")

print("======================================")

print("\nWhat did you discover?")

print("You can explain it in ordinary English.")

print("Type 'exit' when you want to finish.\n")

while True:

    response = input("You: ").strip()

    if response.lower() == "exit":

        print("\nYour investigation has been paused.")

        print("Keep your records safe. We'll continue next time.")

        break

    if not response:

        print("Investigator: Tell me a little more about what you found.")

        continue

    text = response.lower()

    if any(word in text for word in ["withdraw", "sent", "transfer", "moved"]):

        print("\nInvestigator: That's potentially important.")

        print("We need to establish where the Bitcoin was sent.")

        print("Can you find a withdrawal confirmation or transaction ID?")

        print("Please don't share private keys or recovery phrases.")

    elif any(word in text for word in ["purchase", "bought", "buy", "paid", "order"]):

        print("\nInvestigator: Good. A purchase record could help")

        print("establish that you bought Bitcoin.")

        print("Does the email show an amount of Bitcoin, a date,")

        print("or a transaction reference?")

    elif any(word in text for word in ["deposit", "received"]):

        print("\nInvestigator: A deposit record may help us trace")

        print("Bitcoin entering your exchange account.")

        print("Can you see a date, amount, or transaction reference?")

    elif any(word in text for word in ["nothing", "no emails", "can't find", "cannot find"]):

        print("\nInvestigator: No problem. That doesn't mean")

        print("the Bitcoin is gone.")

        print("Let's try another approach.")

        print("Can you remember whether you used any other email")

        print("addresses around that time?")

    elif any(word in text for word in ["newsletter", "promotion", "marketing"]):

        print("\nInvestigator: Those emails may confirm that you")

        print("had contact with the exchange, but they don't")

        print("prove that you purchased or held Bitcoin.")

        print("Let's look for transaction-related emails instead.")

    else:

        print("\nInvestigator: Thanks. Let's narrow that down.")

        print("What date, amount, exchange name, or transaction")

        print("details can you see in what you found?")

print("\nRemember: Finding an email is evidence to investigate,")

print("not proof that Bitcoin remains available.")

print("======================================\n")

