from django.urls import path
from . import views
from .views import*
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('', views.IntroductionView.as_view(), name='intro'),

    # Lesson URLs
    path('lessons/', views.LessonListView.as_view(), name='lesson-list'),   
    path('lessons/<int:pk>/', views.LessonDetailView.as_view(), name='lesson-detail'),
    path('lessons/create/', LessonCreateView.as_view(), name='lesson-create'),
    path('lessons/<int:pk>/update/', views.LessonUpdateView.as_view(), name='lesson-update'),
    path('lessons/<int:pk>/delete/', views.LessonDeleteView.as_view(), name='lesson-delete'),
    path('lessons/<int:pk>/mark-complete/', views.mark_lesson_complete, name='mark-lesson-complete'),
    path('lesson/<int:lesson_id>/notes/', views.lesson_notes, name='lesson-notes'),

    # Lesson Resource URLs
    path('lessons/<int:lesson_id>/resources/add/', 
         views.LessonResourceCreateView.as_view(), 
         name='lesson-resource-add'),
    path('lessons/<int:lesson_id>/resources/<int:pk>/update/', 
         views.LessonResourceUpdateView.as_view(), 
         name='lesson-resource-update'),
    path('lessons/<int:lesson_id>/resources/<int:pk>/delete/', 
         views.LessonResourceDeleteView.as_view(), 
         name='lesson-resource-delete'),

    # Quiz URLs
    path('quizzes/', views.QuizListView.as_view(), name='quiz-list'),
    path('quizzes/<int:pk>/', views.QuizDetailView.as_view(), name='quiz-detail'),
    path('quizzes/create/', views.QuizCreateView.as_view(), name='quiz-create'),
    path('quizzes/manage/', views.QuizListView.as_view(), name='quiz-list-manage'),
    path('quizzes/<int:quiz_id>/questions/add/', 
         views.QuizQuestionCreateView.as_view(), 
         name='quiz-question-create'),
    path('quizzes/<int:pk>/update/', views.QuizUpdateView.as_view(), name='quiz-update'),
    path('quizzes/<int:pk>/delete/', views.QuizDeleteView.as_view(), name='quiz-delete'),
    path('quizzes/<int:pk>/submit/', views.quiz_submit, name='quiz-submit'),

    # UserProgress URLs
    path('progress/', views.UserProgressListView.as_view(), name='progress-list'),
    path('progress/<int:pk>/', views.UserProgressDetailView.as_view(), name='progress-detail'),
    path('progress/<int:pk>/update/', views.UserProgressUpdateView.as_view(), name='progress-update'),

    # Question URLs
    path('questions/', views.QuestionListView.as_view(), name='question-list'),
    path('questions/<int:pk>/', views.QuestionDetailView.as_view(), name='question-detail'),
    path('questions/create/', views.QuestionCreateView.as_view(), name='question-create'),
    path('questions/<int:pk>/update/', views.QuestionUpdateView.as_view(), name='question-update'),
    path('questions/<int:pk>/delete/', views.QuestionDeleteView.as_view(), name='question-delete'),

    # Answer URLs
    path('answers/', views.AnswerListView.as_view(), name='answer-list'),
    path('answers/<int:pk>/', views.AnswerDetailView.as_view(), name='answer-detail'),
    path('questions/<int:question_pk>/answers/create/', views.AnswerCreateView.as_view(), name='answer-create'),
    path('answers/<int:pk>/update/', views.AnswerUpdateView.as_view(), name='answer-update'),
    path('answers/<int:pk>/delete/', views.AnswerDeleteView.as_view(), name='answer-delete'),
    path('chat/', views.chat_page, name='chat'),
    path('ai-chat/', views.chat_with_ai, name='ai_chat'),

    # Student URLs
    path('students/', StudentListView.as_view(), name='student-list'),
    path('students/add/', StudentCreateView.as_view(), name='student-create'),
    path('students/<int:pk>/edit/', StudentUpdateView.as_view(), name='student-update'),
    path('students/<int:pk>/delete/', StudentDeleteView.as_view(), name='student-delete'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student-detail'),

    # Authentication URLs
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),

    # Attendance URLs
    path('attendance/', AttendanceJournalView.as_view(), name='attendance-journal'),
    path('attendance/new-week/', views.create_new_week, name='create-new-week'),
    path('api/attendance/get-record/', views.get_attendance_record, name='get-attendance-record'),
    path('api/attendance/update-reason/', views.update_attendance_reason, name='update-attendance-reason'),
    path('api/attendance/update-attendance/', views.update_attendance, name='update-attendance'),
    path('api/attendance/get-statistics/', views.get_attendance_statistics, name='get-statistics'),

    # Profile URLs
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name='profile-edit'),


]


