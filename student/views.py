from django.shortcuts import render,redirect,reverse
from . import forms,models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from quiz import models as QMODEL
from teacher import models as TMODEL
from django.shortcuts import render, redirect
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import logout as logview
#from .models import Course, Exam
from datetime import datetime
from student import models as SMODEL
from student import forms as SFORM



#for showing signup/login button for student
def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'student/studentclick.html')

def student_signup_view(request):
    userForm=forms.StudentUserForm()
    studentForm=forms.StudentForm()
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=forms.StudentUserForm(request.POST)
        studentForm=forms.StudentForm(request.POST,request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            student=studentForm.save(commit=False)
            student.user=user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        return HttpResponseRedirect('studentlogin')
    return render(request,'student/studentsignup.html',context=mydict)

def is_student(user):
    return user.groups.filter(name='STUDENT').exists()

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    dict={
    
    'total_course':QMODEL.Course.objects.all().count(),
    'total_question':QMODEL.Question.objects.all().count(),
    }
    return render(request,'student/student_dashboard.html',context=dict)

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    today = datetime.today()
    current_time = datetime.now().strftime("%H:%M")
    student = models.Student.objects.get(user_id=request.user.id)
    
    taken_exams = QMODEL.Result.objects.filter(student=student)
    taken_courses = [exam.exam for exam in taken_exams]
    courses = QMODEL.Course.objects.all()
    for course in courses:
        course.already_taken = course in taken_courses
        course_date = course.s_date
        course_time = course.s_time
        if course_date == today.date() and course_time <= today.time():
            course.can_take_exam = True
        else:
            course.can_take_exam = False
    return render(request,'student/student_exam.html',{'courses':courses, 'today': today, 'current_time': current_time})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    total_questions=QMODEL.Question.objects.all().filter(course=course).count()
    questions=QMODEL.Question.objects.all().filter(course=course)
    total_marks=0
    for q in questions:
        total_marks=total_marks + q.marks
    
    return render(request,'student/take_exam.html',{'course':course,'total_questions':total_questions,'total_marks':total_marks})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
@require_http_methods(['GET', 'POST'])
def start_exam_view(request, pk):
    course=QMODEL.Course.objects.get(id=pk)
    questions=QMODEL.Question.objects.all().filter(course=course)
    if request.method=='POST':
        selected_answers = request.POST.getlist('selected_answers[]')
        # Do something with the selected answers
        calculate_marks_view(request, course, questions, selected_answers)
        return HttpResponseRedirect('view-result')
    
    response= render(request,'student/start_exam.html',{'course':course,'questions':questions})
    response.set_cookie('course_id',course.id)
    return response
   


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):
    course_id = request.COOKIES.get('course_id')
    course = QMODEL.Course.objects.get(id=course_id)
    questions = QMODEL.Question.objects.all().filter(course=course)
    

    if request.method == 'POST':
        total_marks = 0  # Initialize total marks
        obtained_marks = 0  # Initialize obtained marks
        student = models.Student.objects.get(user_id=request.user.id)

        # Lists to store correct answers and selected answers
        correct_answers_list = []
        selected_answers_list = []
        category_list = []
        category_list2 = []
        

        # Loop through the questions and calculate the score
        for i, question in enumerate(questions):
            selected_answer = request.POST.get(f'answers_{i+1}')  # Fetch the selected answer
            correct_answer = question.answer.strip().lower()  # Fetch the correct answer from the Question model
            

            # Store the correct and selected answers in lists
            correct_answers_list.append(correct_answer)

            if selected_answer:
                selected_answer = selected_answer.strip().lower()  # Format the selected answer
                selected_answers_list.append(selected_answer)
            else:
                selected_answers_list.append(None)  # If no answer was selected

            # Compare the selected answer with the correct one
            if selected_answer == correct_answer:
                category_list2.append(question.ctg)
                obtained_marks += question.marks  # Add the question marks if correct

            category_list.append(question.ctg)
            total_marks += question.marks
            
        category_percentage = {}
        for category in set(category_list):
            category_count = category_list.count(category)
            category_count2 = category_list2.count(category)
            if category_count != 0:
                category_percentage[category] =f"{(category_count2 / category_count) * 100:.2f}%"
            else:
                category_percentage[category] = "0%"

        student = models.Student.objects.get(user_id=request.user.id)
        result = QMODEL.Result()
        result.exam = course
        result.ans=selected_answers_list
        result.marks = obtained_marks
        result.student = student
        result.ctg = category_percentage
        result.save()

    return HttpResponseRedirect('view-result')
    


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    student = models.Student.objects.get(user_id=request.user.id)
    courses = QMODEL.Course.objects.all()
    
    return render(request,'student/view_result.html',{'courses':courses})
    

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request,pk):
    course=QMODEL.Course.objects.get(id=pk)
    student = models.Student.objects.get(user_id=request.user.id)
    results= QMODEL.Result.objects.all().filter(exam=course).filter(student=student)
    course_details = []
   
    total_mcq = QMODEL.Question.objects.filter(course=course).count()
    total_marks = QMODEL.Question.objects.filter(course=course).aggregate(Sum('marks'))['marks__sum']
    course_details.append({
           
            'total_mcq': total_mcq,
            'total_marks': total_marks
        })
    
    return render(request,'student/check_marks.html',{'results':results,'total_questions':total_mcq,'total_marks':total_marks})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    student = models.Student.objects.get(user_id=request.user.id)
    courses = QMODEL.Course.objects.all()
    return render(request,'student/student_marks.html',{'courses':courses})

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def logout_user(request):
    logview(request)
    return redirect('studentlogin')
@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def profile(request):
    student = models.Student.objects.get(user_id=request.user.id)
    userForm=forms.StudentUserForm(instance=request.user)
    studentForm=forms.StudentForm(instance=student)
    mydict={'userForm':userForm,'studentForm':studentForm}
    if request.method=='POST':
        userForm=forms.StudentUserForm(request.POST,instance=request.user)
        studentForm=forms.StudentForm(request.POST,request.FILES,instance=student)
        if userForm.is_valid() and studentForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            student=studentForm.save(commit=False)
            student.user=user
            student.save()
            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)
        return HttpResponseRedirect('studentlogin')
    return render(request,'student/profile.html',context=mydict)