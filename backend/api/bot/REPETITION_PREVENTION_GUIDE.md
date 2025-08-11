# Global Repetition Prevention System - Enhanced

## Overview
This enhanced system prevents repetition of phrases AND specific words across the ENTIRE conversation. It specifically addresses the problem of overusing words like "کمک" (help), "متاسفم" (sorry), and "می‌تونم" (I can) that were identified in user conversations.

## Key Components

### 1. Enhanced RepetitionPrevention Class
Located in `backend/api/bot/utils.py`, this class now includes:
- **Word-level tracking**: Tracks frequency of specific problematic words
- **Phrase categorization**: Categorizes phrases (empathy, questions, transitions, general)
- **Overuse detection**: Identifies words used more than a threshold
- **Smart phrase cleaning**: Normalizes phrases for accurate comparison

### 2. Problematic Words Tracking
The system now specifically tracks these frequently overused words:
```python
self.problematic_words = {
    'کمک': 0,      # help - most problematic
    'متاسفم': 0,   # sorry
    'می‌تونم': 0,  # I can
    'اینجام': 0,   # I'm here
    'گوش': 0,      # listen
    'صحبت': 0,     # talk
    'احساس': 0,    # feeling
    'ناراحت': 0,   # sad
    'خوشحال': 0,   # happy
    'واقعاً': 0,   # really
    'وای': 0,      # wow
    'اوه': 0,      # oh
    'باشه': 0,     # okay
    'مشکلی': 0,    # problem
    'احترام': 0,   # respect
    'دوست': 0,     # friend
    'طبیعی': 0,    # natural
    'گرم': 0,      # warm
    'صمیمی': 0     # intimate
}
```

### 3. Alternative Phrase Banks
The system now includes specific alternatives for overused expressions:

#### Alternatives for "کمک" (help):
- "اگر دوست داری، می‌تونی بیشتر بگی"
- "من اینجا هستم تا گوش بدم"
- "اگر نیاز به صحبت داری، بگو"
- "می‌تونی بیشتر توضیح بدی"
- "اگر دوست داری، ادامه بده"
- "من گوش می‌کنم"
- "اگر نیاز داری، بگو"

#### Alternatives for "متاسفم" (sorry):
- "این تجربه سختی بوده"
- "این اتفاق تأثیر زیادی رویت گذاشته"
- "این موضوع واقعاً مهمه"
- "این تجربه واقعاً دشوار بوده"
- "این اتفاق تأثیر عمیقی رویت گذاشته"

## How It Works

### 1. Word Frequency Tracking
Every bot response is analyzed for word frequency:
```python
def _track_word_frequency(self, phrase):
    words = phrase.split()
    for word in words:
        if word in self.problematic_words:
            self.problematic_words[word] += 1
```

### 2. Overuse Detection
The system identifies words used beyond a threshold:
```python
def get_overused_words(self, threshold=2):
    overused = {}
    for word, count in self.problematic_words.items():
        if count >= threshold:
            overused[word] = count
    return overused
```

### 3. Enhanced Context Injection
The repetition prevention context now includes:
- **Used phrases**: Previously used expressions
- **Overused words**: Words used beyond threshold
- **Specific warnings**: Clear instructions about problematic words
- **Alternative suggestions**: Direct alternatives for overused expressions

## Updated Prompt Files

### Core Prompts Enhanced:
- `ask_all_event.md` - Added specific word repetition warnings
- `greeting.md` - Added alternative phrase suggestions
- All other prompts include enhanced repetition prevention

### Key Changes in Prompts:
1. **Word-level warnings**: Specific warnings about overused words
2. **Alternative phrases**: Direct alternatives for common expressions
3. **Clear instructions**: Explicit guidance on avoiding repetition
4. **Context awareness**: Prompts consider entire conversation history

## Features

### 1. Automatic Word Categorization
- **Problematic words**: Predefined list of frequently overused words
- **Frequency tracking**: Counts usage of each problematic word
- **Threshold detection**: Identifies words used beyond acceptable limits

### 2. Smart Phrase Alternatives
- **Context-aware suggestions**: Alternatives based on conversation context
- **Variety maintenance**: Ensures diverse expression usage
- **Natural flow**: Maintains conversation naturalness

### 3. Enhanced Context Generation
- **Real-time warnings**: Shows overused words in context
- **Usage counts**: Displays how many times each word was used
- **Clear guidance**: Specific instructions for avoiding repetition

## Usage Examples

### Before (Repetitive with "کمک"):
```
User: "تصادف کردم"
Bot: "متاسفم که این رو می‌شنوم. می‌تونم کمکت کنم."

User: "اسیب روحی دیدم"  
Bot: "متاسفم که این رو می‌شنوم. می‌تونم کمکت کنم."

User: "حال روحیم بده"
Bot: "متاسفم که حالت خوب نیست. می‌تونم کمکت کنم."
```

### After (Varied without "کمک"):
```
User: "تصادف کردم"
Bot: "این تجربه واقعاً سختی بوده. من اینجا هستم تا گوش بدم."

User: "اسیب روحی دیدم"
Bot: "این اتفاق تأثیر عمیقی رویت گذاشته. اگر دوست داری، می‌تونی بیشتر بگی."

User: "حال روحیم بده"
Bot: "این تجربه واقعاً ناراحت‌کننده‌ست. اگر نیاز به صحبت داری، بگو."
```

## Implementation Details

### 1. Word Tracking
```python
# Track word frequency
self.repetition_prevention._track_word_frequency(cleaned_phrase)

# Check for overused words
overused = self.repetition_prevention.get_overused_words(threshold=2)
```

### 2. Enhanced Context Generation
```python
# Generate repetition prevention context with word warnings
context = self._get_repetition_prevention_context()
system_prompt += f"\n\n### ⚠️ هشدار مهم - جلوگیری از تکرار در کل مکالمه:\n{context}"
```

### 3. Response Analysis
```python
# Analyze and categorize response with word tracking
sentences = re.split(r'[.!?؟]', response)
for sentence in sentences:
    if any(word in sentence for word in ['احساس', 'متاسفم', 'درکت']):
        self.repetition_prevention.add_phrase(sentence, "empathy")
```

## Benefits

1. **Eliminates Word Repetition**: Specifically prevents overuse of words like "کمک"
2. **Natural Conversation**: More varied and natural responses
3. **Better User Experience**: Users don't notice repetitive patterns
4. **Professional Quality**: Higher quality conversation flow
5. **Scalable Solution**: Works across all conversation states
6. **Specific Problem Solving**: Addresses the exact repetition issues identified

## Maintenance

### Adding New Problematic Words
To add new words to track:
```python
self.problematic_words['new_word'] = 0
```

### Monitoring Usage
The system automatically tracks:
- Which words are used most frequently
- When words exceed usage thresholds
- Which alternatives are most effective

## Future Enhancements

1. **Per-User Word Tracking**: Store word usage per user
2. **Dynamic Word Detection**: Automatically identify new problematic words
3. **Context-Aware Alternatives**: Choose alternatives based on conversation context
4. **Learning System**: Learn from user preferences and adjust accordingly
5. **Sentiment-Based Alternatives**: Choose alternatives based on user emotion

## Conclusion

This enhanced global repetition prevention system specifically addresses the "کمک" repetition problem and similar issues. By tracking word frequency and providing specific alternatives, the bot maintains high-quality, varied interactions without repetitive responses. The system is designed to be both comprehensive and targeted, ensuring natural conversation flow while preventing the specific repetition patterns that were identified in user conversations.
