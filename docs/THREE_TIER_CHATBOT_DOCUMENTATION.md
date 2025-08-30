# Three-Tier Chatbot System Documentation

## Overview

This system implements a three-tier chatbot architecture for research purposes, with each version designed for different experimental groups in a randomized controlled trial (RCT).

## Chatbot Versions

### 1. Alpha Version (Intervention Group)
- **Endpoint**: `/api/message/`
- **Target Group**: `intervention`
- **Features**: 
  - Full state machine implementation
  - SAT (Self-Attachment Technique) knowledge injection
  - Daily exercise recommendations
  - Progress tracking
  - Comprehensive conversation management
  - Memory and context awareness

### 2. Beta Version (Control Group)  
- **Endpoint**: `/api/simple-chat/`
- **Target Group**: `control`
- **Features**:
  - Simplified bot with single system prompt
  - SAT knowledge injection
  - Daily exercises based on user progress
  - Conversation history (last 6 messages)
  - Basic recommendations

### 3. Gamma Version (Placebo Group)
- **Endpoint**: `/api/placebo-chat/`
- **Target Group**: `placebo`
- **Features**:
  - Minimal system prompt: "تو دستیار دلبستگی به خود هستی که وظیفه‌ات کمک به بهتر شدن حال روحی کاربر است."
  - No SAT knowledge injection
  - No daily exercises
  - No progress tracking
  - Basic conversation history (last 6 messages)
  - Minimal recommendations

## User Group Assignment

When users register, they are automatically assigned to one of the three groups using a balanced assignment algorithm:

```python
def get_balanced_group(self):
    """Get balanced group assignment based on current user counts across all three groups"""
    control_count = User.objects.filter(group='control').count()
    intervention_count = User.objects.filter(group='intervention').count()
    placebo_count = User.objects.filter(group='placebo').count()

    # Find the group with the minimum count
    group_counts = {
        'control': control_count,
        'intervention': intervention_count,
        'placebo': placebo_count
    }
    
    # Get the group(s) with minimum count
    min_count = min(group_counts.values())
    min_groups = [group for group, count in group_counts.items() if count == min_count]
    
    # If multiple groups have the same minimum count, randomly choose among them
    return random.choice(min_groups)
```

## API Endpoints Summary

| Group | Endpoint | Bot File | Complexity | SAT Knowledge | Exercises |
|-------|----------|----------|------------|---------------|-----------|
| Intervention | `/api/message/` | `utils.py` (StateMachine) | High | ✅ | ✅ |
| Control | `/api/simple-chat/` | `simple_bot.py` | Medium | ✅ | ✅ |
| Placebo | `/api/placebo-chat/` | `placebo_bot.py` | Low | ❌ | ❌ |

## Database Changes

### Migration 0006: Add Placebo Group
The UserGroup enum was extended to include three options:
- `control` - Simple bot (RCT control group)
- `intervention` - Main chatbot (RCT intervention group)  
- `placebo` - Placebo bot (minimal prompt chatbot)

## File Structure

```
backend/api/
├── bot/
│   ├── utils.py                 # Alpha version (intervention)
│   ├── simple_bot.py           # Beta version (control)
│   └── placebo_bot.py          # Gamma version (placebo)
├── models.py                   # Updated UserGroup enum
├── views.py                    # All three view classes
├── urls.py                     # URL routing for all endpoints
└── migrations/
    └── 0006_alter_user_group.py  # Migration for placebo group
```

## Usage Examples

### Frontend Integration
Based on user's group assignment (returned during login/registration), the frontend should route to the appropriate endpoint:

```javascript
// Example frontend routing logic
const chatEndpoint = {
  'intervention': '/api/message/',
  'control': '/api/simple-chat/', 
  'placebo': '/api/placebo-chat/'
}[userGroup];
```

### Testing
Run the test suite to verify all three chatbot versions:

```bash
python manage.py test api.tests -v 2
```

## Implementation Notes

1. **Consistency**: All three versions maintain the same API response format for frontend compatibility
2. **Isolation**: Each version is completely isolated - no shared state or cross-contamination
3. **Scalability**: The balanced assignment ensures equal distribution across groups
4. **Maintainability**: Each chatbot version is in its own file for easy management

## Research Considerations

This three-tier system allows researchers to:
- Compare effectiveness of full intervention vs. control vs. placebo
- Isolate the impact of specific features (SAT knowledge, exercises, etc.)
- Maintain proper experimental controls
- Ensure balanced group assignments for valid statistical analysis
