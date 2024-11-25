class StateMachine:
    def __init__(self):
        self.state = "GREETING"  
        self.loop_count = 0
    
    def transition(self, new_state):
        print(f"Transitioning from {self.state} to {new_state}")
        self.state = new_state
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
        elif self.state == "EXC10":
            return "چه چیزی به نظرت میتونه به بهتر شدن حالت کمک کنه؟"
        elif self.state == "ADDITIONAL":
            return "آیا چیزی دیگه‌ای هست که بخواهی اضافه کنی؟"
        elif self.state == "SUGGESTOIN":
            return "آیا می‌خواهی پیشنهاداتی برای بهتر شدن حالت بشنوی؟"
        elif self.state == "FEEDBACK":
            return "آیا حالت بهتر شده؟"
        elif self.state == "THANKS":
            return "خیلی ممنون که صحبت کردی، امیدوارم بهت کمک کرده باشم."
        elif self.state == "END":
            return "روز خوبی داشته باشی"

    def execute_state(self):
        print(f"You are in the {self.state} state")
        print(self.state_handler())

        if self.loop_count < 5:
            self.loop_count += 1
            return

        if self.state == "GREETING":
            self.transition("FORMALITY")
        elif self.state == "FORMALITY":
            self.transition("NAME")
        elif self.state == "NAME":
            self.transition("FEELING")
        elif self.state == "FEELING":
            self.transition("EMOTION_VERIFIER")
        elif self.state == "EMOTION_VERIFIER":
            self.transition("FEELING_CORRECTION")
        elif self.state == "FEELING_CORRECTION":
            self.transition("EVENT")
        elif self.state == "EVENT":
            self.transition("EXC10")
        elif self.state == "EXC10":
            self.transition("ADDITIONAL")
        elif self.state == "ADDITIONAL":
            self.transition("SUGGESTOIN")
        elif self.state == "SUGGESTOIN":
            self.transition("FEEDBACK")
        elif self.state == "FEEDBACK":
            self.transition("THANKS")
        elif self.state == "THANKS":
            self.transition("END")
        elif self.state == "END":
            print("State machine has reached the end.")

# Example usage
state_machine = StateMachine()
while state_machine.state != "END":
    state_machine.execute_state()
