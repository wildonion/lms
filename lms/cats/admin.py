from django.contrib import admin

from cats.models import Cat


@admin.register(Cat)
class CourseTagsAdmin(admin.ModelAdmin):
    list_display = ['id', 'cat', ]
