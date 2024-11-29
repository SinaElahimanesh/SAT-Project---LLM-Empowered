class StateMachine:
    def __init__(self):
        self.state = "GREETING"  
        self.loop_count = 0
    
    def transition(self, new_state):
        print(f"Transitioning from {self.state} to {new_state}")
        self.state = new_state
        self.emotion = 'Positive'
        self.response = 'Yes'
        self.loop_count = 0

    def state_handler(self):
        if self.loop_count < 5:
            return "صحبت آزاد - Open-Ended Conversation"
        
        elif self.state == "GREETING":
            return "سلام روزت بخیر"
        elif self.state == "FORMALITY":
            return "دوست داری با هم رسمی صحبت کنیم یا دوستانه؟"
        elif self.state == "NAME":
            return "اسمت چیه؟"
        elif self.state == "FEELING":
            return "حالت چطوره؟"
        elif self.state == "EMOTION_VERIFIER":
            return "آیا احساس ناراحتی داری؟"
        elif self.state == "FEELING_CORRECTION":
            return "احساست رو میتونی بهم بگی؟"
        elif self.state == "EVENT":
            return "آیا اتفاق خاصی امروز افتاده که بخواهی درباره‌اش صحبت کنی؟"
        elif self.state == "ASK_EVENT_RECENT":
            return "آیا این اتفاق به تازگی برایت رخ داده؟"
        elif self.state == "EXC10":
            return "آیا تمرین ۱۰ را برای خودت تاثیر گذار دونستی؟"
        elif self.state == "ADDITIONAL":
            return "آیا چیزی دیگه‌ای هست که بخواهی اضافه کنی؟"
        elif self.state == "ASK_QUESTION":
            return "از تو یک سوال دیگر می‌پرسم."
        elif self.state == "INVITE_TO_PROJECT":
            return "من تو را به دلبستگی به خود دعوت می‌کنم."
        elif self.state == "ASK_EXERCISE":
            return "آیا دوست داری تمرینی برای بهتر شدن حالت بشنوی؟"
        elif self.state == "SUGGESTION":
            return "من این تمرین رو پیشنهاد می‌کنم که انجام بدی."
        elif self.state == "INVITE_TO_ATTEMPT_EXC":
            return "آیا می‌توانی این تمرین را انجام دهی؟"
        elif self.state == "FEEDBACK":
            return "آیا حالت بهتر شده؟"
        elif self.state == "LIKE_ANOTHER_EXERCSISE":
            return "آیا می‌خواهی یک تمرین دیگر به تو پیشنهاد کنم؟"
        elif self.state == "THANKS":
            return "خیلی ممنون که صحبت کردی، امیدوارم بهت کمک کرده باشم."
        elif self.state == "END":
            return "روز خوبی داشته باشی"

    def execute_state(self):
        print(f"You are in the {self.state} state")
        print(self.state_handler())

        if self.loop_count < 5:
            self.loop_count += 1

        if self.state == "GREETING":
            return self.transition("FORMALITY")    #Need To Save Tone in Memory - Not in SAT Diagram
        
        elif self.state == "FORMALITY":            
            return self.transition("NAME")         #Need To Name in Memory - Not in SAT Diagram
        
        elif self.state == "NAME":
            return self.transition("FEELING")
        
        elif self.state == "FEELING":
            return self.transition("EMOTION_VERIFIER")
            
        elif self.state == "EMOTION_VERIFIER":
            if self.response == 'Yes':
                if self.emotion == 'Negative':
                    return self.transition("EVENT")             #Recommend Exc 7, 15, 16
                if self.emotion == 'Antisocial':
                    return self.transition("EVENT")             #Recommend Exc 17, 18
                if self.emotion == 'Positive':
                    return self.transition("ASK_EXERCISE")      #Recommend Exc 7, 8, 12, 13, 14, 15, 17, 18, 19, 21, 22, 23, 26
            if self.response == 'No':
                return self.transition("FEELING_CORRECTION")
            
        elif self.state == "FEELING_CORRECTION":
            return self.transition("EVENT")
        
        elif self.state == "EVENT":
            if self.response == 'Yes':
                return self.transition("ASK_EVENT_RECENT")
            if self.response == 'No':
                return self.transition("ADDITIONAL")        #Recommend Exc 9

        elif self.state == "ASK_EVENT_RECENT":              
            if self.response == 'Yes':
                return self.transition("ADDITIONAL")        #Recommend Exc 9
            if self.response == 'No':
                return self.transition("EXC10")
        
        elif self.state == "EXC10":
            if self.response == 'Yes':
                return self.transition("ADDITIONAL")        #Recommend Exc 15
            if self.response == 'No':
                return self.transition("ADDITIONAL")        #Recommend Exc 10
        
        elif self.state == "ADDITIONAL":
            if self.response == 'Yes':
                return self.transition("ASK_QUESTION")                      # Before that check if advance exercises are appropriate for user     
            if self.response == 'No':
                return self.transition("INVITE_TO_PROJECT")                 #Recommend Exc 15
            
        elif self.state == "ASK_QUESTION":
            if self.response == 'Yes':
                return self.transition("INVITE_TO_PROJECT")             # Recommend relevant exercises
            if self.response == 'No':
                return self.transition("ASK_QUESTION")                  # Ask a different question
        
        elif self.state == "ASK_EXERCISE":
            if self.response == 'Yes':
                return self.transition("SUGGESTION")
            if self.response == 'No':
                return self.transition("THANKS")
            
        elif self.state == "INVITE_TO_PROJECT":
            return self.transition("SUGGESTION")
            
        elif self.state == "SUGGESTION":
            return self.transition("INVITE_TO_ATTEMPT_EXC")
        
        elif self.state == "INVITE_TO_ATTEMPT_EXC":
            if self.response == 'Yes':
                return self.transition("FEEDBACK")
            if self.response == 'No':
                return self.transition("THANKS")
        
        elif self.state == "FEEDBACK":
            return self.transition("LIKE_ANOTHER_EXERCSISE")
        
        elif self.state == "LIKE_ANOTHER_EXERCSISE":
            if self.response == 'Yes':
                return self.transition("SUGGESTION")
            if self.response == 'No':
                return self.transition("THANKS")
        
        elif self.state == "THANKS":
            return self.transition("END")
        
        elif self.state == "END":
            print("State machine has reached the end.")
            return "Done"
        
    def set_emotion(self, emotion):
        self.emotion = emotion

    def set_response(self, response):
        self.response = response
