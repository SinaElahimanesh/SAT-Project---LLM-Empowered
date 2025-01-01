from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Message, UserMemoryState

# Register the custom User model
admin.site.register(User, UserAdmin)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'text_preview', 'session_id', 'timestamp')
    list_filter = ('user', 'session_id', 'timestamp')
    search_fields = ('text', 'user__username')
    
    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Message Text'

@admin.register(UserMemoryState)
class UserMemoryStateAdmin(admin.ModelAdmin):
    list_display = ('user', 'memory_state_preview', 'last_processed_message')
    list_filter = ('user',)
    search_fields = ('user',)
    
    def memory_state_preview(self, obj):
        return obj.current_memory[:50] + "..." if len(obj.current_memory) > 50 else obj.current_memory
    memory_state_preview.short_description = 'Current Memory'

    def last_processed_message(self, obj):
        if obj.last_processed_message:
            return f"{obj.last_processed_message.text[:30]}... ({obj.last_processed_message.timestamp})"
        return "No messages processed"
    last_processed_message.short_description = 'Last Processed Message'