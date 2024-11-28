def summarize_conversation(text, context):
    ## TODO
    return

class UserMemory:
    def __init__(self, user_id):
        self.user_id = user_id
        self.conversation_history = [] ## Fetch from DB, if nothing was there, initialize as empty list
        self.active_session_history = []
        self.summary = "" ## Fetch from DB

    def add_message(self, user_message, llm_response):
        self.conversation_history.append({"user": user_message, "llm": llm_response})
        self.active_session_history.append({"user": user_message, "llm": llm_response})

    def update_summary(self):
        active_conversation = "\n".join([f"User: {msg['user']}\nLLM: {msg['llm']}" for msg in self.active_session_history])
        self.summary = summarize_conversation(text=active_conversation, context=self.summary)

    def get_full_history(self):
        return self.conversation_history

    def get_summary(self):
        return self.summary
    
    def exit_session(self):
        self.conversation_history = [] ## Push to DB
        self.active_session_history = []
        self.update_summary()


class MemoryManager:
    def __init__(self):
        self.user_memories = {}

    def get_user_memory(self, user_id):
        if user_id not in self.user_memories:
            self.user_memories[user_id] = UserMemory(user_id)
        return self.user_memories[user_id]

    def add_user_message(self, user_id, user_message, llm_response):
        user_memory = self.get_user_memory(user_id)
        user_memory.add_message(user_message, llm_response)

    def get_full_history(self, user_id):
        user_memory = self.get_user_memory(user_id)
        return user_memory.get_full_history()

    def get_summary(self, user_id):
        user_memory = self.get_user_memory(user_id)
        return user_memory.get_summary()


# Example usage
if __name__ == "__main__":
    memory_manager = MemoryManager()

    user_1_id = "user_1"
    user_2_id = "user_2"

    memory_manager.add_user_message(user_1_id, "Hi, how are you?", "I'm great, thank you!")
    memory_manager.add_user_message(user_1_id, "Tell me something interesting.", "Did you know that honey never spoils?")

    memory_manager.add_user_message(user_2_id, "Hello, what's the weather?", "It's sunny and warm today!")
    memory_manager.add_user_message(user_2_id, "Can you give me a fact?", "Octopuses have three hearts!")

    print(f"User 1's full conversation history:")
    print(memory_manager.get_full_history(user_1_id))

    print("\nUser 1's current summary:")
    print(memory_manager.get_summary(user_1_id))

    print(f"\nUser 2's full conversation history:")
    print(memory_manager.get_full_history(user_2_id))

    print("\nUser 2's current summary:")
    print(memory_manager.get_summary(user_2_id))
