from backend.api.bot.gpt_for_summarization import openai_req_generator
from json import json

def summarize_conversation(text, context):
    system_prompt = f"""
    با توجه به پیش‌زمینه‌ای که از مکالمه موجود است و به شرح زیر است:
    {context}،
    این متن را خلاصه کنید:
    {text}

    در خلاصه‌سازی خود، به احساسات کاربر، اطلاعات شخصی کاربر، حالات روحی کاربر، وقایعی که اخیرا برای او رخ داده است و غیره، توجه ویژه داشته باشید.
    """
    return openai_req_generator(system_prompt=system_prompt, json_output=False, temperature=0.1)

class UserMemory:
    def __init__(self, user_id, conversation_history, summary):
        self.user_id = user_id
        self.conversation_history = conversation_history
        self.summary = summary
        self.active_session_history = []

    def add_message(self, user_message, llm_response):
        self.conversation_history.append({"user": user_message, "llm": llm_response})
        self.active_session_history.append({"user": user_message, "llm": llm_response})

    def update_summary(self):
        active_conversation = "\n".join([f"User: {msg['user']}\nLLM: {msg['llm']}" for msg in self.active_session_history])
        self.summary = summarize_conversation(text=active_conversation, context=self.get_summary())

    def get_full_history(self):
        return self.conversation_history

    def get_summary(self):
        return self.summary
    
    def exit_session(self):
        self.update_summary()
        file_path = "memory.json"

        with open(file_path, "r") as json_file:
            data = json.load(json_file)

        data.update({self.user_id: {"conversation_history": self.conversation_history, "summary": self.summary}})  

        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

        self.active_session_history = []

class MemoryManager:
    def __init__(self):
        with open('memory.json', "r") as json_file:
            self.user_memories = json.load(json_file)

    def get_user_memory(self, user_id):
        if user_id not in self.user_memories:
            self.user_memories[user_id] = UserMemory(user_id, [], "")
            return self.user_memories[user_id]
        return UserMemory(user_id, self.user_memories[user_id].conversation_history, self.user_memories[user_id].summary)

    def add_user_message(self, user_id, user_message, llm_response):
        user_memory = self.get_user_memory(user_id)
        user_memory.add_message(user_message, llm_response)

    def get_full_history(self, user_id):
        user_memory = self.get_user_memory(user_id)
        return user_memory.get_full_history()

    def get_summary(self, user_id):
        user_memory = self.get_user_memory(user_id)
        return user_memory.get_summary()
    
    def exit_session(self, user_id):
        user_memory = self.get_user_memory(user_id)
        user_memory.exit_session()

# Example usage
if __name__ == "__main__":
    memory_manager = MemoryManager()

    user_1_id = "user_1"

    user_memory = memory_manager.get_user_memory(user_1_id)

    memory_manager.add_user_message(user_1_id, "Hi, how are you?", "I'm great, thank you!")
    memory_manager.add_user_message(user_1_id, "Tell me something interesting.", "Did you know that honey never spoils?")


    print(f"User 1's full conversation history:")
    print(memory_manager.get_full_history(user_1_id))

    print("\nUser 1's current summary:")
    print(memory_manager.get_summary(user_1_id))
