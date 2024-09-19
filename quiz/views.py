from django.shortcuts import render, redirect, reverse
from . import forms, models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.db.models import Q
from django.core.mail import send_mail
from teacher import models as TMODEL
from student import models as SMODEL
from teacher import forms as TFORM
from student import forms as SFORM
from django.contrib.auth.models import User
from django.contrib.auth import logout as logview
import csv
from io import StringIO
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from .models import Course

def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'quiz/index.html')


def is_teacher(user):
    return user.groups.filter(name='TEACHER').exists()


def is_student(user):
    return user.groups.filter(name='STUDENT').exists()


def afterlogin_view(request):
    if is_student(request.user):
        return redirect('student/student-dashboard')

    elif is_teacher(request.user):
        accountapproval = TMODEL.Teacher.objects.all().filter(user_id=request.user.id, status=True)
        # return redirect('teacher/teacher-dashboard')
        if not accountapproval:
             return render(request, 'teacher/teacher_wait_for_approval.html')
             
        else:
            return redirect('teacher/teacher-dashboard')
            
    else:
        return redirect('admin-dashboard')


def adminclick_view(request):
     if request.user.is_authenticated:
         return HttpResponseRedirect('afterlogin')
     return HttpResponseRedirect('adminlogin')


@login_required(login_url='adminlogin')
def admin_dashboard_view(request):
    dict = {
        'total_student': SMODEL.Student.objects.all().count(),
        'total_teacher': TMODEL.Teacher.objects.all().filter(status=True).count(),
        'total_course': models.Course.objects.all().count(),
        'total_question': models.Question.objects.all().count(),
    }
    return render(request, 'quiz/admin_dashboard.html', context=dict)


@login_required(login_url='adminlogin')
def admin_teacher_view(request):
    dict = {
        'total_teacher': TMODEL.Teacher.objects.all().filter(status=True).count(),
        'pending_teacher': TMODEL.Teacher.objects.all().filter(status=False).count(),
        # 'salary': TMODEL.Teacher.objects.all().filter(status=True).aggregate(Sum('salary'))['salary__sum'],
    }
    return render(request, 'quiz/admin_teacher.html', context=dict)


@login_required(login_url='adminlogin')
def admin_view_teacher_view(request):
    teachers = TMODEL.Teacher.objects.all().filter(status=True)
    return render(request, 'quiz/admin_view_teacher.html', {'teachers': teachers})


@login_required(login_url='adminlogin')
def update_teacher_view(request, pk):
    teacher = TMODEL.Teacher.objects.get(id=pk)
    user = TMODEL.User.objects.get(id=teacher.user_id)
    userForm = TFORM.TeacherUserForm(instance=user)
    teacherForm = TFORM.TeacherForm(request.FILES, instance=teacher)
    mydict = {'userForm': userForm, 'teacherForm': teacherForm}
    if request.method == 'POST':
        userForm = TFORM.TeacherUserForm(request.POST, instance=user)
        teacherForm = TFORM.TeacherForm(request.POST, request.FILES, instance=teacher)
        if userForm.is_valid() and teacherForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            teacherForm.save()
            return redirect('admin-view-teacher')
    return render(request, 'quiz/update_teacher.html', context=mydict)


@login_required(login_url='adminlogin')
def delete_teacher_view(request, pk):
    teacher = TMODEL.Teacher.objects.get(id=pk)
    user = User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return HttpResponseRedirect('/admin-view-teacher')


@login_required(login_url='adminlogin')
def admin_view_pending_teacher_view(request):
    teachers = TMODEL.Teacher.objects.all().filter(status=False)
    return render(request, 'quiz/admin_view_pending_teacher.html', {'teachers': teachers})


@login_required(login_url='adminlogin')
def approve_teacher_view(request, pk):
    teacherSalary = forms.TeacherSalaryForm()
    if request.method == 'POST':
        # teacherSalary = forms.TeacherSalaryForm(request.POST)
        
        teacher = TMODEL.Teacher.objects.get(id=pk)
        # teacher.salary = teacherSalary.cleaned_data['salary']
        teacher.status = True
        teacher.save()
        
        return HttpResponseRedirect('/admin-view-teacher')
    return render(request, 'quiz/salary_form.html', {'teacherSalary': teacherSalary})


