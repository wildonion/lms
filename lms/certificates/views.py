from functools import reduce
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_302_FOUND, HTTP_404_NOT_FOUND, HTTP_406_NOT_ACCEPTABLE, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from certificates.models import Certificate
from courses.models import User_Course
from users.utils import decode_token
from users.models import Point
from .serializers import CertificateSerializer


class CertificateListView(generics.ListAPIView):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer

    def post(self, request, *args, **kwargs):
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
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response({"message": f"Access denied for this user with none {groups} group"},
                                        status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                all_user_certs_for_superuser = False if "user_id" in request.data else True
                if all_user_certs_for_superuser:
                    all_certificates = self.list(request, *args, **kwargs)
                    if all_certificates.data:
                        for cert in all_certificates.data:
                            if cert["content"] != None:
                                cert["content"] = cert["content"][21:]
                    response.data = {"message": token_msg, "data": all_certificates.data}
                    response.status_code = HTTP_200_OK
                else:
                    find_user_courses = User_Course.objects.filter(user_id=request.data["user_id"])
                    if find_user_courses.exists():
                        user_course_id_list = list(find_user_courses.all().values_list('id'))
                        find_user_certs = Certificate.objects.filter(reduce(lambda x, y: x | y, [Q(user_course_id=item) for item in user_course_id_list]))
                        if find_user_certs.exists():
                            serializer = CertificateSerializer(instance=find_user_certs, many=True)
                            response.data = {"message": token_msg, "data": serializer.data}
                            response.status_code = HTTP_200_OK
                        else:
                            response.data = {"message": token_msg, "data": []}
                            response.status_code = HTTP_404_NOT_FOUND
                    else:
                        response.data = {"message": token_msg, "data": []}
                        response.status_code = HTTP_404_NOT_FOUND
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response



class CertificateCreateView(generics.CreateAPIView):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer

    def post(self, request, *args, **kwargs):
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
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response({"message": f"Access denied for this user with none {groups} group"},
                                        status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                is_user_create_cert = False
                user_course_id = request.data["user_course_id"]
                find_cert = Certificate.objects.filter(user_course_id=user_course_id)
                if find_cert.exists():
                    data = find_cert.first()
                    serializer = CertificateSerializer(instance=data)
                    response.data = {"message": token_msg, "data": serializer.data}    
                    response.status_code = HTTP_302_FOUND
                else:
                    if user_group.first().name == "student":
                        user_course = User_Course.objects.filter(id=user_course_id)
                        if user_course.exists():
                            if request.data["cert_type"] == "Exam" or request.data["cert_type"] == "exam":
                                points = 10
                            if request.data["cert_type"] == "Course" or request.data["cert_type"] == "course":
                                points = 20
                            user_id = User_Course.objects.filter(id=user_course_id).first().user_id
                            user_point = Point.objects.filter(user_id=user_id)
                            if user_point.exists():
                                Point.objects.filter(id=user_point.first().id).update(points=points)
                                is_user_create_cert = True
                            else:
                                response.data = {'message': token_msg, 'error': "Wrong user group for issuing certificate"} # NOTE - this user has no points perhaps it's a superuser made by django!!!
                                response.status_code = HTTP_406_NOT_ACCEPTABLE
                        else:
                            return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
                    if user_group.first().name == "superuser" or is_user_create_cert:
                        created_certificate = self.create(request, *args, **kwargs)
                        created_certificate.data["content"] = created_certificate.data["content"][21:] if created_certificate.data["content"] != None else ''
                        response.data = {'message': token_msg, 'data': created_certificate.data}
                        response.status_code = HTTP_201_CREATED
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response



class CertificateEditView(generics.RetrieveUpdateAPIView):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer

    def get(self, request, *args, **kwargs):
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
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response({"message": f"Access denied for this user with none {groups} group"},
                                        status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                if user_group.first().name == "student":
                    user_id = user.first().id
                    user_course = User_Course.objects.filter(user_id=user_id)
                    if not user_course.exists():
                        response.data = {"message": token_msg, "data": []}
                        response.status_code = HTTP_404_NOT_FOUND
                        return response
                user_cert = Certificate.objects.filter(id=self.kwargs.get("pk"))
                if user_cert.exists():
                    data = user_cert.first()
                    serializer = CertificateSerializer(instance=data)
                    response.data = {"message": token_msg, "data": serializer.data}
                    response.status_code = HTTP_200_OK
                if not user_cert.exists():
                    response.data = {"message": token_msg, "data": []}
                    response.status_code = HTTP_404_NOT_FOUND
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response


    def patch(self, request, *args, **kwargs):
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
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response({"message": f"Access denied for this user with none {groups} group"},
                                        status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                updated_cert = self.partial_update(request, *args, **kwargs)
                updated_cert.data["content"] = updated_cert.data["content"][21:] if updated_cert.data["content"] != None else ''
                response.data = {"message": token_msg, "data": updated_cert.data}
                response.status_code = HTTP_200_OK
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response