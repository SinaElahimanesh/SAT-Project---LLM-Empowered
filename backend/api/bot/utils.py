from api.bot.gpt import openai_req_generator
from api.bot.Memory.LLM_Memory import MemoryManager
from api.bot.gpt_recommendations import create_recommendations
from api.bot.gpt_for_comprehension import OpenAILLM
from api.bot.gpt_for_statedetection import if_data_sufficient_for_state_change
from api.bot.RAG.gpt_explainability import create_exercise_explanation
from api.bot.RAG.llm_excercise_suggestor import suggest_exercises, exercises
from api.models import UserDayProgress


class StateMachine:
    def __init__(self):
        self.user_states = {}  # Dictionary to store per-user state
        self.memory_manager = MemoryManager()
        self.openai_llm = OpenAILLM(model="gpt-4o-mini")

    def get_user_day_progress(self, user):
        """Get or create day progress for a specific user"""
        day_progress, created = UserDayProgress.objects.get_or_create(user=user)
        return day_progress.calculate_current_day()

    def get_day_allowed_exercises(self, day):
        """Get allowed exercise numbers for a given day"""
        if day == 8:
            return None
        elif 1 <= day <= 7:
            # Changed to cumulative: day 1 = [1,2,3], day 2 = [1,2,3,4,5,6], etc.
            end_exercise = day * 3
            return list(range(1, end_exercise + 1))
        else:
            return [1, 2, 3]

    def parse_exercise_number(self, exercise_num):
        """Parse exercise number to base number (e.g., '2a' -> 2, '0.1' -> 0)"""
        if '.' in exercise_num:
            return int(float(exercise_num))
        else:
            import re
            base_num = re.match(r'(\d+)', exercise_num)
            return int(base_num.group(1)) if base_num else 0

    def filter_exercises_by_day(self, available_exercises, user):
        """Filter exercises based on user's current day"""
        current_day = self.get_user_day_progress(user)
        allowed_exercises = self.get_day_allowed_exercises(current_day)

        if allowed_exercises is None:
            return available_exercises

        # Filter exercises based on day restrictions
        filtered_exercises = []
        for exercise in available_exercises:
            exercise_base_num = self.parse_exercise_number(exercise["Exercise Number"])
            if exercise_base_num in allowed_exercises or exercise_base_num == 0:  # 0.x exercises allowed on day 1
                filtered_exercises.append(exercise)

        return filtered_exercises

    def get_user_state(self, user):
        """Get or create state for a specific user"""
        if user.id not in self.user_states:
            self.user_states[user.id] = {
                'state': "GREETING_FORMALITY_NAME",
                'message_count': 0,
                'emotion': None,
                'response': None,
                'stage': user.stage,
                'exercises_done': set(),
                'current_day': self.get_user_day_progress(user)
            }
        else:
            self.user_states[user.id]['current_day'] = self.get_user_day_progress(user)
        return self.user_states[user.id]

    def transition(self, new_state, user):
        user_state = self.get_user_state(user)
        print(f"Transitioning from {user_state['state']} to {new_state}")
        user_state['state'] = new_state

    def ask_llm(self, prompt_file, message, user):
        with open(f'api/bot/Prompts/{prompt_file}', "r", encoding="utf-8") as file:
            system_prompt = file.read()
            memory_context = self.memory_manager.format_memory_for_prompt(user)
            with open('debug.md', 'w', encoding="utf-8") as file:
                file.write(memory_context)
            if memory_context != "":
                system_prompt = system_prompt.format(memory=memory_context)

        # print(f'system_prompt={system_prompt}')
        # print(f'user_prompt={message}')
        return openai_req_generator(system_prompt=system_prompt, user_prompt=message, json_output=False, temperature=0.1)

    def customize_excercises(self, prompt_file, user, excercises):
        with open(f'api/bot/Prompts/{prompt_file}', "r", encoding="utf-8") as file:
            system_prompt = file.read()
            memory_context = self.memory_manager.format_memory_for_prompt(user)
            # with open('debug.md', 'w', encoding="utf-8") as file:
            #     file.write(memory_context)
            if memory_context != "":
                system_prompt = system_prompt.format(
                    memory=memory_context, exc=excercises)

        return openai_req_generator(system_prompt=system_prompt, user_prompt=None, json_output=False, temperature=0.1)

    def if_transition(self, user, data):
        messages_obj = self.memory_manager.get_chat_history(user)
        chat_history = "\n".join([
            f"{'User' if msg.is_user else 'Assistant'}: {msg.text}"
            for msg in messages_obj
        ])
        transit = if_data_sufficient_for_state_change(data, chat_history)
        return transit

    def state_handler(self, message, user):
        user_state = self.get_user_state(user)
        exercise_number = None

        messages_obj = self.memory_manager.get_chat_history(user)
        chat_history = "\n".join([
            f"{'User' if msg.is_user else 'Assistant'}: {msg.text}"
            for msg in messages_obj
        ])

        if user_state['state'] == "EMOTION_DECIDER":
            emotion = self.openai_llm.emotion_retriever(user_message=message, chat_history=chat_history)
            self.set_emotion(emotion, user)
            if 'Positive' in user_state['emotion']:
                self.transition("ASK_EXERCISE", user)
            else:
                self.transition("SUPER_STATE_EVENT", user)

        if user_state['state'] == "ASK_EXERCISE_DECIDER":
            response = self.openai_llm.response_retriever(user_message=message, chat_history=chat_history)
            self.set_response(response, user)
            if 'Yes' in user_state['response']:
                self.transition("EXERCISE_SUGGESTION", user)
            else:
                self.transition("THANKS", user)

        if user_state['state'] == "EXERCISE_SUGGESTION_DECIDER":
            response = self.openai_llm.response_retriever(user_message=message, chat_history=chat_history)
            self.set_response(response, user)
            if 'Yes' in user_state['response']:
                self.transition("FEEDBACK", user)
            else:
                self.transition("LIKE_ANOTHER_EXERCSISE", user)

        if user_state['state'] == "LIKE_ANOTHER_EXERCSISE_DECIDER":
            response = self.openai_llm.response_retriever(user_message=message, chat_history=chat_history)
            self.set_response(response, user)
            if 'Yes' in user_state['response']:
                self.transition("EXERCISE_SUGGESTION", user)
            else:
                self.transition("THANKS", user)

        if user_state['state'] == "GREETING_FORMALITY_NAME":
            response = self.ask_llm(
                "greeting_formality_name.md", message, user)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user)), None, None

        elif user_state['state'] == "EMOTION":
            response = self.ask_llm("emotion.md", message, user)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user)), None, None

        elif user_state['state'] == "SUPER_STATE_EVENT":
            response = self.ask_llm("ask_all_event.md", message, user)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user)), None, None

        elif user_state['state'] == "ASK_EXERCISE":
            response = self.ask_llm("ask_exercise.md", message, user)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user)), None, None

        elif user_state['state'] == "EXERCISE_SUGGESTION":
            user_memory = self.memory_manager.get_current_memory(user)

            all_exercises = exercises
            day_filtered_exercises = self.filter_exercises_by_day(all_exercises, user)

            exercise_content, exercise_number = suggest_exercises(
                user_state['exercises_done'],
                user_memory,
                user_state['stage'],
                day_filtered_exercises
            )
            user_state['exercises_done'].add(exercise_number)
            response = self.customize_excercises(
                "suggestion.md", user, exercise_content)
            explainability = create_exercise_explanation(
                exercise_content, user_memory)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user)), explainability, exercise_number

        elif user_state['state'] == "FEEDBACK":
            response = self.ask_llm("feedback.md", message, user)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user)), None, None

        elif user_state['state'] == "LIKE_ANOTHER_EXERCSISE":
            response = self.ask_llm("like_to_do_another_exc.md", message, user)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user)), None, None

        elif user_state['state'] == "THANKS":
            response = self.ask_llm("thanks.md", message, user)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user)), None, None

        elif user_state['state'] == "END":
            response = self.ask_llm("end.md", message, user)
            return response, create_recommendations(response, self.memory_manager.get_current_memory(user)), None, None

        else:
            return "میتونی بیشتر توضیح بدی", [], None, None

    def execute_state(self, message, user):
        user_state = self.get_user_state(user)
        print(f"You are in the {user_state['state']} state")

        # update memory and increment message count
        self.memory_manager.add_message(user=user, text=message, is_user=True)

        # Check if we need to update memory summary
        if user_state['message_count'] >= 4:
            self.memory_manager.update_memory(user)
            user_state['message_count'] = 0

        if user_state['state'] == "GREETING_FORMALITY_NAME":
            transit = self.if_transition(user, "greeting.md")
            print("transit", transit)
            if "بله" in transit:
                self.transition("EMOTION", user)

        elif user_state['state'] == "EMOTION":
            transit = self.if_transition(user, "emotion.md")
            print("transit", transit)
            if "بله" in transit:
                self.transition("EMOTION_DECIDER", user)

        elif user_state['state'] == "SUPER_STATE_EVENT":
            transit = self.if_transition(user, "event.md")
            print("transit", transit)
            if "بله" in transit:
                self.transition("ASK_EXERCISE", user)

        elif user_state['state'] == "ASK_EXERCISE":
            self.transition("ASK_EXERCISE_DECIDER", user)

        elif user_state['state'] == "EXERCISE_SUGGESTION":
            self.transition("EXERCISE_SUGGESTION_DECIDER", user)

        elif user_state['state'] == "FEEDBACK":
            self.transition("LIKE_ANOTHER_EXERCSISE", user)

        elif user_state['state'] == "LIKE_ANOTHER_EXERCSISE":
            self.transition("LIKE_ANOTHER_EXERCSISE_DECIDER", user)

        elif user_state['state'] == "THANKS":
            self.transition("END", user)

        elif user_state['state'] == "END":
            print("State machine has reached the end.")

        response, recommendations, explainibility, excercise_number = self.state_handler(
            message, user)
        # print(response, recommendations)

        self.memory_manager.add_message(
            user=user, text=response, is_user=False)
        user_state['message_count'] += 2

        return response, recommendations, user_state['state'], explainibility, excercise_number

    def set_emotion(self, emotion, user):
        user_state = self.get_user_state(user)
        user_state['emotion'] = emotion
        print(f'user emotion={user_state["emotion"]}')

    def set_response(self, response, user):
        user_state = self.get_user_state(user)
        user_state['response'] = response
        print(f'user response={user_state["response"]}')

    def handle_session_end(self, user):
        """Handle cleanup when user ends session"""
        self.memory_manager.update_memory(user)
        # Reset user state
        self.user_states[user.id] = {
            'state': "GREETING_FORMALITY_NAME",
            'message_count': 0,
            'emotion': None,
            'response': None
        }