@login_required(login_url='adminlogin')
def reject_teacher_view(request, pk):
    teacher = TMODEL.Teacher.objects.get(id=pk)
    user = User.objects.get(id=teacher.user_id)
    user.delete()
    teacher.delete()
    return HttpResponseRedirect('/admin-view-pending-teacher')


@login_required(login_url='adminlogin')
def admin_view_teacher_salary_view(request):
    teachers = TMODEL.Teacher.objects.all().filter(status=True)
    return render(request, 'quiz/admin_view_teacher_salary.html', {'teachers': teachers})


@login_required(login_url='adminlogin')
def admin_student_view(request):
    dict = {
        'total_student': SMODEL.Student.objects.all().count(),
    }
    return render(request, 'quiz/admin_student.html', context=dict)


@login_required(login_url='adminlogin')
def admin_view_student_view(request):
    students = SMODEL.Student.objects.all()
    return render(request, 'quiz/admin_view_student.html', {'students': students})


@login_required(login_url='adminlogin')
def update_student_view(request, pk):
    student = SMODEL.Student.objects.get(id=pk)
    user = SMODEL.User.objects.get(id=student.user_id)
    userForm = SFORM.StudentUserForm(instance=user)
    studentForm = SFORM.StudentForm(request.FILES, instance=student)
    mydict = {'userForm': userForm, 'studentForm': studentForm}
    if request.method == 'POST':
        userForm = SFORM.StudentUserForm(request.POST, instance=user)
        studentForm = SFORM.StudentForm(request.POST, request.FILES, instance=student)
        if userForm.is_valid() and studentForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()
            studentForm.save()
            return redirect('admin-view-student')
    return render(request, 'quiz/update_student.html', context=mydict)


@login_required(login_url='adminlogin')
def delete_student_view(request, pk):
    student = SMODEL.Student.objects.get(id=pk)
    user = User.objects.get(id=student.user_id)
    user.delete()
    student.delete()
    return HttpResponseRedirect('/admin-view-student')


@login_required(login_url='adminlogin')
def admin_course_view(request):
    return render(request, 'quiz/admin_course.html')


@login_required(login_url='adminlogin')
def admin_add_course_view(request):
    courseForm = forms.CourseForm()
    if request.method == 'POST':
        courseForm = forms.CourseForm(request.POST)
        if courseForm.is_valid():
            courseForm.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/admin-add-question')
    return render(request, 'quiz/admin_add_course.html', {'courseForm': courseForm})


@login_required(login_url='adminlogin')
def admin_view_course_view(request):
    courses = models.Course.objects.all()
    course_details = []
    for course in courses:
        total_mcq = models.Question.objects.filter(course=course).count()
        total_marks = models.Question.objects.filter(course=course).aggregate(Sum('marks'))['marks__sum']
        course_details.append({
            'course': course,
            'total_mcq': total_mcq,
            'total_marks': total_marks
        })
    
    return render(request, 'quiz/admin_view_course.html', {'courses': courses})


@login_required(login_url='adminlogin')
def delete_course_view(request, pk):
    course = models.Course.objects.get(id=pk)
    course.delete()
    return HttpResponseRedirect('/admin-view-course')


@login_required(login_url='adminlogin')
def admin_question_view(request):
    return render(request, 'quiz/admin_question.html')


