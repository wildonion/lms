


from django.contrib.auth.models import User
from django.db.models import query
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_406_NOT_ACCEPTABLE
from rest_framework.utils import serializer_helpers

from courses.models import Course
from courses.serializers import QuizCourseInfoSerializer
from .models import *
from rest_framework import generics
from .serializers import *
from users.utils import *
from django.db.models import Q
from functools import reduce
import json
from django.core.serializers.json import DjangoJSONEncoder
from courses.models import User_Course





# -------------------------
# --- Create Quizz API
# -------------------------
@api_view(['POST'])
def quizz_create(request):
    response = Response()
    if 'Authorization' in request.headers:
        token = request.headers.get("Authorization")[7:]
        payload = decode_token(token)
        if payload == "decode error":
            response.data = {'message': "Can't decode jwt"}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
        elif payload == "expired":
            response.data = {'message': "Token has been expired"}
            response.status_code = HTTP_401_UNAUTHORIZED
        else:
            user = User.objects.filter(id=payload["user_id"])
            if user.exists():
                token_msg = "Valid token"
                groups = ["superuser", "teacher"]
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none teacher or superuser group"}, status=HTTP_403_FORBIDDEN)
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            serializer = QuizzSerializer(data=request.data)
            if serializer.is_valid():
                resp = serializer.create(serializer.validated_data)
                serializer_data = serializer.data
                serializer_data["response"] = resp
                serializer_data["response"]["token_status"] = token_msg
                response.data = serializer_data["response"]
                response.status_code = HTTP_201_CREATED
            else:
                response.data = serializer.errors
                response.status_code = HTTP_400_BAD_REQUEST
            # /////////////////////////////////////////////////////////////
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response







# -------------------------
# --- Update Quizz API
# -------------------------
@api_view(['POST'])
def quizz_update(request):
    response = Response()
    if 'Authorization' in request.headers:
        token = request.headers.get("Authorization")[7:]
        payload = decode_token(token)
        if payload == "decode error":
            response.data = {'message': "Can't decode jwt"}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
        elif payload == "expired":
            response.data = {'message': "Token has been expired"}
            response.status_code = HTTP_401_UNAUTHORIZED
        else:
            user = User.objects.filter(id=payload["user_id"])
            if user.exists():
                token_msg = "Valid token"
                groups = ["superuser", "teacher"]
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none {groups} group"}, status=HTTP_403_FORBIDDEN)
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            teacher_can_see_related_quizz = False
            if user_group.first().name == "teacher":
                find_quiz = Quizz.objects.filter(id=request.data["id"])
                if find_quiz.exists():
                    find_course = Course.objects.filter(id=find_quiz.first().course_id)
                    if find_course.exists():
                        teacher_id = find_course.first().teacher_id
                        if teacher_id == user.first().id:
                            teacher_can_see_related_quizz = True
                        else:
                            return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
            if user_group.first().name == "superuser" or teacher_can_see_related_quizz:
                quiz_info = Quizz.objects.filter(id=request.data["id"])
                if quiz_info.exists():
                    updated_quiz = quiz_info.update(content=request.data["content"], title=request.data["title"], expiration_time=request.data["expiration_time"])
                    response.data = {"message": token_msg, "data": []}
                    response.status_code = HTTP_200_OK
                else:
                    response.data = {"message": "Quiz not found"}
                    response.status_code = HTTP_404_NOT_FOUND
            # /////////////////////////////////////////////////////////////
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response










# -------------------------
# --- Get All Quizzes API
# -------------------------
@api_view(['GET'])
def get_quizzes(request):
    response = Response()
    if 'Authorization' in request.headers:
        token = request.headers.get("Authorization")[7:]
        payload = decode_token(token)
        if payload == "decode error":
            response.data = {'message': "Can't decode jwt"}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
        elif payload == "expired":
            response.data = {'message': "Token has been expired"}
            response.status_code = HTTP_401_UNAUTHORIZED
        else:
            user = User.objects.filter(id=payload["user_id"])
            if user.exists():
                token_msg = "Valid token"
                groups = ["superuser", "student"]
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none teacher or superuser group"}, status=HTTP_403_FORBIDDEN)
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            if user_group.first().name == "student":
                quizzes_infos = []
                for q in Quizz.objects.all():
                    quiz_info = {}
                    find_course = Course.objects.filter(id=q.course_id)
                    if find_course.exists():
                        serializer = QuizCourseInfoSerializer(instance=find_course.first())
                        quiz_info["course_info"] = serializer.data
                        quiz_info["id"] = q.id
                        quiz_info["title"] = q.title
                        quiz_info["created_at"] = q.created_at
                        quiz_info["course_id"] = q.course_id
                        quizzes_infos.append(quiz_info)
                response.data = {"message": "Fetched successfully", "data": quizzes_infos}
                response.status_code = HTTP_200_OK
            if user_group.first().name == "superuser": 
                serializer = QuizzSerializer(instance=Quizz.objects.all().values(), many=True)
                response.data = {"message": "Fetched successfully", "data": serializer.data}
                response.status_code = HTTP_200_OK
            # /////////////////////////////////////////////////////////////
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response








