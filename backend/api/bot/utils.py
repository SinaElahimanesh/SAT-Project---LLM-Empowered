import os
from api.bot.gpt import openai_req_generator
from api.bot.Memory.LLM_Memory import MemoryManager
from api.bot.gpt_recommendations import create_recommendations
from api.bot.gpt_for_comprehension import OpenAILLM
from api.bot.gpt_for_statedetection import if_data_sufficient_for_state_change

class StateMachine:
    def __init__(self):
        self.user_states = {}  # Dictionary to store per-user state
        self.memory_manager = MemoryManager()
        self.openai_llm = OpenAILLM(model="gpt-4o-mini")
    
    def get_user_state(self, user):
        """Get or create state for a specific user"""
        if user.id not in self.user_states:
            self.user_states[user.id] = {
                'state': "GREETING_FORMALITY_NAME",
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
        # user_state['loop_count'] = 0

    def ask_llm(self, prompt_file, message, user):
        with open(f'api/bot/Prompts/{prompt_file}', "r", encoding="utf-8") as file:
            system_prompt = file.read()   
            memory_context = self.memory_manager.format_memory_for_prompt(user)
            with open('debug.md', 'w', encoding="utf-8") as file:
                file.write(memory_context)
            if memory_context != "":
                system_prompt = system_prompt.format(memory=memory_context)
        
        return openai_req_generator(system_prompt=system_prompt, user_prompt=message, json_output=False, temperature=0.1)

    def state_handler(self, message, user):
        user_state = self.get_user_state(user)

        if user_state['state'] == "DECIDER":
            emotion = self.openai_llm.emotion_retriever(user_message=message)
            print(emotion)
            self.set_emotion(emotion, user)
            if user_state['emotion'] == 'Positive':
                self.transition("ASK_EXERCISE", user)
            else:
                self.transition("SUPER_STATE_EVENT", user)

        if user_state['state'] == "ASK_EXERCISE_DECIDER":    
            response = self.openai_llm.response_retriever(user_message=message)
            print(response)
            self.set_response(response, user)
            if user_state['response'] == 'Yes':
                self.transition("SUGGESTION", user)
            else:
                self.transition("THANKS", user)

        if user_state['state'] == "INVITE_TO_ATTEMPT_EXC_DECIDER":
            response = self.openai_llm.response_retriever(user_message=message)
            print(response)
            self.set_response(response, user)
            if user_state['response'] == 'Yes':
                self.transition("FEEDBACK", user)
            else:
                self.transition("THANKS", user)

        if user_state['state'] == "LIKE_ANOTHER_EXERCSISE_DECIDER":
            response = self.openai_llm.response_retriever(user_message=message)
            print(response)
            self.set_response(response, user)
            if user_state['response'] == 'Yes':
                self.transition("SUGGESTION", user)
            else:
                self.transition("THANKS", user)

        if user_state['state'] == "GREETING_FORMALITY_NAME":
            response = self.ask_llm("greeting_formality_name.md", message, user)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user))

        elif user_state['state'] == "EMOTION":
            response = self.ask_llm("emotion.md", message, user)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user))
        
        elif user_state['state'] == "SUPER_STATE_EVENT":
            response = self.ask_llm("ask_all_event.md", message, user)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user))

        elif user_state['state'] == "ADDITIONAL":
            response = self.ask_llm("additional.md", message, user)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user))
        
        elif user_state['state'] == "INVITE_TO_PROJECT":
            response = self.ask_llm("invite_to_project.md", message, user)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user))
        
        elif user_state['state'] == "ASK_EXERCISE":
            response = self.ask_llm("ask_exercise.md", message, user)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user))
        
        elif user_state['state'] == "SUGGESTION":
            response = self.ask_llm("suggestion.md", message, user)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user))
        
        elif user_state['state'] == "INVITE_TO_ATTEMPT_EXC":
            response = self.ask_llm("invite_to_attempt_exc.md", message, user)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user))
        
        elif user_state['state'] == "FEEDBACK":
            response = self.ask_llm("invite_to_attempt_exc.md", message, user)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user))
        
        elif user_state['state'] == "LIKE_ANOTHER_EXERCSISE":
            response = self.ask_llm("like_to_do_another_exc.md", message, user)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user))
        
        elif user_state['state'] == "THANKS":
            response = self.ask_llm("thanks.md", message, user)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user))
        
        elif user_state['state'] == "END":
            response = self.ask_llm("end.md", message, user)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user))
  
        else:
            return "میتونی بیشتر توضیح بدی", []

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

        if user_state['state'] == "GREETING_FORMALITY_NAME": 
            messages_obj = self.memory_manager.get_chat_history(user)  
            chat_history = "\n".join([
                f"{'User' if msg.is_user else 'Assistant'}: {msg.text}" 
                for msg in messages_obj
            ])
            transit = if_data_sufficient_for_state_change("greeting.md", chat_history)
            print("transit", transit)
            if transit == "Yes":
                self.transition("EMOTION", user)
        
        elif user_state['state'] == "EMOTION":
            self.transition("DECIDER", user)

        elif user_state['state'] == "SUPER_STATE_EVENT":
            self.transition("ADDITIONAL", user)

        elif user_state['state'] == "ADDITIONAL":
            self.transition("ASK_EXERCISE", user)

        elif user_state['state'] == "ASK_EXERCISE":
            self.transition("ASK_EXERCISE_DECIDER", user)
            
        elif user_state['state'] == "INVITE_TO_PROJECT":
            self.transition("SUGGESTION", user)
            
        elif user_state['state'] == "SUGGESTION":
            self.transition("INVITE_TO_ATTEMPT_EXC", user)

        elif user_state['state'] == "INVITE_TO_ATTEMPT_EXC":
            self.transition("INVITE_TO_ATTEMPT_EXC_DECIDER", user)
        
        elif user_state['state'] == "FEEDBACK":
            self.transition("LIKE_ANOTHER_EXERCSISE", user)

        elif user_state['state'] == "LIKE_ANOTHER_EXERCSISE":
            self.transition("LIKE_ANOTHER_EXERCSISE_DECIDER", user)
        
        elif user_state['state'] == "THANKS":
            self.transition("END", user)
        
        elif user_state['state'] == "END":
            print("State machine has reached the end.")
        
        return response, recommendations, user_state['state']
        
    def set_emotion(self, emotion, user):
        user_state = self.get_user_state(user)
        user_state['emotion'] = emotion
        print(user_state['emotion'])

    def set_response(self, response, user):
        user_state = self.get_user_state(user)
        user_state['response'] = response

    def handle_session_end(self, user):
        """Handle cleanup when user ends session"""
        self.memory_manager.update_memory(user)
        # Reset user state
        self.user_states[user.id] = {
            'state': "GREETING_FORMALITY_NAME",
            'loop_count': 0,
            'message_count': 0,
            'emotion': None,
            'response': None
        }