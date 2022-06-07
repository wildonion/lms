








from datetime import datetime
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import FunQuiz, UserFunQuiz





# ----------------------------
# --- FunQuizSerializer
# ----------------------------
# --------------=============--------------=============--------------=============--------------=============
class FunQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = FunQuiz
        fields = "__all__"
        
    def create(self, validated_data):
        created_quiz = FunQuiz.objects.create(**validated_data)
        return {'message': "Created successfully"}
        
    def update(self, instance, validated_data):
        instance.time = validated_data.get('time', instance.time)
        instance.qna = validated_data.get('qna', instance.qna)
        instance.result_stmt = validated_data.get('result_stmt', instance.result_stmt)
        instance.save()
        updated_quiz = {"qna": instance.qna, "time": instance.time, "result_stmt": instance.result_stmt}
        return {'message': "Updated successfully", "data": updated_quiz}
# --------------=============--------------=============--------------=============--------------=============

# ----------------------------
# --- UserFunQuiz Serializer
# ----------------------------
# --------------=============--------------=============--------------=============--------------=============
class UserFunQuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserFunQuiz
        fields = "__all__"
        
    def create(self, validated_data):
        created_userfunquiz = UserFunQuiz.objects.create(**validated_data)
        return {'message': "Created successfully"}
        
    def get(self, instance, validated_data):
        instance.user_email = validated_data.get('user_email', instance.user_email)
        instance.result = validated_data.get('result', instance.result)
        instance.result_stmt = validated_data.get('result_stmt', instance.result_stmt)
        funquiz = {"user_email": instance.user_email, "result": instance.result}
        return {'message': "Fetched successfully", "data": funquiz}
# --------------=============--------------=============--------------=============--------------=============

