from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta, datetime
import time
from .models import *
from .mixins import StaffRequiredMixin, OwnerOrStaffRequiredMixin
from .forms import QuizForm, QuizQuestionForm, StudentCreateForm, CustomUserCreationForm, UserProfileForm, LessonForm
import json
from django.middleware.csrf import get_token
import google.generativeai as genai
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth import login, authenticate
from django.contrib.auth.backends import ModelBackend

# Configure Gemini at module level
genai.configure(api_key=settings.GEMINI_API_KEY)


# Lesson CRUD
class LessonListView(ListView):
    model = Lesson
    template_name = 'lessons/lesson_list.html'
    context_object_name = 'lessons'
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(topic__icontains=q) |
                Q(content__icontains=q)
            )
        return queryset

class LessonDetailView(DetailView):
    model = Lesson
    template_name = 'lessons/lesson_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['resources'] = self.object.resources.all()
        if self.request.user.is_authenticated:
            context['progress'], _ = UserProgress.objects.get_or_create(
                user=self.request.user,
                lesson=self.object,
                defaults={'is_completed': False}
            )
        return context

class LessonCreateView(LoginRequiredMixin, CreateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'lessons/lesson_form.html'
    success_url = reverse_lazy('lesson-list')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

class LessonUpdateView(StaffRequiredMixin, UpdateView):
    model = Lesson
    template_name = 'lessons/lesson_form.html'
    fields = ['topic', 'content', 'created_by_ai']
    success_url = reverse_lazy('lesson-list')

class LessonDeleteView(StaffRequiredMixin, DeleteView):
    model = Lesson
    template_name = 'lessons/lesson_confirm_delete.html'
    success_url = reverse_lazy('lesson-list')

@require_POST
def mark_lesson_complete(request, pk):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'message': 'Please login first'})
    
    try:
        lesson = Lesson.objects.get(pk=pk)
        progress, created = UserProgress.objects.get_or_create(
            user=request.user,
            lesson=lesson
        )
        progress.is_completed = True
        progress.save()
        return JsonResponse({'success': True})
    except Lesson.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Lesson not found'})

class LessonResourceCreateView(StaffRequiredMixin, CreateView):
    model = LessonResource
    template_name = 'lessons/resource_form.html'
    fields = ['title', 'resource_type', 'file', 'url', 'description']

    def form_valid(self, form):
        lesson = get_object_or_404(Lesson, pk=self.kwargs['lesson_id'])
        form.instance.lesson = lesson
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('lesson-detail', kwargs={'pk': self.kwargs['lesson_id']})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lesson'] = get_object_or_404(Lesson, pk=self.kwargs['lesson_id'])
        return context

