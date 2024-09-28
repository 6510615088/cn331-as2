from django.contrib import admin
from .models import Subject

class SubjectAdmin(admin.ModelAdmin):
    list_display = ('subject_id', 'name', 'semester', 'academic_year', 'max_students', 'open_for_registration')
    list_filter = ('semester', 'academic_year', 'open_for_registration')
    search_fields = ('subject_id', 'name')

admin.site.register(Subject, SubjectAdmin)
