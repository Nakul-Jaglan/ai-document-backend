from django.contrib import admin
from .models import Document, Conversation

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_type', 'user', 'uploaded_at', 'size')
    list_filter = ('file_type', 'uploaded_at', 'user')
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('uploaded_at', 'size', 'file_type')

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('document', 'user', 'question_preview', 'created_at')
    list_filter = ('created_at', 'document__file_type', 'user')
    search_fields = ('question', 'answer', 'document__title', 'user__username')
    readonly_fields = ('created_at',)
    
    def question_preview(self, obj):
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question
    question_preview.short_description = "Question"
