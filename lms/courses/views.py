from functools import reduce
import json
from pathlib import Path
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.utils import timezone
from rest_framework import status, generics
from rest_framework.filters import SearchFilter
from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, ListAPIView, RetrieveUpdateAPIView, \
    get_object_or_404
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_302_FOUND, HTTP_403_FORBIDDEN, HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND, \
    HTTP_406_NOT_ACCEPTABLE
from rest_framework.views import APIView
import os
from users.utils import decode_token
from .models import User_Video, Video, Prerequisite, User_Course, Course
from .serializers import CourseViewSerializer, CourseEditSerializer, CourseCreateSerializer, \
    CourseChangeStatusSerializer, VideoUploadSerializer, VideoSerializer, PrerequisiteSerializer, User_CourseSerializer, PrerequisiteFetchSerializer, User_VideoSerializer



class CourseListView(ListAPIView):  # published courses
    queryset = Course.published_objects.all()
    serializer_class = CourseViewSerializer
    filter_backends = [SearchFilter]
    search_fields = ['title', 'short_description', 'content', ]

    def get(self, request, *args, **kwargs):
        response = Response()
        published_course = self.list(request, *args, **kwargs)
        if published_course.data:
            for pc in published_course.data:
                if pc["image"] != None:
                    pc["image"] = pc["image"][21:]
            response.data = {"message": "Fetched successfully", "data": published_course.data}
            response.status_code = HTTP_200_OK
        else:
            response.data = {"message": "No published course found", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
        return response



class AllCourseListView(ListAPIView):  # all courses
    queryset = Course.objects.all()
    serializer_class = CourseViewSerializer

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
                    groups = ["superuser"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response({"message": f"Access denied for this user with none {groups} group"},
                                        status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                all_courses = self.list(request, *args, **kwargs)
                for course in all_courses.data:
                    if course["image"] != None:
                        course["image"] = course["image"][21:]
                response.data = {"message": token_msg, "data": all_courses.data}
                response.status_code = HTTP_200_OK
                # /////////////////////////////////////////////////////////////

        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response



class CourseCreateView(CreateAPIView):
    queryset = Course.published_objects.all()
    serializer_class = CourseCreateSerializer

    def perform_create(self, serializer):
        serializer.save(teacher_id=self.request.data["teacher_id"])  # owner is the logged in user

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
                    groups = ["teacher", "superuser"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists() or int(request.data["teacher_id"]) != user.first().id:
                        return Response({"message": f"Access denied for users with none {groups} group"},
                                        status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                created_course = self.create(request, *args, **kwargs)
                created_course.data["image"] = created_course.data["image"][21:] if created_course.data["image"] != None else ''
                response.data = {"message": token_msg, "data": created_course.data}
                response.status_code = HTTP_201_CREATED
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response



# list courses of each author
class AuthorCourseList(ListAPIView):
    serializer_class = CourseEditSerializer

    def get_queryset(self):
        teacher_id = self.request.data["teacher_id"]
        return Course.objects.filter(teacher_id=teacher_id)

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
                    groups = ["teacher", "superuser"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists() or int(request.data["teacher_id"]) != user.first().id:
                        return Response(
                            {"message": f"Access denied for this user with none {groups} group"},
                            status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                list_courses = self.list(request, *args, **kwargs)
                for course in list_courses.data:
                    if course["image"] != None:
                        course["image"] = course["image"][21:]
                response.data = {"message": token_msg, "data": list_courses.data}
                response.status_code = HTTP_200_OK
            # /////////////////////////////////////////////////////////////

        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response



class CourseEditView(RetrieveUpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseEditSerializer
    lookup_field = 'slug'

    # def perform_update(self, serializer):
    #     serializer.save(author=self.request.data["teacher_id"])

    def get(self, request, *args, **kwargs):
        response = Response()
        instance = self.get_object()
        instance.visit_count += 1
        instance.save()
        serializer = self.get_serializer(instance)
        serializer_data = serializer.data
        serializer_data["image"] = serializer_data["image"][21:] if serializer_data["image"] != None else ''
        response.data = {"message": "Fetched successfully", "data": serializer_data}
        response.status_code = HTTP_200_OK
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
                    groups = ["teacher", "superuser"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response(
                            {"message": f"Access denied for this user with none {groups} group"},
                            status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                teacher_can_see_related_course = False
                if user_group.first().name == "teacher":
                    find_course = Course.objects.filter(slug=request.data["slug"])
                    if find_course.exists():
                        teacher_id = find_course.first().teacher_id
                        if teacher_id == user.first().id:
                            teacher_can_see_related_course = True
                        else:
                            return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
                if user_group.first().name == "superuser" or teacher_can_see_related_course:
                    updated_course = self.partial_update(request, *args, **kwargs)
                    updated_course.data["image"] = updated_course.data["image"][21:] if updated_course.data["image"] != None else ''
                    response.data = {"message": token_msg, "data": updated_course.data}
                    response.status_code = HTTP_200_OK
                # /////////////////////////////////////////////////////////////

        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response



class CourseChangeStatusView(RetrieveUpdateAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseChangeStatusSerializer
    lookup_field = 'slug'

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
                instance = self.get_object()
                if request.data.get("status") == 'published':
                    if instance.publish_time:
                        instance.last_publish_time = timezone.now()
                        instance.status = 'published'
                    else:
                        instance.publish_time = timezone.now()
                        instance.last_publish_time = timezone.now()
                        instance.status = 'published'
                if request.data.get("status") == 'draft':
                    instance.status = 'draft'
                serializer = self.get_serializer(instance, data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_update(serializer)
                serializer_data = serializer.data
                serializer_data["image"] = serializer_data["image"][21:] if serializer_data["image"] != None else '' 
                response.status_code = HTTP_200_OK
                response.data = {"message": token_msg, "data": serializer_data}
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response



class UploadVideoView(APIView):
    serializer_class = VideoUploadSerializer

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
                    groups = ["teacher", "superuser"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response(
                            {"message": f"Access denied for this user with none {groups} group"},
                            status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                teacher_can_see_related_videos = False
                if user_group.first().name == "teacher":
                    find_course = Course.objects.filter(id=request.data["course_id"])
                    if find_course.exists():
                        teacher_id = find_course.first().teacher_id
                        if teacher_id == user.first().id:
                            teacher_can_see_related_videos = True
                        else:
                            return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
                if user_group.first().name == "superuser" or teacher_can_see_related_videos:
                    serializer = VideoUploadSerializer(data=request.data)
                    if serializer.is_valid():
                        name = serializer.data.get('video_name')
                        course_id = serializer.data.get('course_id')
                        image = request.FILES['image']
                        part = serializer.data.get('part')
                        video_duration = serializer.data.get('video_duration')
                        short_description = serializer.data.get('short_description')
                        video_playlist_url = serializer.data.get('video_playlist_url')
                        videos_for_this_course = Video.objects.filter(course_id=course_id)
                        for video in videos_for_this_course:
                            if part == video.part:
                                return Response({"message": {"token": token_msg, "error": "this part already exists"},
                                                "data": serializer.errors}, status=status.HTTP_406_NOT_ACCEPTABLE)
                    else:
                        return Response({"message": token_msg, "data": serializer.errors}, status=status.HTTP_409_CONFLICT)
                    video = Video()
                    video.video_playlist_url = video_playlist_url
                    video.image = image
                    video.video_name = name
                    video.part = part
                    video.short_description = short_description
                    video.course_id = course_id
                    video.video_duration = video_duration
                    video.save()
                    data = {"id": video.id, "video_name": name, "course_id": course_id, "image": video.image.url,
                            "part": part, "short_description": short_description, 'video_duration': video_duration, 'video_playlist_url': video_playlist_url}
                    return Response({"message": token_msg, "data": data}, status=status.HTTP_201_CREATED)
                # /////////////////////////////////////////////////////////////

        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response



class VideoListView(ListAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer

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
                    groups = ["superuser"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response({"message": f"Access denied for this user with none {groups} group"},
                                        status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                videos = self.list(request, *args, **kwargs)
                for v in videos.data:
                        # v["clip"] = v["clip"][21:]
                    v["image"] = v["image"][21:]
                response.data = {"message": token_msg, "data": videos.data}
                response.status_code = HTTP_200_OK
                # /////////////////////////////////////////////////////////////

        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response



class CourseVideoListView(ListAPIView):
    serializer_class = VideoSerializer

    def get_queryset(self):
        course_id = self.request.data["course_id"]
        return Video.objects.filter(course_id=course_id)

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
                    groups = ["teacher", "superuser", "student"]
                    user_group = user.first().groups.filter(reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response(
                            {"message": f"Access denied for this user with none {groups} group"},
                            status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                user_can_see_related_videos = False
                teacher_can_see_related_videos = False
                if user_group.first().name == "teacher":
                    find_course = Course.objects.filter(id=request.data["course_id"])
                    if find_course.exists():
                        teacher_id = find_course.first().teacher_id
                        if teacher_id == user.first().id:
                            teacher_can_see_related_videos = True
                        else:
                            return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
                if user_group.first().name == "student":
                    find_user_course = User_Course.objects.filter(user_id=user.first().id, course_id=request.data["course_id"]) # NOTE - user must be bought this course to see its all videos
                    if find_user_course.exists():
                        user_can_see_related_videos = True
                    else:
                        return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
                if user_group.first().name == "superuser" or user_can_see_related_videos or teacher_can_see_related_videos:
                    videos = self.list(request, *args, **kwargs)
                    for v in videos.data:
                        # if v["clip"] != None:
                            # v["clip"] = v["clip"][21:]
                        v["image"] = v["image"][21:]
                    response.data = {"message": token_msg, "data": videos.data}
                    response.status_code = HTTP_200_OK
                # ////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response



class VideoDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    lookup_field = 'pk'

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
                    groups = ["teacher", "superuser", "student"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response(
                            {"message": f"Access denied for this user with none {groups} group"},
                            status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                user_can_see_related_videos = False
                teacher_can_see_related_videos = False
                if user_group.first().name == "teacher":
                    video_id = self.kwargs.get('pk')
                    find_video = Video.objects.filter(id=video_id)
                    if find_video.exists():
                        course_id = find_video.first().course_id
                        find_course = Course.objects.filter(id=course_id)
                        if find_course.exists():
                           teacher_id = find_course.first().teacher_id
                        if teacher_id == user.first().id:
                            teacher_can_see_related_videos = True
                        if teacher_id != user.first().id:
                            return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
                if user_group.first().name == "student":
                    video_id = self.kwargs.get('pk')
                    find_video = Video.objects.filter(id=video_id)
                    if find_video.exists():
                        course_id = find_video.first().course_id
                        find_user_course = User_Course.objects.filter(user_id=user.first().id, course_id=course_id) # NOTE - user must be bought this course to see its all videos
                        if find_user_course.exists():
                            user_can_see_related_videos = True
                            # NOTE - create a user video info if not exist
                            find_user_video = User_Video.objects.filter(video_id=video_id, user_id=user.first().id, course_id=course_id)
                            if not find_user_video.exists():
                                User_Video.objects.create(video_id=video_id, user_id=user.first().id, course_id=course_id)
                        else:
                            return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
                if user_group.first().name == "superuser" or user_can_see_related_videos or teacher_can_see_related_videos:
                    video_detail = self.retrieve(request, *args, **kwargs)
                    # video_detail.data["clip"] = video_detail.data["clip"][21:]
                    video_detail.data["image"] = video_detail.data["image"][21:]
                    response.data = {"message": token_msg, "data": video_detail.data}
                    response.status_code = HTTP_200_OK
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
                    groups = ["teacher", "superuser", "student"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response(
                            {"message": f"Access denied for this user with none {groups} group"},
                            status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                user_can_see_related_videos = False
                teacher_can_see_related_videos = False
                if user_group.first().name == "teacher":
                    video_id = self.kwargs.get('pk')
                    find_video = Video.objects.filter(id=video_id)
                    if find_video.exists():
                        course_id = find_video.first().course_id
                        find_course = Course.objects.filter(id=course_id)
                        if find_course.exists():
                           teacher_id = find_course.first().teacher_id
                        if teacher_id == user.first().id:
                            teacher_can_see_related_videos = True
                        if teacher_id != user.first().id:
                            return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
                if user_group.first().name == "student":
                    video_id = self.kwargs.get('pk')
                    find_video = Video.objects.filter(id=video_id)
                    if find_video.exists():
                        course_id = find_video.first().course_id
                        find_user_course = User_Course.objects.filter(user_id=user.first().id, course_id=course_id) # NOTE - user must be bought this course to see its all videos
                        if find_user_course.exists():
                            user_can_see_related_videos = True
                        else:
                            return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
                if user_group.first().name == "superuser" or user_can_see_related_videos or teacher_can_see_related_videos:
                    updated_video = self.partial_update(request, *args, **kwargs)
                    updated_video.data["image"] = updated_video.data["image"][21:] if updated_video.data["image"] != None else ''
                    response.data = {"message": token_msg, "data": updated_video.data}
                    response.status_code = HTTP_200_OK
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response
    
    def delete(self, request, *args, **kwargs):
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
                        return Response(
                            {"message": f"Access denied for this user with none {groups} group"},
                            status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                lms_path = str(Path(__file__).parent.parent)
                find_video = Video.objects.filter(id=self.kwargs.get("pk"))
                if find_video.exists():
                    # video_path = lms_path + find_video.first().clip.url
                    image_path = lms_path + find_video.first().image.url 
                    # if os.path.exists(video_path):
                    #     os.remove(video_path)
                    if os.path.exists(image_path):
                        os.remove(image_path)
                deleted_video = self.destroy(request, *args, **kwargs)
                response.data = {"message": token_msg, "data": deleted_video.data}
                response.status_code = HTTP_200_OK
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response
    
    
    
class UserVideosView(generics.RetrieveAPIView):
    queryset = User_Video.objects.all()
    serializer_class = User_VideoSerializer
    
    
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
                        return Response(
                            {"message": f"Access denied for this user with none {groups} group"},
                            status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                course_id = self.request.data["course_id"]
                user_can_see_related_videos = False
                if user_group.first().name == "student":
                    find_user_course = User_Course.objects.filter(user_id=user.first().id, course_id=course_id) # NOTE - user must be bought this course to see its all videos
                    if find_user_course.exists():
                        user_can_see_related_videos = True
                    else:
                        return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
                if user_group.first().name == "superuser" or user_can_see_related_videos:
                    user_videos_data = User_Video.objects.filter(user_id=user.first().id, course_id=course_id)
                    if user_videos_data.exists():
                        serializer = User_VideoSerializer(instance=user_videos_data, many=True)
                        response.data = {"message": token_msg, "data": serializer.data}
                        response.status_code = HTTP_200_OK
                    else:
                        response.data = {"message": token_msg, "data": []}
                        response.status_code = HTTP_404_NOT_FOUND
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response
        


class UserVideoView(generics.RetrieveUpdateAPIView):
    queryset = User_Video.objects.all()
    serializer_class = User_VideoSerializer

    

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
                        return Response(
                            {"message": f"Access denied for this user with none {groups} group"},
                            status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                video_id = self.kwargs.get('pk') # NOTE - the primary key passed to the url is the video id not a user_video record
                user_can_see_related_videos = False
                if user_group.first().name == "student":
                    find_video = Video.objects.filter(id=video_id)
                    if find_video.exists():
                        course_id = find_video.first().course_id
                        find_user_course = User_Course.objects.filter(user_id=user.first().id, course_id=course_id) # NOTE - user must be bought this course to see its all videos
                        if find_user_course.exists():
                            user_can_see_related_videos = True
                        else:
                            return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
                if user_group.first().name == "superuser" or user_can_see_related_videos:
                    user_video_data = User_Video.objects.filter(video_id=video_id, user_id=user.first().id)
                    if user_video_data.exists():
                        serializer = User_VideoSerializer(instance=user_video_data, many=True)
                        response.data = {"message": token_msg, "data": serializer.data}
                        response.status_code = HTTP_200_OK
                    else:
                        response.data = {"message": token_msg, "data": []}
                        response.status_code = HTTP_404_NOT_FOUND
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response

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
                        return Response(
                            {"message": f"Access denied for this user with none {groups} group"},
                            status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                video_id = self.kwargs.get('pk') # NOTE - the primary key passed to the url is the video id not a user_video record
                current_process_percentage = self.request.data["current_process_percentage"]
                user_can_see_related_videos = False
                if user_group.first().name == "student":
                    find_video = Video.objects.filter(id=video_id)
                    if find_video.exists():
                        course_id = find_video.first().course_id
                        find_user_course = User_Course.objects.filter(user_id=user.first().id, course_id=course_id) # NOTE - user must be bought this course to see its all videos
                        if find_user_course.exists():
                            user_can_see_related_videos = True
                        else:
                            return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
                if user_group.first().name == "superuser" or user_can_see_related_videos:
                    find_user_video = User_Video.objects.filter(video_id=video_id, user_id=user.first().id)
                    if find_user_video.exists():
                        find_user_video.update(current_process_percentage=current_process_percentage)
                        serializer = User_VideoSerializer(instance=find_user_video, many=True)
                        response.data = {"message": token_msg, "data": serializer.data}
                        response.status_code = HTTP_200_OK
                    else:
                        response.data = {"message": token_msg, "data": []}
                        response.status_code = HTTP_404_NOT_FOUND
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response

    
    


class PrerequisiteListView(ListAPIView):
    queryset = Prerequisite.objects.all()
    serializer_class = PrerequisiteFetchSerializer

    def get(self, request, *args, **kwargs):
        response = Response()
        prerequisite = self.list(request, *args, **kwargs)
        response.data = {"message": "Fetched successfully", "data": prerequisite.data}
        response.status_code = HTTP_200_OK
        return response



class PrerequisiteCreateView(CreateAPIView):
    queryset = Prerequisite.objects.all()
    serializer_class = PrerequisiteSerializer

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
                    groups = ["teacher", "superuser"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response(
                            {"message": f"Access denied for this user with none {groups} group"},
                            status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                teacher_can_see_related_prereq = False
                if user_group.first().name == "teacher":
                    find_course = Course.objects.filter(id=request.data["main_course"])
                    if find_course.exists():
                        teacher_id = find_course.first().teacher_id
                        if teacher_id == user.first().id:
                            teacher_can_see_related_prereq = True
                        if teacher_id != user.first().id:
                            return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
                if user_group.first().name == "superuser" or teacher_can_see_related_prereq:
                    find_course = Prerequisite.objects.filter(main_course=request.data["main_course"])
                    if find_course.exists():
                        serializer = PrerequisiteFetchSerializer(instance=find_course, many=True)
                        response.data = {"message": token_msg, "data": serializer.data}
                        response.status_code = HTTP_302_FOUND
                    else:
                        created_prerequisite = self.create(request, *args, **kwargs)
                        response.data = {"message": token_msg, "data": created_prerequisite.data}
                        response.status_code = HTTP_200_OK
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response



class PrerequisiteEditView(RetrieveUpdateAPIView):
    queryset = Prerequisite.objects.all()
    serializer_class = PrerequisiteSerializer

    def get_object(self):
        try:
            course_id = Course.objects.filter(slug=self.kwargs.get('slug')).first().id
        except:
            course_id = None
        return get_object_or_404(Prerequisite, main_course=course_id)
    

    def get(self, request, *args, **kwargs):
        response = Response()
        find_course = Course.objects.filter(slug=self.kwargs.get('slug'))
        if find_course.exists():
            prerequisites = Prerequisite.objects.filter(main_course=find_course.first().id)
            serializer = PrerequisiteFetchSerializer(instance=prerequisites, many=True)
            response.data = {"message": "Fetched successfully", "data": serializer.data}
            response.status_code = HTTP_200_OK
        else:
            response.data = {"message": "No course found with this slug", "data": []}
            response.status_code = HTTP_404_NOT_FOUND
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
                    groups = ["teacher", "superuser"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response(
                            {"message": f"Access denied for this user with none {groups} group"},
                            status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                teacher_can_see_related_prereq = False
                if user_group.first().name == "teacher":
                    find_course = Course.objects.filter(id=request.data["main_course"])
                    if find_course.exists():
                        teacher_id = find_course.first().teacher_id
                        if teacher_id == user.first().id:
                            teacher_can_see_related_prereq = True
                        if teacher_id != user.first().id:
                            return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
                if user_group.first().name == "superuser" or teacher_can_see_related_prereq:
                    updated_prerequisite = self.partial_update(request, *args, **kwargs)
                    response.data = {"message": token_msg, "data": updated_prerequisite.data}
                    response.status_code = HTTP_200_OK
                # /////////////////////////////////////////////////////////////

        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response



class User_CourseCreateView(CreateAPIView):
    queryset = User_Course.objects.all()
    serializer_class = User_CourseSerializer

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
                user_id = request.data["user_id"]
                course_id = request.data["course_id"]
                find_user_course = User_Course.objects.filter(user_id=user_id, course_id=course_id)
                if find_user_course.exists():
                    response.data = {"message": token_msg, "data": find_user_course.first()}    
                    response.status_code = HTTP_302_FOUND
                else:
                    created_user_course = self.create(request, *args, **kwargs)
                    response.data = {"message": token_msg, "data": created_user_course.data}
                    response.status_code = HTTP_200_OK
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response



class User_CourseListView(ListAPIView):
    queryset = User_Course.objects.all()
    serializer_class = User_CourseSerializer

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
                all_user_courses_for_superuser = False if "user_id" in request.data else True
                if all_user_courses_for_superuser:
                    user_course = self.list(request, *args, **kwargs)
                    response.data = {"message": token_msg, "data": user_course.data}
                    response.status_code = HTTP_200_OK
                else:
                    find_user_courses = User_Course.objects.filter(user_id=request.data["user_id"])
                    if find_user_courses.exists():
                        serializer = User_CourseSerializer(instance=find_user_courses, many=True)
                        response.data = {"message": token_msg, "data": serializer.data}
                        response.status_code = HTTP_200_OK
                    else:
                        response.data = {"message": token_msg, "data": []}
                        response.status_code = HTTP_404_NOT_FOUND
                # /////////////////////////////////////////////////////////////
        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response



class User_CourseEditView(RetrieveUpdateAPIView):
    queryset = User_Course.objects.all()
    serializer_class = User_CourseSerializer

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
                user_course = []
                if user_group.first().name == "superuser":
                    user_course = User_Course.objects.filter(id=self.kwargs.get("pk"))
                if user_group.first().name == "student":
                    user_id = user.first().id
                    user_course = User_Course.objects.filter(id=self.kwargs.get("pk"), user_id=user_id)
                if user_course.exists():
                    response.data = {"message": token_msg, "data": user_course.all().values()}
                    response.status_code = HTTP_200_OK
                if not user_course.exists():
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
                    groups = ["superuser", "student"]
                    user_group = user.first().groups.filter(
                        reduce(lambda x, y: x | y, [Q(name=item) for item in groups]))
                    if not user_group.exists():
                        return Response({"message": f"Access denied for this user with none {groups} group"},
                                        status=HTTP_403_FORBIDDEN)
                else:
                    return Response({"message": "Wrong user"}, status=HTTP_403_FORBIDDEN)
                # /////////////////// ACCESS GRANTED LOGICS ///////////////////
                if user_group.first().name == "student" and 'payment_info_id' in request.data:
                    return Response({"message": "lock for this user"}, status=HTTP_403_FORBIDDEN)
                updated_user_course = self.partial_update(request, *args, **kwargs)
                response.data = {"message": token_msg, "data": updated_user_course.data}
                response.status_code = HTTP_200_OK
                # /////////////////////////////////////////////////////////////

        else:
            response.data = {'message': "Unauthorized"}
            response.status_code = HTTP_401_UNAUTHORIZED
        return response