class LessonResourceUpdateView(UserPassesTestMixin, UpdateView):
    model = LessonResource
    template_name = 'lessons/resource_form.html'
    fields = ['title', 'resource_type', 'file', 'url', 'description']

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return reverse_lazy('lesson-detail', kwargs={'pk': self.object.lesson.id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['lesson'] = self.object.lesson
        context['is_update'] = True
        return context

class LessonResourceDeleteView(UserPassesTestMixin, DeleteView):
    model = LessonResource
    template_name = 'lessons/resource_confirm_delete.html'

    def test_func(self):
        return self.request.user.is_staff

    def get_success_url(self):
        return reverse_lazy('lesson-detail', kwargs={'pk': self.object.lesson.id})

# Quiz CRUD
class QuizListView(ListView):
    model = Quiz
    template_name = 'quizzes/quiz_list.html'
    context_object_name = 'quizzes'

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(lesson__topic__icontains=q) |
                Q(question__icontains=q)
            )
        return queryset

class QuizDetailView(DetailView):
    model = Quiz
    template_name = 'quizzes/quiz_detail.html'
    context_object_name = 'quiz'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['questions'] = self.object.questions.all()
        return context

class QuizCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Quiz
    form_class = QuizForm
    template_name = 'quizzes/quiz_form.html'
    success_url = reverse_lazy('quiz-list')

    def form_valid(self, form):
        messages.success(self.request, 'Quiz created successfully!')
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.is_superuser

class QuizUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Quiz
    template_name = 'quizzes/quiz_form.html'
    fields = ['lesson', 'question', 'correct_answer', 'choices']
    success_url = reverse_lazy('quiz-list')

    def test_func(self):
        return self.request.user.is_superuser

class QuizDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Quiz
    template_name = 'quizzes/quiz_confirm_delete.html'
    success_url = reverse_lazy('quiz-list')

    def test_func(self):
        return self.request.user.is_superuser

class QuizQuestionCreateView(LoginRequiredMixin, CreateView):
    model = QuizQuestion
    form_class = QuizQuestionForm
    template_name = 'quizzes/question_form.html'

    def form_valid(self, form):
        form.instance.quiz_id = self.kwargs['quiz_id']
        messages.success(self.request, 'Question added successfully!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('quiz-detail', kwargs={'pk': self.kwargs['quiz_id']})

@login_required
def quiz_submit(request, pk):
    if request.method != 'POST':
        return redirect('quiz-detail', pk=pk)
    
    quiz = get_object_or_404(Quiz, pk=pk)
    score = 0
    total_questions = quiz.questions.count()
    
    # Calculate score
    for question in quiz.questions.all():
        answer = request.POST.get(f'answer_{question.id}')
        if answer and int(answer) == question.correct_answer:
            score += 1
    
    # Save or update user progress
    progress, created = UserProgress.objects.get_or_create(
        user=request.user,
        lesson=quiz.lesson,
        defaults={'score': 0}
    )
    
    # Update the progress score
    progress.score = (score / total_questions) * 100
    progress.save()
    
    # Add message for user feedback
    messages.success(
        request, 
        f'Quiz submitted! You scored {score} out of {total_questions} questions.'
    )
    
    return redirect('lesson-detail', pk=quiz.lesson.pk)

# UserProgress CRUD
class UserProgressListView(LoginRequiredMixin, ListView):
    model = UserProgress
    template_name = 'progress/progress_list.html'
    context_object_name = 'progress_list'

    def get_queryset(self):
        return UserProgress.objects.filter(user=self.request.user)

class UserProgressDetailView(LoginRequiredMixin, DetailView):
    model = UserProgress
    template_name = 'progress/progress_detail.html'

class UserProgressUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProgress
    template_name = 'progress/progress_form.html'
    fields = ['is_completed', 'quiz_score']
    success_url = reverse_lazy('progress-list')

# Question CRUD
class QuestionListView(ListView):
    model = Question
    template_name = 'questions/question_list.html'
    context_object_name = 'questions'
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(body__icontains=q) |
                Q(tags__icontains=q)
            )
        return queryset

class QuestionDetailView(DetailView):
    model = Question
    template_name = 'questions/question_detail.html'

class QuestionCreateView(LoginRequiredMixin, CreateView):
    model = Question
    template_name = 'questions/question_form.html'
    fields = ['title', 'body', 'tags']
    success_url = reverse_lazy('question-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)  # This will print form errors to console
        return super().form_invalid(form)

class QuestionUpdateView(OwnerOrStaffRequiredMixin, UpdateView):
    model = Question
    template_name = 'questions/question_form.html'
    fields = ['title', 'body', 'tags']
    success_url = reverse_lazy('question-list')

class QuestionDeleteView(OwnerOrStaffRequiredMixin, DeleteView):
    model = Question
    template_name = 'questions/question_confirm_delete.html'
    success_url = reverse_lazy('question-list')

# Answer CRUD
class AnswerListView(ListView):
    model = Answer
    template_name = 'answers/answer_list.html'
    context_object_name = 'answers'
    ordering = ['-created_at']

class AnswerDetailView(DetailView):
    model = Answer
    template_name = 'answers/answer_detail.html'

class AnswerCreateView(LoginRequiredMixin, CreateView):
    model = Answer
    fields = ['content']
    template_name = 'answers/answer_form.html'

    def form_valid(self, form):
        # Set the owner of the answer
        form.instance.owner = self.request.user
        # Get the question from the URL parameter
        question_pk = self.kwargs.get('question_pk')
        form.instance.question_id = question_pk
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add question to context
        question_pk = self.kwargs.get('question_pk')
        context['question'] = Question.objects.get(pk=question_pk)
        return context

    def get_success_url(self):
        # Redirect back to the question detail page
        return reverse_lazy('question-detail', kwargs={'pk': self.kwargs['question_pk']})

class AnswerUpdateView(OwnerOrStaffRequiredMixin, UpdateView):
    model = Answer
    template_name = 'answers/answer_form.html'
    fields = ['content', 'is_ai_generated']
    success_url = reverse_lazy('answer-list')

class AnswerDeleteView(OwnerOrStaffRequiredMixin, DeleteView):
    model = Answer
    template_name = 'answers/answer_confirm_delete.html'
    success_url = reverse_lazy('answer-list')


# Registration View
class RegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('lesson_list')  # Changed from 'home' to 'lesson_list'

    def form_valid(self, form):
        response = super().form_valid(form)
        # Get the user that was just created
        user = form.instance
        # Create UserProfile for the new user
        UserProfile.objects.create(user=user)
        # Authenticate and login with specific backend
        authenticated_user = authenticate(
            self.request,
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1']
        )
        if authenticated_user:
            login(self.request, authenticated_user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(self.request, 'Welcome to TutorFlow! Your account has been created successfully.')
        return response

    def form_invalid(self, form):
        messages.error(self.request, 'Registration failed. Please correct the errors below.')
        return super().form_invalid(form)


# Introduction View
class IntroductionView(TemplateView):
    template_name = 'intro.html'


from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
import json
from django.conf import settings

def chat_page(request):
    return render(request, 'chat.html')  # Make sure this matches your template name

@ensure_csrf_cookie
def chat_with_ai(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message', '')
        user_is_staff = request.user.is_staff
        
        # Different system messages based on user role
        if user_is_staff:
            system_message = """You are Madara, an administrative AI assistant. Your tasks include:
            1. Analyzing student attendance data and providing statistics
            2. Identifying students with attendance issues
            3. Suggesting interventions for improving attendance
            4. Providing detailed reports on student performance
            5. Helping with administrative tasks
            
            When asked about attendance, fetch and analyze the data to provide meaningful insights."""
        else:
            system_message = """You are Madara, a programming mentor. Your tasks include:
            1. Teaching programming concepts clearly and patiently
            2. Providing code examples and explanations
            3. Helping debug code issues
            4. Suggesting best practices
            5. Guiding students through their learning journey"""

        try:
            # If admin asks about attendance, include attendance data
            if user_is_staff and ('attendance' in message.lower() or 'absent' in message.lower()):
                attendance_data = get_attendance_statistics()
                context = f"Here's the current attendance data: {json.dumps(attendance_data)}\n\n"
                message = context + message
            
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(message)
            return JsonResponse({'response': response.text})
            
        except Exception as e:
            print(f"Error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_attendance_statistics():
    """Helper function to get attendance statistics"""
    from django.db.models import Count, F, FloatField
    from django.db.models.functions import Cast
    
    students = Student.objects.annotate(
        total_records=Count('attendancerecord'),
        present_count=Count('attendancerecord', filter=F('attendancerecord__is_present')),
        attendance_rate=Cast(
            F('present_count') * 100.0 / Cast('total_records', FloatField()),
            FloatField()
        )
    ).values('user__first_name', 'user__last_name', 'attendance_rate')
    
    return list(students)


# Student CRUD
class StudentListView(UserPassesTestMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    
    def test_func(self):
        return self.request.user.is_superuser

class StudentCreateView(UserPassesTestMixin, CreateView):
    model = Student
    template_name = 'students/student_form.html'
    form_class = StudentCreateForm  # Use the custom form instead of fields
    success_url = reverse_lazy('student-list')
    
    def form_valid(self, form):
        try:
            # Get user-related data from the form
            user_data = {
                'username': form.cleaned_data['email'],
                'email': form.cleaned_data['email'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'password': User.objects.make_random_password()
            }
            
            # Create the user first
            user = User.objects.create_user(**user_data)
            
            # Create the student and link to user
            student = form.save(commit=False)
            student.user = user
            student.save()
            
            messages.success(self.request, 'Student created successfully!')
            return super().form_valid(form)
            
        except Exception as e:
            messages.error(self.request, f'Error creating student: {str(e)}')
            return self.form_invalid(form)
    
    def test_func(self):
        return self.request.user.is_superuser

class StudentUpdateView(UserPassesTestMixin, UpdateView):
    model = Student
    template_name = 'students/student_form.html'
    fields = ['student_id', 'date_of_birth', 'phone_number', 'address', 'grade_level']
    success_url = reverse_lazy('student-list')
    
    def test_func(self):
        return self.request.user.is_superuser

class StudentDeleteView(UserPassesTestMixin, DeleteView):
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('student-list')
    
    def test_func(self):
        return self.request.user.is_superuser

class StudentDetailView(UserPassesTestMixin, DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'
    
    def test_func(self):
        return self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Student Details: {self.object.user.get_full_name()}"
        return context


# Attendance Journal View
class AttendanceJournalView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Student
    template_name = 'attendance/attendance_journal.html'
    context_object_name = 'students'

    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all attendance records
        attendance_records = AttendanceRecord.objects.select_related('student').all()
        
        # Convert to dictionary for easier lookup
        attendance_dict = {}
        for record in attendance_records:
            if record.student_id not in attendance_dict:
                attendance_dict[record.student_id] = {}
            attendance_dict[record.student_id][record.date.strftime('%Y-%m-%d')] = record
        
        context['attendance_records'] = attendance_dict
        
        # Get weeks data
        today = datetime.now()
        current_monday = today - timedelta(days=today.weekday())
        
        weeks = []
        for week in range(10):
            week_start = current_monday + timedelta(weeks=week)
            week_dates = []
            for day in range(6):  # Monday to Saturday
                date = week_start + timedelta(days=day)
                week_dates.append(date)
            weeks.append({
                'number': week + 1,
                'dates': week_dates,
                'start_date': week_dates[0],
                'end_date': week_dates[-1]
            })
        
        context['weeks'] = weeks
        
        # Calculate statistics
        stats = self.get_attendance_statistics()
        context['attendance_stats'] = json.dumps(stats)
        
        return context

    def get_attendance_statistics(self):
        stats = {
            'labels': [],
            'datasets': []
        }
        
        colors = [
            'rgba(255, 99, 132, 0.8)',   # Red
            'rgba(54, 162, 235, 0.8)',   # Blue
            'rgba(255, 206, 86, 0.8)',   # Yellow
            'rgba(75, 192, 192, 0.8)',   # Teal
            'rgba(153, 102, 255, 0.8)',  # Purple
        ]
        
        students = self.get_queryset()
        records = AttendanceRecord.objects.all()
        
        for i, student in enumerate(students):
            student_records = records.filter(student=student)
            if student_records.exists():
                present_count = student_records.filter(is_present=True).count()
                total_count = student_records.count()
                attendance_rate = (present_count / total_count) * 100 if total_count > 0 else 0
                
                stats['labels'].append(student.user.get_full_name())
                stats['datasets'].append({
                    'label': student.user.get_full_name(),
                    'data': [attendance_rate],
                    'backgroundColor': colors[i % len(colors)],
                    'borderColor': colors[i % len(colors)],
                    'borderWidth': 1
                })
        
        return stats

@login_required
@user_passes_test(lambda u: u.is_staff)
@csrf_exempt
def create_new_week(request):
    if request.method == 'POST':
        try:
            today = datetime.now()
            days_ahead = 7 - today.weekday()
            next_monday = today + timedelta(days=days_ahead)
            next_saturday = next_monday + timedelta(days=5)  # Changed from 4 to 5
            
            students = Student.objects.all()
            
            for student in students:
                current_date = next_monday
                while current_date <= next_saturday:  # Changed to next_saturday
                    record, created = AttendanceRecord.objects.get_or_create(
                        student=student,
                        date=current_date,
                        defaults={
                            'is_present': False,
                            'reason': None,
                            'late_minutes': 0
                        }
                    )
                    current_date += timedelta(days=1)
            
            return JsonResponse({
                'status': 'success',
                'message': 'New week created successfully',
                'redirect_url': reverse('attendance-journal')
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)

@login_required
@user_passes_test(lambda u: u.is_staff)
def get_attendance_record(request):
    student_id = request.GET.get('student_id')
    date = request.GET.get('date')
    
    try:
        record = AttendanceRecord.objects.get(
            student_id=student_id,
            date=date
        )
        return JsonResponse({
            'reason': record.reason,
            'late_minutes': record.late_minutes
        })
    except AttendanceRecord.DoesNotExist:
        return JsonResponse({
            'reason': '',
            'late_minutes': 0
        })

@login_required
@user_passes_test(lambda u: u.is_staff)
@require_POST
def update_attendance_reason(request):
    data = json.loads(request.body)
    student_id = data.get('student_id')
    date = data.get('date')
    reason = data.get('reason')
    late_minutes = data.get('late_minutes', 0)
    
    record, created = AttendanceRecord.objects.get_or_create(
        student_id=student_id,
        date=date,
        defaults={
            'is_present': False,
            'reason': reason,
            'late_minutes': late_minutes
        }
    )
    
    if not created:
        record.reason = reason
        record.late_minutes = late_minutes
        record.save()
    
    return JsonResponse({'status': 'success'})

@login_required
@user_passes_test(lambda u: u.is_staff)
@require_POST
def update_attendance(request):
    data = json.loads(request.body)
    student_id = data.get('student_id')
    date = data.get('date')
    is_present = data.get('is_present')
    
    try:
        record, created = AttendanceRecord.objects.get_or_create(
            student_id=student_id,
            date=datetime.strptime(date, '%Y-%m-%d').date(),
            defaults={'is_present': is_present}
        )
        
        if not created:
            record.is_present = is_present
            record.save()
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@user_passes_test(lambda u: u.is_staff)
def get_attendance_statistics(request):
    try:
        stats = {
            'labels': [],
            'attendance_rates': [],
            'colors': []
        }
        
        students = Student.objects.all()
        for student in students:
            total_days = AttendanceRecord.objects.filter(student=student).count()
            if total_days > 0:
                present_days = AttendanceRecord.objects.filter(
                    student=student,
                    is_present=True
                ).count()
                attendance_rate = (present_days / total_days) * 100
                
                stats['labels'].append(student.user.get_full_name())
                stats['attendance_rates'].append(round(attendance_rate, 1))
                
                if attendance_rate >= 90:
                    color = 'rgba(40, 167, 69, 0.8)'  # Green
                elif attendance_rate >= 75:
                    color = 'rgba(255, 193, 7, 0.8)'  # Yellow
                else:
                    color = 'rgba(220, 53, 69, 0.8)'  # Red
                    
                stats['colors'].append(color)
        
        return JsonResponse(stats)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
def lesson_notes(request, lesson_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        note, created = LessonNote.objects.update_or_create(
            user=request.user,
            lesson_id=lesson_id,
            defaults={'content': content}
        )
        return JsonResponse({'success': True})
    
    elif request.method == 'GET':
        try:
            note = LessonNote.objects.get(user=request.user, lesson_id=lesson_id)
            return JsonResponse({'content': note.content})
        except LessonNote.DoesNotExist:
            return JsonResponse({'content': ''})


# Profile CRUD
class ProfileView(LoginRequiredMixin, DetailView):
    model = UserProfile
    template_name = 'profile/profile_detail.html'
    context_object_name = 'profile'

    def get_object(self):
        return self.request.user.profile

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'profile/profile_edit.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user.profile


@login_required
def dashboard_view(request):
    return render(request, 'core/dashboard.html', {
        'title': 'Dashboard',
    })

