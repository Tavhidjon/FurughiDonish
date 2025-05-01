from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.conf import settings
from django.db.models.signals import post_save  # Fixed import statement
from django.dispatch import receiver
from datetime import datetime

class Lesson(models.Model):
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('book', 'Book'),
        ('file', 'File'),
    ]

    title = models.CharField(max_length=200)
    subject = models.CharField(
        max_length=100,
        default='General'
    )
    content_type = models.CharField(
        max_length=10,
        choices=CONTENT_TYPE_CHOICES,
        default='file'
    )
    description = models.TextField()
    file = models.FileField(
        upload_to='lesson_files/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['pdf', 'doc', 'docx', 'mp4', 'txt'])]
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.subject} - {self.title}"

    class Meta:
        ordering = ['-created_at']


class LessonResource(models.Model):
    RESOURCE_TYPE_CHOICES = [
        ('book', 'Book'),
        ('video', 'Video'),
        ('document', 'Document')
    ]
    
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    resource_type = models.CharField(max_length=10, choices=RESOURCE_TYPE_CHOICES)
    file = models.FileField(
        upload_to='lesson_resources/',
        validators=[FileExtensionValidator(['pdf', 'mp4', 'doc', 'docx'])],
        null=True,
        blank=True
    )
    url = models.URLField(null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"


class Quiz(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question = models.TextField()
    choices = models.JSONField()
    correct_answer = models.IntegerField()

    def __str__(self):
        return f"Question for {self.quiz.title}"


class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True)
    is_completed = models.BooleanField(default=False)
    quiz_score = models.FloatField(null=True, blank=True)
    last_accessed = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title}"


class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    body = models.TextField()
    tags = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_answered = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Answer(models.Model):
    content = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        related_name='answers'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Answered by {self.owner.username} on {self.created_at.strftime('%B %d, %Y')}"

    @property
    def formatted_date(self):
        return self.created_at.strftime("%b %d, %Y at %I:%M %p")


class Student(models.Model):
    GRADE_CHOICES = [
        ('1', 'First Year'),
        ('2', 'Second Year'),
        ('3', 'Third Year'),
        ('4', 'Fourth Year'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20, unique=True, editable=False)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    enrollment_date = models.DateField(auto_now_add=True)
    grade_level = models.CharField(max_length=1, choices=GRADE_CHOICES)
    
    class Meta:
        ordering = ['-enrollment_date']
        permissions = [
            ("view_student_details", "Can view student details"),
            ("manage_students", "Can manage students"),
        ]

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"

    def save(self, *args, **kwargs):
        if not self.student_id:
            # Generate student ID: FD + Year + Random 4 digits (changed from TF to FD)
            year = datetime.now().strftime('%y')
            last_student = Student.objects.order_by('-student_id').first()
            
            if last_student and last_student.student_id.startswith(f'FD{year}'):
                last_number = int(last_student.student_id[-4:])
                new_number = str(last_number + 1).zfill(4)
            else:
                new_number = '0001'
                
            self.student_id = f'FD{year}{new_number}'
        
        super().save(*args, **kwargs)


class AttendanceRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=False)
    reason = models.CharField(max_length=255, blank=True, null=True)
    late_minutes = models.IntegerField(default=0)

    class Meta:
        unique_together = ['student', 'date']
        ordering = ['date', 'student']

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.date}"


class LessonNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'lesson']


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='profile_avatars/', default='default_avatar.png')
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    location = models.CharField(max_length=100, blank=True)
    interests = models.CharField(max_length=200, blank=True)
    education_level = models.CharField(max_length=50, blank=True)
    joined_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        UserProfile.objects.create(user=instance)

