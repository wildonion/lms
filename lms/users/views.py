






from .models import OTPModel
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializers import *
from .models import *
from .utils import generate_access_token, generate_refresh_token, decode_token
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_403_FORBIDDEN, HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, HTTP_406_NOT_ACCEPTABLE
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate
from django.db.models import Q
from functools import reduce
from courses.models import Course, User_Course










############## ==================-----------------------==================-----------------------==================-----------------------
############## ==================-----------------------==================-----------------------==================-----------------------
#                                                              AUTHORIZED ROUTES
############## ==================-----------------------==================-----------------------==================-----------------------
############## ==================-----------------------==================-----------------------==================-----------------------









# -------------------------
# --- User Update Status
# -------------------------
@api_view(['POST'])
def user_update_status(request):
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
                groups = ["superuser"]
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none {groups} group"}, status=HTTP_403_FORBIDDEN) 
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            serializer = StatusSerializer(data=request.data)
            if serializer.is_valid():
                user_info = User.objects.filter(id=request.data["user_id"])
                if user_info.exists():
                    resp = serializer.update(user_info.first(), serializer.validated_data)
                    serializer_data = serializer.data
                    serializer_data["response"] = resp
                    serializer_data["response"]["token_status"] = token_msg
                    response.data = serializer_data["response"]
                    response.status_code = HTTP_201_CREATED
                else:
                    response.data = {"message": "User not found"}
                    response.status_code = HTTP_404_NOT_FOUND
            else:
                response.data = serializer.errors
                response.status_code = HTTP_400_BAD_REQUEST
            # ///////////////////////////////////////////////////////////// 
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response











# -------------------------
# --- User Update Group
# -------------------------
@api_view(['POST'])
def user_update_group(request):
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
                groups = ["superuser"]
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none {groups} group"}, status=HTTP_403_FORBIDDEN) 
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            serializer = GroupSerializer(data=request.data)
            if serializer.is_valid():
                user_info = User.objects.filter(id=request.data["user_id"])
                if user_info.exists():
                    resp = serializer.update(user_info.first(), serializer.validated_data)
                    serializer_data = serializer.data
                    serializer_data["response"] = resp
                    serializer_data["response"]["token_status"] = token_msg
                    response.data = serializer_data["response"]
                    response.status_code = HTTP_201_CREATED
                else:
                    response.data = {"message": "User not found"}
                    response.status_code = HTTP_404_NOT_FOUND
            else:
                response.data = serializer.errors
                response.status_code = HTTP_400_BAD_REQUEST
            # ///////////////////////////////////////////////////////////// 
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response






# -------------------------
# --- User Update Password
# -------------------------
@api_view(['POST'])
def user_edit_password(request):
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
                groups = ["superuser", "admin", "student", "teacher"]
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none {groups} group"}, status=HTTP_403_FORBIDDEN) 
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            serializer = PasswordSerializer(data=request.data)
            if serializer.is_valid():
                user_info = User.objects.filter(id=request.data["user_id"])
                if user_info.exists():
                    resp = serializer.update(user_info.first(), serializer.validated_data)
                    serializer_data = serializer.data
                    serializer_data["response"] = resp
                    serializer_data["response"]["token_status"] = token_msg
                    response.data = serializer_data["response"]
                    response.status_code = HTTP_200_OK
                else:
                    response.data = {"message": "User not found"}
                    response.status_code = HTTP_404_NOT_FOUND
            else:
                response.data = serializer.errors
                response.status_code = HTTP_400_BAD_REQUEST
            # ///////////////////////////////////////////////////////////// 
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response






# ------------------------------
# --- User Update Image Profile
# ------------------------------
@api_view(['POST'])
def user_upload_profile(request):
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
                groups = ["superuser", "admin", "student", "teacher"]
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none {groups} group"}, status=HTTP_403_FORBIDDEN)
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            serializer = ImageSerializer(data=request.data)
            if serializer.is_valid():
                profile_info = Profile.objects.filter(user_id=request.data["user_id"])
                if profile_info.exists():
                    resp = serializer.update(profile_info.first(), serializer.validated_data)
                    serializer_data = serializer.data
                    serializer_data["response"] = resp
                    serializer_data["response"]["token_status"] = token_msg
                    response.data = serializer_data["response"]
                    response.status_code = HTTP_200_OK
                else:
                    response.data = {"message": "User not found"}
                    response.status_code = HTTP_404_NOT_FOUND
            else:
                response.data = serializer.errors
                response.status_code = HTTP_400_BAD_REQUEST
            # ///////////////////////////////////////////////////////////// 
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response
    
    
    



