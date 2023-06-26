from django.db import models
from academics.models import *
from students.models import Student
from authman.models import *
from django.db.models.signals import post_save
from django.dispatch import receiver
from grading.models import *
from django.db.models import Count,Sum

# Create your models here.


class Result(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE)
    term = models.ForeignKey(AcademicTerm, on_delete=models.CASCADE)
    current_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    current_section = models.ForeignKey(
        ClassSection, on_delete=models.CASCADE, default=None, null=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    test_score = models.IntegerField(default=0)
    exam_score = models.IntegerField(default=0)
    grade = models.ForeignKey(Grades,on_delete=models.SET_NULL,default=12,blank=True,null=True)
    points_earned = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["subject"]

    def __str__(self):
        return f"{self.student} {self.session} {self.term} {self.subject}"

    def total_score(self):
        return self.test_score + self.exam_score

    def mean_grade(self,student, grading_type='points'):
        overall_grading = OverallGrading.objects.filter(current=True).first()
        grade = None
        if overall_grading is None or overall_grading.gradingitems.count() == 0:
            return None
        for rule in overall_grading.gradingitems.all():
            if grading_type == 'points':
                marks = sum([result.points_earned for result in student.result_set.all() if result.exam_score > 1])
                range_start, range_end = map(int, rule.points_range.split('-'))
                if range_start <= marks <= range_end:
                    grade = rule.grade
            else:
                marks = sum([(result.test_score + result.exam_score)
                            for result in student.result_set.all() if result.exam_score > 1])
                range_start, range_end = map(int, rule.mark_range.split('-'))
                if range_start <= marks <= range_end:
                    grade = rule.grade
        return grade

    def calculate_subject_position(self):
        subject_results = Result.objects.filter(
                session=self.session,
                term=self.term,
                current_class=self.current_class,
                subject=self.subject
            ).annotate(total_score=Sum('test_score') + Sum('exam_score')).order_by('-total_score')

            # Iterate through the subject results and find the position of the current result
        position = None
        for index, result in enumerate(subject_results, start=1):
            if result == self:
                position = index
                break

        # Count the number of students who took the subject
        total_students = subject_results.count()

        return position

    def total_student(self):
        subject_results = Result.objects.filter(
                session=self.session,
                term=self.term,
                current_class=self.current_class,
                subject=self.subject
            )
            # Iterate through the subject results and find the position of the current result

        # Count the number of students who took the subject
        total_students = subject_results.count()

        return total_students