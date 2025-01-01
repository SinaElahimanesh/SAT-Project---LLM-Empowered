import os
from api.bot.gpt import openai_req_generator
from api.bot.Memory.LLM_Memory import MemoryManager
from api.bot.gpt_recommendations import create_recommendations

class StateMachine:
    def __init__(self):
        self.user_states = {}  # Dictionary to store per-user state
        self.memory_manager = MemoryManager()
    
    def get_user_state(self, user):
        """Get or create state for a specific user"""
        if user.id not in self.user_states:
            self.user_states[user.id] = {
                'state': "GREETING",
                'loop_count': 0,
                'message_count': 0,
                'emotion': None,
                'response': None
            }
        return self.user_states[user.id]

    def transition(self, new_state, user):
        user_state = self.get_user_state(user)
        print(f"Transitioning from {user_state['state']} to {new_state}")
        user_state['state'] = new_state
        user_state['emotion'] = 'Positive'
        user_state['response'] = 'Yes'
        user_state['loop_count'] = 0

    def ask_llm(self, prompt_file, message, user):
        with open(f'api/bot/Prompts/{prompt_file}', "r", encoding="utf-8") as file:
            system_prompt = file.read()   
            memory_context = self.memory_manager.format_memory_for_prompt(user)
            if memory_context != "":
                system_prompt = system_prompt.format(memory=memory_context)
        
        return openai_req_generator(system_prompt=system_prompt, user_prompt=message, json_output=False, temperature=0.1)

    def state_handler(self, message, user):
        user_state = self.get_user_state(user)
            
        if user_state['state'] == "GREETING":
            response = self.ask_llm("greeting.md", message, user)
            return response, create_recommendations(response)

        elif user_state['state'] == "NAME":
            response = self.ask_llm("name.md", message, user)
            return response, create_recommendations(response)

        elif user_state['state'] == "FORMALITY":
            response = self.ask_llm("formality.md", message, user)
            return response, create_recommendations(response)

        elif user_state['state'] == "EMOTION":
            response = self.ask_llm("emotion.md", message, user)
            return response, create_recommendations(response)
        
        elif user_state['state'] == "EMOTION_VERIFIER":
            response = self.ask_llm("emotion_verifier.md", message, user)
            return response, create_recommendations(response)
        
        elif user_state['state'] == "EMOTION_CORRECTION":
            response = self.ask_llm("emotion_correction.md", message, user)
            return response, create_recommendations(response)
        
        elif user_state['state'] == "EVENT":
            response = self.ask_llm("event.md", message, user)
            return response, create_recommendations(response)
        
        # elif self.state == "ASK_EVENT_RECENT":
        #     return "آیا این اتفاق به تازگی برایت رخ داده؟"
        # elif self.state == "EXC10":
        #     return "آیا تمرین ۱۰ را برای خودت تاثیر گذار دونستی؟"
        # elif self.state == "ADDITIONAL":
        #     return "آیا چیزی دیگه‌ای هست که بخواهی اضافه کنی؟"
        # elif self.state == "ASK_QUESTION":
        #     return "از تو یک سوال دیگر می‌پرسم."
        # elif self.state == "INVITE_TO_PROJECT":
        #     return "من تو را به دلبستگی به خود دعوت می‌کنم."
        # elif self.state == "ASK_EXERCISE":
        #     return "آیا دوست داری تمرینی برای بهتر شدن حالت بشنوی؟"
        # elif self.state == "SUGGESTION":
        #     return "من این تمرین رو پیشنهاد می‌کنم که انجام بدی."
        # elif self.state == "INVITE_TO_ATTEMPT_EXC":
        #     return "آیا می‌توانی این تمرین را انجام دهی؟"
        # elif self.state == "FEEDBACK":
        #     return "آیا حالت بهتر شده؟"
        # elif self.state == "LIKE_ANOTHER_EXERCSISE":
        #     return "آیا می‌خواهی یک تمرین دیگر به تو پیشنهاد کنم؟"
        # elif self.state == "THANKS":
        #     return "خیلی ممنون که صحبت کردی، امیدوارم بهت کمک کرده باشم."
        # elif self.state == "END":
        #     return "روز خوبی داشته باشی"

    def execute_state(self, message, user):
        user_state = self.get_user_state(user)
        print(f"You are in the {user_state['state']} state")
        response, recommendations = self.state_handler(message, user)
        print(response, recommendations)
        
        # update memory and increment message count
        self.memory_manager.add_message(user=user, text=message, is_user=True)
        self.memory_manager.add_message(user=user, text=response, is_user=False)
        user_state['message_count'] += 2

        # Check if we need to update memory summary
        if user_state['message_count'] >= 4:
            self.memory_manager.update_memory(user)
            user_state['message_count'] = 0

        if user_state['loop_count'] < 5:
            user_state['loop_count'] += 1

        if user_state['state'] == "GREETING":
            self.transition("FORMALITY", user)    #Need To Save Tone in Memory - Not in SAT Diagram
        
        elif user_state['state'] == "FORMALITY":            
            self.transition("NAME", user)         #Need To Name in Memory - Not in SAT Diagram
        
        elif user_state['state'] == "NAME":
            self.transition("EMOTION", user)
        
        elif user_state['state'] == "EMOTION":
            self.transition("EMOTION_VERIFIER", user)
            
        elif user_state['state'] == "EMOTION_VERIFIER":
            if user_state['response'] == 'Yes':
                if user_state['emotion'] == 'Negative':
                    self.transition("EVENT", user)             #Recommend Exc 7, 15, 16
                if user_state['emotion'] == 'Antisocial':
                    self.transition("EVENT", user)             #Recommend Exc 17, 18
                if user_state['emotion'] == 'Positive':
                    self.transition("ASK_EXERCISE", user)      #Recommend Exc 7, 8, 12, 13, 14, 15, 17, 18, 19, 21, 22, 23, 26
            if user_state['response'] == 'No':
                self.transition("EMOTION_CORRECTION", user)
            
        elif user_state['state'] == "EMOTION_CORRECTION":
            self.transition("EVENT", user)
        
        elif user_state['state'] == "EVENT":
            if user_state['response'] == 'Yes':
                self.transition("ASK_EVENT_RECENT", user)
            if user_state['response'] == 'No':
                self.transition("ADDITIONAL", user)        #Recommend Exc 9

        elif user_state['state'] == "ASK_EVENT_RECENT":              
            if user_state['response'] == 'Yes':
                self.transition("ADDITIONAL", user)        #Recommend Exc 9
            if user_state['response'] == 'No':
                self.transition("EXC10", user)
        
        elif user_state['state'] == "EXC10":
            if user_state['response'] == 'Yes':
                self.transition("ADDITIONAL", user)        #Recommend Exc 15
            if user_state['response'] == 'No':
                self.transition("ADDITIONAL", user)        #Recommend Exc 10
        
        elif user_state['state'] == "ADDITIONAL":
            if user_state['response'] == 'Yes':
                self.transition("ASK_QUESTION", user)                      # Before that check if advance exercises are appropriate for user     
            if user_state['response'] == 'No':
                self.transition("INVITE_TO_PROJECT", user)                 #Recommend Exc 15
            
        elif user_state['state'] == "ASK_QUESTION":
            if user_state['response'] == 'Yes':
                self.transition("INVITE_TO_PROJECT", user)             # Recommend relevant exercises
            if user_state['response'] == 'No':
                self.transition("ASK_QUESTION", user)                  # Ask a different question
        
        elif user_state['state'] == "ASK_EXERCISE":
            if user_state['response'] == 'Yes':
                self.transition("SUGGESTION", user)
            if user_state['response'] == 'No':
                self.transition("THANKS", user)
            
        elif user_state['state'] == "INVITE_TO_PROJECT":
            self.transition("SUGGESTION", user)
            
        elif user_state['state'] == "SUGGESTION":
            self.transition("INVITE_TO_ATTEMPT_EXC", user)
        
        elif user_state['state'] == "INVITE_TO_ATTEMPT_EXC":
            if user_state['response'] == 'Yes':
                self.transition("FEEDBACK", user)
            if user_state['response'] == 'No':
                self.transition("THANKS", user)
        
        elif user_state['state'] == "FEEDBACK":
            self.transition("LIKE_ANOTHER_EXERCSISE", user)
        
        elif user_state['state'] == "LIKE_ANOTHER_EXERCSISE":
            if user_state['response'] == 'Yes':
                self.transition("SUGGESTION", user)
            if user_state['response'] == 'No':
                self.transition("THANKS", user)
        
        elif user_state['state'] == "THANKS":
            self.transition("END", user)
        
        elif user_state['state'] == "END":
            print("State machine has reached the end.")
        
        return response, recommendations
        
    def set_emotion(self, emotion, user):
        user_state = self.get_user_state(user)
        user_state['emotion'] = emotion

    def set_response(self, response, user):
        user_state = self.get_user_state(user)
        user_state['response'] = response

    def handle_session_end(self, user):
        """Handle cleanup when user ends session"""
        self.memory_manager.update_memory(user)
        # Reset user state
        self.user_states[user.id] = {
            'state': "GREETING",
            'loop_count': 0,
            'message_count': 0,
            'emotion': None,
            'response': None
        }