# -------------------------
# --- User Update Profile
# -------------------------
@api_view(['POST'])
def user_edit_profile(request):
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
            if user.exists() and user.first().id == int(request.data["user_id"]):
                token_msg = "Valid token"
                groups = ["superuser", "admin", "student", "teacher"]
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none {groups} group"}, status=HTTP_403_FORBIDDEN)
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            serializer = ProfileSerializer(data=request.data)
            if serializer.is_valid():
                resp = serializer.create(serializer.validated_data)
                serializer_data = serializer.data
                serializer_data["response"] = resp
                serializer_data["response"]["token_status"] = token_msg
                response.data = serializer_data["response"]
                response.status_code = HTTP_200_OK
            else:
                response.data = serializer.errors
                response.status_code = HTTP_400_BAD_REQUEST
            # /////////////////////////////////////////////////////////////
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response
    
    







# -------------------------------------------
# --- Verify Media Path Request
# -------------------------------------------
@api_view(['GET'])
def check_media(request):
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
                groups = ["superuser", "admin", "student", "teacher"]
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none {groups} group"}, status=HTTP_403_FORBIDDEN)
            else: 
                return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
            # /////////////////// ACCESS GRANTED LOGICS ///////////////////
            user_id = user.first().id
            course_id = 0 if request.path[22:24] == None else int(request.path[22:24]) 
            if user_group.first().name == "student":
                if course_id == 0:
                    response.data = {'message': token_msg, "error": "Course id is none"}
                    response.status_code = HTTP_406_NOT_ACCEPTABLE 
                else:
                    find_user_course = User_Course.objects.filter(user_id=user_id, course_id=course_id)
                    if find_user_course.exists():
                        response.data = {'message': token_msg, "data": find_user_course.first().id}
                        response.status_code = HTTP_200_OK 
                        response.content_type = ''
                        response["X-Accel-Redirect"] = request.path
                    else:
                        response.data = {'message': token_msg, "data": []}
                        response.status_code = HTTP_404_NOT_FOUND # NOTE - access denied for this user cause he/sher has not bought the course yet
            if user_group.first().name == "teacher": # NOTE - the course must have made by this user in order the teacher see its videos
                find_teacher_course = Course.objects.filter(id=course_id)
                if find_teacher_course.exists():
                    teacher_id = find_teacher_course.first().teacher_id
                    if user_id == teacher_id:
                        response.data = {'message': token_msg, "data": find_teacher_course.first().id}
                        response.status_code = HTTP_200_OK 
                        response.content_type = ''
                        response["X-Accel-Redirect"] = request.path
                    else:
                        return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN) # NOTE - access denied for this user cause he/sher is not the owner of this course
                else:
                    response.data = {'message': token_msg, "data": []}
                    response.status_code = HTTP_404_NOT_FOUND # NOTE - can't find the course
            if user_group.first().name == "admin":
                return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
            if user_group.first().name == "superuser":
                response.data = {'message': token_msg, "data": find_teacher_course.first().id}
                response.status_code = HTTP_200_OK 
                response.content_type = ''
                response["X-Accel-Redirect"] = request.path
            # /////////////////////////////////////////////////////////////
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response











############## ==================-----------------------==================-----------------------==================-----------------------
############## ==================-----------------------==================-----------------------==================-----------------------
#                                                              OPEN ROUTES
############## ==================-----------------------==================-----------------------==================-----------------------
############## ==================-----------------------==================-----------------------==================-----------------------










# ---------------------------
# --- Verify Token Request
# ---------------------------
@api_view(['POST'])
def check_token(request):
    response = Response()
    token_msg = ''
    data = {}
    token = request.data.get("token")
    payload = decode_token(token)
    if payload == "decode error":
        token_msg = "Can't decode jwt"
    elif payload == "expired":
        token_msg = "Token has been expired"
    else:
        user = User.objects.filter(id=payload["user_id"])
        if user.exists():
            groups = ["student", "teacher", "superuser", "admin"]
            user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
            if user_group.exists():
                user_group_name = user_group.first().name
                data["user_group"] = user_group_name
            user_id = user.first().id
            data["status"] = user.first().is_active
            data["user_id"] = user_id
            data["email"] = user.first().email
            data["username"] = user.first().username
            data["first_name"] = user.first().first_name if user.first().first_name else ""
            data["last_name"] = user.first().last_name if user.first().last_name else ""
            profile_info = Profile.objects.filter(user_id=user_id)
            otp_info = OTPModel.objects.filter(user_id=user_id)
            points_info = Point.objects.filter(user_id=user_id)
            user_ssid = USSID.objects.filter(user_id=user_id)
            final_image_url = ""
            if profile_info.exists():
                profile_image = profile_info.first().image
                if profile_image:
                    final_image_url = profile_image.url
            google_image = GoogleMetaData.objects.filter(user_id=user_id)
            if google_image.exists():
                google_image_url = google_image.first().image_url
                if google_image_url:
                    final_image_url = google_image.first().image_url
            data["image_url"] = final_image_url
            data["phone_number"] = otp_info.first().receptor if otp_info.exists() else ""
            data["user_points"] = points_info.first().points if points_info.exists() else 0
            data["user_ssid"] = user_ssid.first().ssid if user_ssid.exists() else ""
            token_msg = "Valid token"
        else:
            token_msg = "Wrong User"
    response.data = {'message': token_msg, "data": data}
    return response




