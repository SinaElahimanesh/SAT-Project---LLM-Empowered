from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Message

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
