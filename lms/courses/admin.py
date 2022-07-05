from django.contrib import admin

from .models import Course, Video


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'status', 'slug', 'teacher_id', 'image', ]
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'status', 'slug', 'teacher_id', ]


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    list_display = ['id', 'video_name', 'course_id', 'part', 'created_at', ]