# --------------------------------
# --- Google Login JWT Handler
# --------------------------------
@api_view(['POST'])
def user_google_login(request):
    serializer = GoogleAuthSerializer(data=request.data)
    if serializer.is_valid():
        response = Response()
        resp = serializer.create(serializer.validated_data)
        user = resp["data"] # NOTE - fetched or created user
        access_token = generate_access_token(user)
        response.data = {
            'access': access_token,
            'user': user,
        }
        response.status_code = HTTP_200_OK
        return response
    else:
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)





# --------------------------------
# --- Simple Login JWT Handler
# --------------------------------
@api_view(['POST'])
def user_login(request):
    response = Response()
    email_or_phone_number = request.data.get('email_or_phone_number')
    password = request.data.get('password')
    user_email = User.objects.filter(email=email_or_phone_number)
    user_phone = OTPModel.objects.filter(receptor=email_or_phone_number)
    user_id, user_auth, username = None, None, None
    if user_email.exists():
        if user_email.first().is_active:
            username = user_email.first().username
            user_id = user_email.first().id
        else:
            res = {'message': 'Account suspended'}
            return Response(res, status=HTTP_403_FORBIDDEN)
    elif user_phone.exists():
        user_id = user_phone.first().user_id
        username = User.objects.filter(id=user_id)
        if username.first().is_active:
            username = username.first().username
        else:
            res = {'message': 'Account suspended'}
            return Response(res, status=HTTP_403_FORBIDDEN)
    else:
        res = {'message': 'can not authenticate with the given credentials'}
        return Response(res, status=HTTP_403_FORBIDDEN)
    user_auth = authenticate(request, username=username, password=password)
    if user_auth is None:
        res = {'message': 'wrong credentials'}
        return Response(res, status=HTTP_403_FORBIDDEN)
    user_for_token = {"user_id": user_id, "username": username}
    access_token = generate_access_token(user_for_token)
    response.data = {
        'access': access_token,
        'user': user_for_token,
    }
    response.status_code = HTTP_200_OK
    return response





# --------------------------------
# --- OTP Login JWT Handler
# --------------------------------
@api_view(['POST'])
def user_otp_login(request):
    serializer = OTPForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        response = Response()
        resp = serializer.create(serializer.validated_data)
        if "data" in resp:
            user = resp["data"] # NOTE - fetched or created user
            access_token = generate_access_token(user)
            response.data = {
                'access': access_token,
                'user': user,
            }
            response.status_code = HTTP_200_OK
            return response
        else:
            return Response(resp, status=HTTP_406_NOT_ACCEPTABLE)
    else:
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)




# --------------------------------
# --- OTP Forgot Password Request
# --------------------------------
@api_view(['POST']) # NOTE - allow access to all users
def send_forgot_password_otp_request(request):
    serializer = SendOTPForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        resp = serializer.create(serializer.validated_data)
        serializer_data = serializer.data
        serializer_data["response"] = resp
        return Response(serializer_data["response"], status=HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)    




# -----------------------
# --- OTP Signup Request
# -----------------------
@api_view(['POST']) # NOTE - allow access to all users
def send_signup_otp_request(request):
    serializer = SendOTPSignupSerializer(data=request.data)
    if serializer.is_valid():
        resp = serializer.create(serializer.validated_data)
        serializer_data = serializer.data
        serializer_data["response"] = resp
        return Response(serializer_data["response"], status=HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    
    
    
# -----------------------
# --- OTP Signup Updater
# -----------------------
@api_view(['POST']) # NOTE - allow access to all users
def signup_otp_updater(request):
    serializer = OTPSignupSerializer(data=request.data)
    if serializer.is_valid():
        resp = serializer.create(serializer.validated_data)
        serializer_data = serializer.data
        serializer_data["response"] = resp
        return Response(serializer_data["response"], status=HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)   


# --------------------------------
# --- Get All Users
# --------------------------------
@api_view(['GET'])
def get_all_users(request):
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
                groups = ["superuser"]
                user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                if not user_group.exists():
                    return Response({"message": f"Access denied for this user with none {groups} group"}, status=HTTP_403_FORBIDDEN) 
            users = User.objects.all().values('id', 'username', 'email', 'is_active')
            allowd_groups = ["superuser", "admin", "student", "teacher"]
            data = []
            for u in users:
                if u["id"] == user.first().id:
                    continue
                users_group = User.objects.filter(id=u["id"]).first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in allowd_groups]))
                if users_group.exists():
                    find_phone = OTPModel.objects.filter(user_id=u["id"])
                    user_phone = find_phone.first().receptor if find_phone.exists() else ""
                    data.append({ "user_group": users_group.first().name ,"id": u["id"] , "email": u["email"] , "username": u["username" ] , "phone number": user_phone, "user_status": u["is_active"] } ) 
            response.data = {'message': token_msg , 'data': data}
            response.status_code = HTTP_200_OK
    else:
        response.data = {'message': "Unauthorized"}
        response.status_code = HTTP_401_UNAUTHORIZED
    return response


