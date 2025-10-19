# characters.py
import random

class CharacterMessages:
    def __init__(self):
        self.messages = {
            "Farmer Finn": [
                "🌾 Welcome to my farm! I grow the finest crops.",
                "🌾 Need some fresh vegetables? I have the best prices!",
                "🌾 The weather's been perfect for growing this season.",
                "🌾 I can sell you seeds if you want to start farming.",
                "🌾 My tomatoes are the sweetest in the valley!"
            ],
            "Poultry Guy Pip": [
                "🐔 Fresh eggs daily! My chickens are the happiest around.",
                "🐔 Need some protein? I've got eggs and chicken meat.",
                "🐔 My rooster wakes me up every morning at dawn.",
                "🐔 Chicken feed is getting expensive these days.",
                "🐔 I'm thinking of expanding my poultry business."
            ],
            "Witch of Woe": [
                "🧙 Welcome to my dark domain, mortal...",
                "🧙 I sense great potential in you, young one.",
                "🧙 My potions can grant you power beyond imagination.",
                "🧙 Beware the price of magic - it always comes with a cost.",
                "🧙 The spirits whisper secrets only I can understand."
            ],
            "Banker Bard": [
                "🏦 Welcome to the Cosmic Bank! How may I assist you?",
                "🏦 I can help you with loans, investments, and savings.",
                "🏦 Interest rates are quite favorable this season.",
                "🏦 Your credit score looks promising, young entrepreneur.",
                "🏦 We offer the most secure banking in the galaxy!"
            ],
            "Coffee Shop": [
                "☕ Welcome to Cosmic Café! What can I brew for you?",
                "☕ Our espresso is made from beans harvested from distant planets.",
                "☕ Try our signature Cosmic Latte - it's out of this world!",
                "☕ We're having a special on frappuccinos today.",
                "☕ The aroma of fresh coffee fills the air with magic."
            ]
        }
        
        self.current_messages = {}
        self.message_history = {}
        
        # Initialize current messages
        for character in self.messages:
            self.current_messages[character] = self.messages[character][0]
            self.message_history[character] = []

    def get_message(self, character_name):
        """Get current message for a character"""
        return self.current_messages.get(character_name, "Hello there!")

    def change_message(self, character_name, function_type="random"):
        """Change character message based on function type"""
        if character_name not in self.messages:
            return "Character not found!"
        
        if function_type == "random":
            # Random message
            new_message = random.choice(self.messages[character_name])
        elif function_type == "cycle":
            # Cycle through messages
            current_index = self.messages[character_name].index(self.current_messages[character_name])
            next_index = (current_index + 1) % len(self.messages[character_name])
            new_message = self.messages[character_name][next_index]
        elif function_type == "time_based":
            # Time-based messages (morning, afternoon, evening)
            import datetime
            hour = datetime.datetime.now().hour
            if 6 <= hour < 12:
                time_msg = "Good morning! "
            elif 12 <= hour < 18:
                time_msg = "Good afternoon! "
            else:
                time_msg = "Good evening! "
            new_message = time_msg + random.choice(self.messages[character_name])
        elif function_type == "mood":
            # Mood-based messages
            moods = ["happy", "tired", "excited", "worried", "confident"]
            mood = random.choice(moods)
            base_message = random.choice(self.messages[character_name])
            new_message = f"[{mood.title()}] {base_message}"
        else:
            # Default to random
            new_message = random.choice(self.messages[character_name])
        
        # Store in history
        self.message_history[character_name].append(self.current_messages[character_name])
        if len(self.message_history[character_name]) > 5:  # Keep only last 5 messages
            self.message_history[character_name].pop(0)
        
        # Update current message
        self.current_messages[character_name] = new_message
        return new_message

    def get_message_history(self, character_name):
        """Get message history for a character"""
        return self.message_history.get(character_name, [])

    def add_custom_message(self, character_name, message):
        """Add a custom message to a character"""
        if character_name in self.messages:
            self.messages[character_name].append(message)
            return True
        return False
