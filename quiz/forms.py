from django import forms
from django.contrib.auth.models import User
from . import models
from .models import Student



class ContactusForm(forms.Form):
    Name = forms.CharField(max_length=30)
    Email = forms.EmailField()
    Message = forms.CharField(max_length=500,widget=forms.Textarea(attrs={'rows': 3, 'cols': 30}))

class TeacherSalaryForm(forms.Form):
    salary=forms.IntegerField()

class CourseForm(forms.ModelForm):
   
   
   class Meta:
        model = models.Course
        fields = ['course_name', 'exam_name', 'secret_key', 's_date', 's_time', 'd_time','total','total_mcq']

   def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['s_date'].widget.attrs.update({
            'class': 'form-control',
            'type': 'date',
            'placeholder': '2025-12-16'
        })
        self.fields['exam_name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Java'
        })
        self.fields['secret_key'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'exam'
        })
        self.fields['s_time'].widget.attrs.update({
            'class': 'form-control',
            'type': 'time',
            'placeholder': '00:30'
        })
        self.fields['d_time'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter The Minute'
        })
        

class QuestionForm(forms.ModelForm):
    
    #this will show dropdown __str__ method course model is shown on html so override it
    #to_field_name this will fetch corresponding value  user_id present in course model and return it
    courseID=forms.ModelChoiceField(queryset=models.Course.objects.all(),empty_label="Course Name", to_field_name="id")
    class Meta:
        model=models.Question
        fields=['marks','question','option1','option2','option3','option4','answer','ctg']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 3, 'cols': 50})
        }
