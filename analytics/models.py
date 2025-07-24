from django.db import models
from tickets.models import Ticket

class AgentPerformance(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='agent_performance')
    agent_name = models.CharField(max_length=255)
    response_time = models.FloatField()
    success = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

class AgentPerformanceLog(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='performance_logs')
    agent_name = models.CharField(max_length=255)
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.agent_name} - {self.action} ({self.created_at})"

class Feedback(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name='feedbacks')
    user = models.CharField(max_length=255)
    rating = models.IntegerField()
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback by {self.user} for Ticket {self.ticket_id}"