@login_required(login_url='adminlogin')
def admin_add_question_view(request):
    questionForm = forms.QuestionForm()
    if request.method == 'POST':
        if 'manual_submit' in request.POST:
            questionForm = forms.QuestionForm(request.POST)
            if questionForm.is_valid():
                question = questionForm.save(commit=False)
                course = models.Course.objects.get(id=request.POST.get('courseID'))
                question.course = course
                question.save()
            else:
                print("form is invalid")
        elif 'csv_submit' in request.POST:
            csv_file = request.FILES['csv_file']
            course_id = request.POST.get('courseID')
            course = models.Course.objects.get(id=course_id)

            # Read the contents of the file into a string
            #csv_data = csv_file.read().decode('utf-8')
            csv_data = csv_file.read().decode('latin1')
            
            

            # Create a file-like object from the string
            csv_io = StringIO(csv_data)

            reader = csv.DictReader(csv_io)
            for row in reader:
                try:
                    marks = int(row['marks'])
                    
                except ValueError:
                    marks = 1
                question = models.Question(
                    course=course,
                    question=row['question'],
                    option1=row['option1'],
                    option2=row['option2'],
                    option3=row['option3'],
                    option4=row['option4'],
                    # Get the correct answer choice value
                    answer=row['answer'],
                    ctg=row['ctg'],
                    marks=marks
                     
                )
                question.save()

                

        return HttpResponseRedirect('/admin-view-question')

    return render(request, 'quiz/admin_add_question.html', {'questionForm': questionForm})



@login_required(login_url='adminlogin')
def admin_view_question_view(request):
    courses = models.Course.objects.all()
    return render(request, 'quiz/admin_view_question.html', {'courses': courses})


@login_required(login_url='adminlogin')
def view_question_view(request, pk):
    questions = models.Question.objects.all().filter(course_id=pk)
    return render(request, 'quiz/view_question.html', {'questions': questions})


@login_required(login_url='adminlogin')
def delete_question_view(request, pk):
    question = models.Question.objects.get(id=pk)
    question.delete()
    return HttpResponseRedirect('/admin-view-question')


@login_required(login_url='adminlogin')
def admin_view_student_marks_view(request):
    students = SMODEL.Student.objects.all()
    return render(request, 'quiz/admin_view_student_marks.html', {'students': students})


@login_required(login_url='adminlogin')
def admin_view_marks_view(request, pk):
    courses = models.Course.objects.all()
    response = render(request, 'quiz/admin_view_marks.html', {'courses': courses})
    response.set_cookie('student_id', str(pk))
    return response


@login_required(login_url='adminlogin')
def admin_check_marks_view(request, pk):
    course = models.Course.objects.get(id=pk)
    student_id = request.COOKIES.get('student_id')
    student = SMODEL.Student.objects.get(id=student_id)
    course_details = []
    total_mcq = models.Question.objects.filter(course=course).count()
    total_marks = models.Question.objects.filter(course=course).aggregate(Sum('marks'))['marks__sum']
    course_details.append({
           
            'total_mcq': total_mcq,
            'total_marks': total_marks
        })

    results = models.Result.objects.all().filter(exam=course).filter(student=student)
    return render(request, 'quiz/admin_check_marks.html', {'results': results ,'total_questions':total_mcq,'total_marks':total_marks})


def aboutus_view(request):
    return render(request, 'quiz/aboutus.html')


def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name = sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            send_mail(str(name) + ' || ' + str(email), message, settings.EMAIL_HOST_USER, settings.EMAIL_RECEIVING_USER,
                      fail_silently=False)
            return render(request, 'quiz/contactussuccess.html')
    return render(request, 'quiz/contactus.html', {'form': sub})

@login_required(login_url='adminlogin')
def logout_user(request):
    logview(request)
    return redirect('studentlogin')

from .forms import CourseForm
@login_required(login_url='adminlogin')
def edit_course(request, pk):
    course = models.Course.objects.get(id=pk)
    if request.method == 'POST':
        courseForm = forms.CourseForm(request.POST, instance=course)
        if courseForm.is_valid():
            course = courseForm.save(commit=False)
            course.save()  # Update the course with the provided pk
            return HttpResponseRedirect('/admin-view-course')
    else:
        courseForm = forms.CourseForm(instance=course)
    return render(request, 'quiz/edit_course.html', {'courseForm': courseForm})


@login_required(login_url='adminlogin')
def update_question_view(request, pk):
    question = models.Question.objects.get(pk=pk)
    if request.method == 'POST':
        form = forms.QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/admin-view-question')
    else:
        form = forms.QuestionForm(instance=question)
    return render(request, 'quiz/update_question.html', {'form': form})