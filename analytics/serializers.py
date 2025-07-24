from rest_framework import serializers
from .models import AgentPerformance, Feedback, AgentPerformanceLog

class AgentPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentPerformance
        fields = '__all__'

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

class AgentPerformanceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentPerformanceLog
        fields = '__all__'
