


from django.contrib.auth.models import User
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.status import HTTP_302_FOUND,HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND, HTTP_406_NOT_ACCEPTABLE

from courses.models import Course
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
# --- Create FUN Quiz API
# -------------------------
@api_view(['POST'])
def funquiz_update(request):
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
                groups = ["admin"]
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none admin group"}, status=HTTP_403_FORBIDDEN)
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            find_funquiz = FunQuiz.objects.all()
            serializer = FunQuizSerializer(data=request.data)
            if find_funquiz.exists():
                if serializer.is_valid():
                    resp = serializer.update(find_funquiz.first(), serializer.validated_data)
                    serializer_data = serializer.data
                    serializer_data["response"] = resp
                    serializer_data["response"]["token_status"] = token_msg
                    response.data = serializer_data["response"]
                    response.status_code = HTTP_201_CREATED
                else:
                    response.data = serializer.errors
                    response.status_code = HTTP_400_BAD_REQUEST
            else:
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





# --------------------------------------------------
# --- Get Single FunQuiz API
# --------------------------------------------------
@api_view(['GET'])
def get_funquiz(request):
    response = Response()
    quiz = FunQuiz.objects.all()
    if quiz.exists():
        serializer = FunQuizSerializer(instance=quiz,many=True)
        response.data = {"message": "Fetched successfully", "data": serializer.data}
        response.status_code = HTTP_200_OK
    else:
        response.data = {"message": "no quiz found", "data": []}
        response.status_code = HTTP_404_NOT_FOUND
    return response






# --------------------------------
# --- add user funquiz
# --------------------------------
@api_view(['POST'])
def add_user_funquiz_result(request):
    response = Response()
    user_email = request.data["user_email"]
    result = request.data["result"]
    create_user_funquiz = UserFunQuiz.objects.create(user_email=user_email, result=result)
    # serializer = UserFunQuizSerializer(instance=create_user_funquiz, many=True)
    response.data = {'message': "Created successfully", 'data': create_user_funquiz.id}
    response.status_code = HTTP_201_CREATED  
    return response





# -------------------------
# --- Get Single FunQuiz API
# -------------------------
@api_view(['GET'])
def get_all_results(request):
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
                groups = ["admin"]
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none {groups} group"}, status=HTTP_403_FORBIDDEN)
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            results = UserFunQuiz.objects.all()
            if results.exists():
                response.data = {"message": token_msg, "data": results.values()}
                response.status_code = HTTP_200_OK
            else:
                response.data = {"message": token_msg, "data": []}
                response.status_code = HTTP_404_NOT_FOUND
            # ///////////////////////////////////////////////////////////////////////////////////////////////
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response


# --------------------------------
# --- add user funquiz email
# --------------------------------
@api_view(['POST'])
def add_user_email(request):
    response = Response()
    user_email = request.data["user_email"]
    find_user_email = UserFunQuiz.objects.filter(user_email=user_email)
    # if find_user_email.exists():
    #     response.data = {'message': "Email already exists", 'data': []}
    #     response.status_code = HTTP_302_FOUND
    # else:
    add_user_email = UserFunQuiz(user_email=user_email)
    add_user_email.save()
    response.data = {'message': "Created successfully", 'data': {"id": add_user_email.id, "user_email": add_user_email.user_email }}
    response.status_code = HTTP_201_CREATED
    return response





# -------------------------
# --- Get User All FunQuizes API
# -------------------------
@api_view(['POST'])
def get_user_last_funquiz(request):
    response = Response()
    if 'user_funquiz_id' in request.data:
        user_funquiz_id = request.data['user_funquiz_id']
        user_funquiz = UserFunQuiz.objects.filter(id=user_funquiz_id)
        if user_funquiz.exists():
            serializer = UserFunQuizSerializer(instance=user_funquiz, many=True)
            response.data = {"message": "Fetched successfully", "data": serializer.data}
            response.status_code = HTTP_200_OK
        else:
            response.data = {"message": "no quiz found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
    elif 'user_email' in request.data:
        user_email = request.data['user_email']
        user_funquizes = UserFunQuiz.objects.filter(user_email=user_email)
        if user_funquizes.exists():
            latest_id = UserFunQuiz.objects.filter(user_email=request.data['user_email']).last().id
            found = UserFunQuiz.objects.filter(user_email=request.data['user_email'], id=latest_id)
            serializer = UserFunQuizSerializer(instance=found,many=True)
            response.data = {"message": "Fetched successfully", "data": serializer.data}
            response.status_code = HTTP_200_OK
        else:
            response.data = {"message": "no quiz found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
    else:
        response.data = {"message": "enter id or email", "data": []}
        response.status_code = HTTP_404_NOT_FOUND
    return response
