






from datetime import datetime
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Quizz





# ----------------------------
# --- Quizz Serializer
# ----------------------------
# --------------=============--------------=============--------------=============--------------=============
class QuizzSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quizz
        fields = "__all__"
        
    def create(self, validated_data):
        created_quiz = Quizz.objects.create(**validated_data)
        created_quiz.save()
        return {'message': "Created successfully"}
        
    def update(self, instance, validated_data):
        instance.content = validated_data.get('content', instance.content)
        instance.title = validated_data.get('title', instance.title)
        instance.expiration_time = validated_data.get('expiration_time', instance.expiration_time)
        instance.save()
        updated_quiz = {"teacher_id": instance.teacher_id, "title": instance.title, "content": instance.content, "course_id": instance.course_id, "expiration_time": instance.expiration_time}
        return {'message': "Updated successfully", "data": updated_quiz}
# --------------=============--------------=============--------------=============--------------=============