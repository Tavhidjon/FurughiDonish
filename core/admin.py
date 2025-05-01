from django.contrib import admin
from .models import Lesson, Quiz, UserProgress, Question, Answer, Student

admin.site.register(Lesson)
admin.site.register(Quiz)
admin.site.register(UserProgress)
admin.site.register(Question)
admin.site.register(Answer)

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('student_id', 'user', 'grade_level', 'enrollment_date')
    search_fields = ('student_id', 'user__username', 'user__email')
    list_filter = ('grade_level', 'enrollment_date')