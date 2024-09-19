from django.db import models

from student.models import Student
class Course(models.Model):
   course_name = models.CharField(max_length=500)
   exam_name = models.CharField(max_length=500,null=True, blank=True)
   total = models.PositiveIntegerField(max_length=10,null=True, blank=True)
   total_mcq= models.PositiveIntegerField(max_length=10,null=True, blank=True)
   secret_key = models.CharField(max_length=50)
   s_date = models.DateField(max_length=100,default='1212',null=True, blank=True) 
   s_time=models.TimeField(max_length=100,null=True, blank=True)
   d_time= models.PositiveIntegerField(max_length=100,null=True, blank=True)
   

   def __str__(self):
        return self.course_name

class Question(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    marks=models.PositiveIntegerField()
    question=models.CharField(max_length=600)
    option1=models.CharField(max_length=200)
    option2=models.CharField(max_length=200)
    option3=models.CharField(max_length=200)
    option4=models.CharField(max_length=200)
   
    cat=(('Option1','Option1'),('Option2','Option2'),('Option3','Option3'),('Option4','Option4'))
    answer=models.CharField(max_length=200)
    ctg=models.CharField(max_length=100,default="journal")


class Result(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    exam = models.ForeignKey(Course,on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now=True)
    ans=models.CharField(max_length=200,default='5')
    ctg=models.CharField(max_length=200,default='5')


