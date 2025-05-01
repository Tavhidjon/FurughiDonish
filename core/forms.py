from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import re
from .models import Quiz, QuizQuestion, Student, UserProfile, Lesson

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': ' ',
            'autocomplete': 'off'  # Prevent browser autofill
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': ' ',
            'autocomplete': 'off'
        })
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': ' ',
            'autocomplete': 'off'
        })
    )
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': ' ',
            'autocomplete': 'off'
        })
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': ' ',
            'autocomplete': 'new-password'  # Prevent password autofill
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': ' ',
            'autocomplete': 'new-password'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

class QuizForm(forms.ModelForm):
    class Meta:
        model = Quiz
        fields = ['title', 'lesson', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class QuizQuestionForm(forms.ModelForm):
    class Meta:
        model = QuizQuestion
        fields = ['question', 'choices', 'correct_answer']
        widgets = {
            'choices': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter choices as JSON array: ["Choice 1", "Choice 2", "Choice 3"]'
            })
        }

class StudentCreateForm(forms.ModelForm):
    first_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    grade_level = forms.ChoiceField(
        choices=[
            ('1', 'First Year'),
            ('2', 'Second Year'),
            ('3', 'Third Year'),
            ('4', 'Fourth Year')
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    phone_number = forms.CharField(
        required=False,
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )

    class Meta:
        model = Student
        fields = ['grade_level', 'date_of_birth', 'phone_number', 'address']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar', 'bio', 'birth_date', 'location', 'interests', 'education_level']
        widgets = {
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your location'
            }),
            'interests': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your interests (comma separated)'
            }),
            'education_level': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your education level'
            })
        }

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter lesson title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Enter lesson description',
                'rows': 4
            })
        }