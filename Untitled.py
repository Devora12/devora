import json
import os

# File to store election data
ELECTION_FILE = "election_data.json"

# Sample candidates
CANDIDATES = ["Alice", "Bob", "Charlie"]

def load_data():
    """Load election data from a JSON file."""
    if os.path.exists(ELECTION_FILE):
        with open(ELECTION_FILE, "r") as file:
            return json.load(file)
    return {"voters": {}, "votes": {candidate: 0 for candidate in CANDIDATES}}

def save_data(data):
    """Save election data to a JSON file."""
    with open(ELECTION_FILE, "w") as file:
        json.dump(data, file, indent=4)

def register_voter(voter_id):
    """Register a new voter if not already registered."""
    data = load_data()
    if voter_id in data["voters"]:
        print("⚠️ Voter already registered!")
        return False
    data["voters"][voter_id] = False  # False means the voter has not voted yet
    save_data(data)
    print("✅ Voter registered successfully!")
    return True

def cast_vote(voter_id, candidate):
    """Allow a registered voter to cast a vote."""
    data = load_data()
    
    if voter_id not in data["voters"]:
        print("❌ Voter not registered!")
        return False
    if data["voters"][voter_id]:
        print("⚠️ You have already voted!")
        return False
    if candidate not in CANDIDATES:
        print("❌ Invalid candidate!")
        return False

    # Record the vote
    data["votes"][candidate] += 1
    data["voters"][voter_id] = True  # Mark voter as having voted
    save_data(data)
    
    print(f"✅ Vote cast successfully for {candidate}!")
    return True

def display_results():
    """Display the current vote count and declare a winner."""
    data = load_data()
    print("\n📊 Election Results:")
    for candidate, votes in data["votes"].items():
        print(f"🗳 {candidate}: {votes} votes")
    
    # Determine winner
    winner = max(data["votes"], key=data["votes"].get)
    print(f"\n🏆 The winner is: {winner}!")

def main():
    """Main function to run the election system."""
    while True:
        print("\n📢 Election System Menu")
        print("1️⃣ Register Voter")
        print("2️⃣ Vote")
        print("3️⃣ Show Results")
        print("4️⃣ Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == "1":
            voter_id = input("Enter your voter ID: ")
            register_voter(voter_id)
        
        elif choice == "2":
            voter_id = input("Enter your voter ID: ")
            print("Candidates:", ", ".join(CANDIDATES))
            candidate = input("Enter your chosen candidate: ")
            cast_vote(voter_id, candidate)
        
        elif choice == "3":
            display_results()
        
        elif choice == "4":
            print("🚪 Exiting Election System. Goodbye!")
            break
        
        else:
            print("❌ Invalid choice, try again.")

if __name__ == "__main__":
    main()
