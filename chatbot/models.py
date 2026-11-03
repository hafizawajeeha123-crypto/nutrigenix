from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ChatSession(models.Model):
    user              = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    title             = models.CharField(max_length=150, blank=True)
    created_at        = models.DateTimeField(auto_now_add=True)
    updated_at        = models.DateTimeField(auto_now=True)
    messages_today    = models.PositiveSmallIntegerField(default=0)
    last_message_date = models.DateField(null=True, blank=True)

    FREE_TIER_LIMIT = 10

    class Meta:
        verbose_name        = 'Chat Session'
        verbose_name_plural = 'Chat Sessions'
        ordering            = ['-updated_at']

    def __str__(self):
        return f'{self.user.username} — {self.title or "Untitled session"}'

    def increment_message_count(self):
        today = timezone.now().date()
        if self.last_message_date != today:
            self.messages_today    = 0
            self.last_message_date = today
        self.messages_today += 1
        self.save(update_fields=['messages_today', 'last_message_date'])
        return self.messages_today

    @property
    def is_limit_reached(self):
        today = timezone.now().date()
        if self.last_message_date != today:
            return False
        return self.messages_today >= self.FREE_TIER_LIMIT

    @property
    def messages_remaining(self):
        today = timezone.now().date()
        if self.last_message_date != today:
            return self.FREE_TIER_LIMIT
        return max(self.FREE_TIER_LIMIT - self.messages_today, 0)


class ChatMessage(models.Model):
    ROLE_USER      = 'user'
    ROLE_ASSISTANT = 'assistant'
    ROLE_CHOICES   = [
        (ROLE_USER,      'User'),
        (ROLE_ASSISTANT, 'Assistant'),
    ]

    SOURCE_GROQ   = 'groq'
    SOURCE_GEMINI = 'gemini'
    SOURCE_RULE   = 'rule_based'
    SOURCE_CHOICES = [
        (SOURCE_GROQ,   'Groq (Llama 3)'),
        (SOURCE_GEMINI, 'Google Gemini'),
        (SOURCE_RULE,   'Rule-based fallback'),
    ]

    session    = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role       = models.CharField(max_length=12, choices=ROLE_CHOICES)
    content    = models.TextField()
    source     = models.CharField(max_length=12, choices=SOURCE_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        ordering            = ['created_at']

    def __str__(self):
        preview = self.content[:60] + '…' if len(self.content) > 60 else self.content
        return f'[{self.role}] {preview}'