# -------------------------
# --- Get Single Quizz API
# -------------------------
@api_view(['POST'])
def get_quizz(request):
    response = Response()
    if 'Authorization' in request.headers:
        token = request.headers.get("Authorization")[7:]
        payload = decode_token(token)
        if payload == "decode error":
            response.data = {'message': "Can't decode jwt"}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
        elif payload == "expired":
            response.data = {'message': "Token has been expired"}
            response.status_code = HTTP_401_UNAUTHORIZED
        else:
            user = User.objects.filter(id=payload["user_id"])
            if user.exists():
                token_msg = "Valid token"
                groups = ["superuser", "student", "teacher"]
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none {groups} group"}, status=HTTP_403_FORBIDDEN)
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            teacher_can_see_related_quizz = False
            user_can_see_related_quizz = False
            if user_group.first().name == "teacher":
                find_quiz = Quizz.objects.filter(id=request.data["quiz_id"])
                if find_quiz.exists():
                    find_course = Course.objects.filter(id=find_quiz.first().course_id)
                    if find_course.exists():
                        teacher_id = find_course.first().teacher_id
                        if teacher_id == user.first().id:
                            teacher_can_see_related_quizz = True
                        else:
                            return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
            if user_group.first().name == "student":
                find_quiz = Quizz.objects.filter(id=request.data["quiz_id"])
                if find_quiz.exists():
                    find_user_course = User_Course.objects.filter(user_id=user.first().id, course_id=find_quiz.first().course_id) # NOTE - user must be bought this course to see its quizz
                    if find_user_course.exists(): # NOTE - this user has bought this quiz (course)
                        user_can_see_related_quizz = True
                    else:
                        return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
            if user_group.first().name == "superuser" or user_can_see_related_quizz or teacher_can_see_related_quizz:
                quizz = Quizz.objects.filter(id=request.data["quiz_id"])
                if quizz.exists():
                    data = quizz.all().values()
                    response.data = {"message": token_msg, "data": data}
                    response.status_code = HTTP_200_OK
                else:
                    response.data = {"message": token_msg, "data": []}
                    response.status_code = HTTP_404_NOT_FOUND
            # /////////////////////////////////////////////////////////////
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response








# --------------------------------
# --- Get All Teacher Quizzes API
# --------------------------------
@api_view(['POST'])
def get_teacher_quizzes(request):
    response = Response()
    if 'Authorization' in request.headers:
        token = request.headers.get("Authorization")[7:]
        payload = decode_token(token)
        if payload == "decode error":
            response.data = {'message': "Can't decode jwt"}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
        elif payload == "expired":
            response.data = {'message': "Token has been expired"}
            response.status_code = HTTP_401_UNAUTHORIZED
        else:
            user = User.objects.filter(id=payload["user_id"])
            if user.exists():
                token_msg = "Valid token"
                groups = ["superuser", "teacher"]
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists() or int(request.data["teacher_id"]) != user.first().id:
                    return Response({"message": f"Access denied for this user with none {groups} group"}, status=HTTP_403_FORBIDDEN) 
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            teacher_quizz = Quizz.objects.filter(teacher_id=int(request.data["teacher_id"]))
            if teacher_quizz.exists():
                response.data = {"message": token_msg, "data": teacher_quizz.all().values()}
                response.status_code = HTTP_200_OK
            else:
                response.data = {"message": token_msg, "data": []}
                response.status_code = HTTP_404_NOT_FOUND
            # /////////////////////////////////////////////////////////////
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response





# --------------------------------
# --- Get Single User Quizz API
# --------------------------------
@api_view(['POST'])
def get_user_quizz(request):
    response = Response()
    if 'Authorization' in request.headers:
        token = request.headers.get("Authorization")[7:]
        payload = decode_token(token)
        if payload == "decode error":
            response.data = {'message': "Can't decode jwt"}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
        elif payload == "expired":
            response.data = {'message': "Token has been expired"}
            response.status_code = HTTP_401_UNAUTHORIZED
        else:
            user = User.objects.filter(id=payload["user_id"])
            if user.exists():
                token_msg = "Valid token"
                groups = ["superuser", "student"]
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none {groups} group"}, status=HTTP_403_FORBIDDEN)
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            user_can_see_related_quizz = False
            if user_group.first().name == "student":
                find_quiz = Quizz.objects.filter(id=request.data["quiz_id"])
                if find_quiz.exists():
                    find_user_course = User_Course.objects.filter(user_id=user.first().id, course_id=find_quiz.first().course_id) # NOTE - user must be bought this course to see its quizz
                    if find_user_course.exists(): # NOTE - this user has bought this quiz (course)
                        user_can_see_related_quizz = True
                    else:
                        return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
            if user_group.first().name == "superuser" or user_can_see_related_quizz:
                user_quizz = UserQuizz.objects.filter(quiz_id=request.data["quiz_id"], user_id=user.first().id)
                if user_quizz.exists():
                    data = user_quizz.all().values()
                    response.data = {"message": token_msg, "data": data}
                    response.status_code = HTTP_200_OK
                else:
                    response.data = {"message": token_msg, "data": []}
                    response.status_code = HTTP_200_OK
            # /////////////////////////////////////////////////////////////
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response








# --------------------------------
# --- Update Single User Quizz API
# --------------------------------
@api_view(['POST'])
def update_user_quizz(request):
    response = Response()
    if 'Authorization' in request.headers:
        token = request.headers.get("Authorization")[7:]
        payload = decode_token(token)
        if payload == "decode error":
            response.data = {'message': "Can't decode jwt"}
            response.status_code = HTTP_406_NOT_ACCEPTABLE
        elif payload == "expired":
            response.data = {'message': "Token has been expired"}
            response.status_code = HTTP_401_UNAUTHORIZED
        else:
            user = User.objects.filter(id=payload["user_id"])
            if user.exists():
                token_msg = "Valid token"
                groups = ["superuser", "student"]
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none {groups} group"}, status=HTTP_403_FORBIDDEN)
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            user_can_see_related_quizz = False
            if user_group.first().name == "student":
                find_quiz = Quizz.objects.filter(id=request.data["quiz_id"])
                if find_quiz.exists():
                    find_user_course = User_Course.objects.filter(user_id=user.first().id, course_id=find_quiz.first().course_id) # NOTE - user must be bought this course to see its quizz
                    if find_user_course.exists(): # NOTE - this user has bought this quiz (course)
                        user_can_see_related_quizz = True
                    else:
                        return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
            if user_group.first().name == "superuser" or user_can_see_related_quizz:
                user_quiz_id = request.data["id"]
                quiz_id = request.data["quiz_id"]
                user_id = user.first().id
                current_index_question = request.data["current_index_question"]
                shuffled_content = request.data["shuffled_content"]
                start_time = request.data["start_time"]
                remaining_time = request.data["remaining_time"]
                finish_time = request.data["finish_time"]
                if user_quiz_id != 0:
                    user_quizz = UserQuizz.objects.filter(id=user_quiz_id)
                    if user_quizz.exists():
                        user_quizz.update(current_index_question=current_index_question, 
                                           quiz_id=quiz_id, user_id=user_id, # NOTE - i lost the bet!!!! 
                                           shuffled_content=shuffled_content, 
                                           start_time=start_time, remaining_time=remaining_time, 
                                           finish_time=finish_time)
                        response.data = {"message": token_msg, "data": user_quizz.all().values()}
                        response.status_code = HTTP_200_OK
                else:
                    user_quizz = UserQuizz(current_index_question=current_index_question, 
                                           quiz_id=quiz_id, user_id=user_id, # NOTE - i lost the bet!!!! 
                                           shuffled_content=shuffled_content, 
                                           start_time=start_time, remaining_time=remaining_time, 
                                           finish_time=finish_time)
                    user_quizz.save()
                    user_quiz_data = {"id": user_quizz.id, "current_index_question": user_quizz.current_index_question, "shuffled_content": user_quizz.shuffled_content, 
                                     "start_time": user_quizz.start_time, "remaining_time": user_quizz.remaining_time, "finish_time": user_quizz.finish_time,
                                     "quiz_id": int(user_quizz.quiz_id), "user_id": user_quizz.user_id}
                    response.data = {"message": token_msg, "data": user_quiz_data}
                    response.status_code = HTTP_201_CREATED
            # /////////////////////////////////////////////////////////////
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response