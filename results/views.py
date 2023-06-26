from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView, View
from students.models import *
from .forms import *
from .models import *
from.utils import *
import json
from django.core import serializers
from datetime import datetime

from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from django.core import serializers
import json
import ast
from django.contrib.staticfiles import finders

from reportlab.platypus import Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.template.loader import get_template
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4,landscape
@login_required
def create_result(request):
    students = Student.objects.distinct()
    if not request.user.is_superuser:
        students=Student.objects.filter(subject__teachers__id=request.user.staff.id).distinct()
    if request.method == "POST":
        # after visiting the second page
        if "finish" in request.POST:
            form = CreateResults(request.POST)
            if form.is_valid():
                subjects = form.cleaned_data["subjects"]
                session = form.cleaned_data["session"]
                term = form.cleaned_data["term"]
                students = request.POST["students"]
                results = []
                for student in students.split(","):
                    stu = Student.objects.get(pk=student)
                    if stu.current_class:
                        for subject in subjects:
                            check = Result.objects.filter(
                                session=session,
                                term=term,
                                current_class=stu.current_class,
                                current_section=stu.current_section,
                                subject=subject,
                                student=stu,
                            ).first()
                            if not check:
                                results.append(
                                    Result(
                                        session=session,
                                        term=term,
                                        current_class=stu.current_class,
                                        current_section=stu.current_section,
                                        subject=subject,
                                        student=stu,
                                    )
                                )

                Result.objects.bulk_create(results)
                return redirect("edit-results")

        # after choosing students
        id_list = request.POST.getlist("students")
        if id_list:
            form = CreateResults(
                initial={
                    "session": request.current_session,
                    "term": request.current_term,
                }
            )
            studentlist = ",".join(id_list)
            return render(
                request,
                "result/create_result_page2.html",
                {"students": studentlist, "form": form, "count": len(id_list)},
            )
        else:
            messages.warning(request, "You didnt select any student.")
    return render(request, "result/create_result.html", {"students": students})


@login_required
def edit_results(request):
    if request.method == "POST":
        formset  = EditResults(request.POST)
        if formset.is_valid():
           for form in formset:
                result = form.save(commit=False)
                # Calculate points_earned based on grading rules
                grading_rules = GradingRules.objects.filter(grading_level__course=result.subject.course).all()
                print(grading_rules)
                total_score = result.test_score + result.exam_score

                for rule in grading_rules:
                    mark_range = rule.mark_range.split("-")
                    min_mark, max_mark = int(mark_range[0]), int(mark_range[1])

                    if min_mark <= total_score <= max_mark:
                        result.points_earned = rule.grade.points
                        result.grade = rule.grade
                        break
                result.save()
        messages.success(request, "Results successfully updated")
        return redirect("edit-results")
    else:
        results = Result.objects.filter(
            session=request.current_session, term=request.current_term
        )
        form = EditResults(queryset=results)
    return render(request, "result/edit_results.html", {"formset": form})

def results_cards_filter(request):
    if request.method == 'POST':
        form = ResultsFilterForm(request.POST)
        if form.is_valid():
            # Process the filter criteria here
            session= form.cleaned_data['session'].id
            term= form.cleaned_data['term'].id
            selected_class= form.cleaned_data['Class'].id
            selected_section= form.cleaned_data['Section'].id
            # Redirect to the next page
            return redirect(f'/results/result/reportcard/all/?session={session}&term={term}&Class={selected_class}&Section={selected_section}')
    else:
        form = ResultsFilterForm()
    return render(request, 'result/results_filter.html', {'form': form,"title":"Report Cards"})

def results_view_filter(request):
    if request.method == 'POST':
        form = ResultsFilterForm(request.POST)
        if form.is_valid():
            # Process the filter criteria here
            session= form.cleaned_data['session'].id
            term= form.cleaned_data['term'].id
            selected_class= form.cleaned_data['Class'].id
            selected_section= form.cleaned_data['Section'].id
            # Redirect to the next page
            return redirect(f'/results/view/all/results/?session={session}&term={term}&Class={selected_class}&Section={selected_section}')
    else:
        form = ResultsFilterForm()
    return render(request, 'result/results_filter.html', {'form': form,"title":"Transcript"})


class ResultListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        selected_class=request.GET.get('Class')
        selected_section=request.GET.get('Section')
        selected_session=request.GET.get('session')
        selected_term=request.GET.get('term')
        #print(selected_class,selected_section)
        section=ClassSection.objects.get(id=selected_section)
        #print(section.name)
        if section.name =='All':
            results = Result.objects.filter(
                session=selected_session, term=selected_term,current_class=selected_class
            ).order_by('subject__name')
        else:
             results = Result.objects.filter(
                session=selected_session, term=selected_term,current_class=selected_class,current_section=selected_section
            ).order_by('subject__name')
        ##prev session results
        prevresults = Result.objects.filter(
            session__to_date__lte=request.current_session.from_date
        ).exclude(term=request.current_term).order_by('session__from_date').all()
        ##get ranking criteria
        config=SiteConfig.objects.filter(key='grading_criteria').first()
        ranking_type=config.value
        # print(ranking_type)
        # print(prevresults)
        bulk = {}
        allsubjects=Subject.objects.values("name").order_by("name")
        prevscores={}
        if prevresults !=None:
            for result in prevresults:
                test_total = 0
                exam_total = 0
                for subject in prevresults:
                    if subject.student == result.student:
                        test_total += subject.test_score
                        exam_total += subject.exam_score
            prevscores.update({result.student.id:(test_total + exam_total)/len(allsubjects)})
        #print('preve',prevscores)
        ##current score
        for result in results:
            test_total = 0
            exam_total = 0
            subjects = []
            for subject in results:
                if subject.student == result.student:
                    subjects.append(subject)
                    test_total += subject.test_score
                    exam_total += subject.exam_score
            positions=calculate_positions(selected_class,selected_term,ranking_type)
            bulk[result.student.id] = {
                "student": result.student,
                "subjects": subjects,
                "allsubjects":allsubjects,
                "test_total": test_total,
                "exam_total": exam_total,
                "total_total": test_total + exam_total,
                "mean_total": f"{(test_total + exam_total)/len(allsubjects):.2f}",
                "mean_grade": result.mean_grade(result.student,ranking_type),
                "deviation": f"{(test_total + exam_total)/len(allsubjects)-prevscores.get(result.student.id):.2f}" if len(prevscores) >0  else 0,
                "stream_pos":positions[0].get(result.student.id),
                "overall_rank":positions[1].get(result.student.id),
            }
        #context = {"results": bulk}
        results=bulk
        school_details=SiteConfig.objects.all()
        name=school_details[0].value
        moto=school_details[1].value
        adres=school_details[2].value
        email=school_details[3].value
        header_text=f"{name}<br/>{moto}<br/>{adres}"
       # Create the PDF document
       # Create a file-like buffer to receive PDF data.
        buffer = BytesIO()

        # Create the PDF object, using the buffer as its "file."
        doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), topMargin=2, bottomMargin=2)
        logo_path = finders.find('school_logo/logo.png')

        # Set up styles for the header and footer.
        styles = getSampleStyleSheet()
        header_style = styles['Heading2']
        header_style.vAlign=1
        footer_style = styles['Normal']
        footer_style.alignment = 2  # Align the text to the right

        # Create a list to hold the elements of the PDF document.
        elements = []

        # Add the school logo and details to the header.
        logo = Image(logo_path, width=100, height=100)
        header_text=Paragraph(header_text, header_style)
        logo.hAlign = 'LEFT'
        # Create a table to hold the logo and header text side by side
        header_table = Table([[logo, header_text]], colWidths=[120, None])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Vertically align the logo and header text
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),  # Horizontally align the logo and header text
        ]))

        elements.extend([header_table, Spacer(20, 20)])
        # elements.extend([logo, Spacer(20, 20), Paragraph(name, header_style), Paragraph(moto, header_style),Paragraph(adres, header_style)])

        data = []

        # Add table headers.
        headers = ['ADM'] + [subject['name'][:3] for subject in allsubjects] + ['CAT', 'Exam', 'T.Marks', 'M.Marks', 'Deviation','Stream Pos', 'Overall Pos','M.Grade']
        data.append(headers)

        # Add student result data to the table.
        for student_id, result_data in results.items():
            row = [result_data['student']]
            subjects = result_data['subjects']
            for subject in subjects:
                row.append(subject.exam_score)
            row += [result_data['test_total'], result_data['exam_total'], result_data['total_total'], result_data['mean_total'], result_data['deviation'], result_data['stream_pos'], result_data['overall_rank'], result_data['mean_grade']]
            data.append(row)

        # Create the table and apply styles.
        table = Table(data, colWidths=None,repeatRows=1)
        table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 2),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
        # Add the table to the PDF document.
        elements.append(table)#add footer
        elements.append(Spacer(20, 20))
        elements.append(Paragraph(f'Email: {email}', footer_style))
        # Build the PDF document and return it as a response.
        doc.build(elements)
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="transcript.pdf"'
        response.write(buffer.getvalue())
        buffer.close()
        return response
        #return context#render(request, "result/all_results.html", context)


def load_student_card(request):
    selected_class=request.GET.get('Class')
    selected_section=request.GET.get('Section')
    selected_session=request.GET.get('session')
    selected_term=request.GET.get('term')
    #print(selected_class,selected_section)
    section=ClassSection.objects.get(id=selected_section)
    #print(section.name)
    if section.name =='All':
        results = Result.objects.filter(
            session=selected_session, term=selected_term,current_class=selected_class
        ).order_by('subject__name')
    else:
            results = Result.objects.filter(
            session=selected_session, term=selected_term,current_class=selected_class,current_section=selected_section
        ).order_by('subject__name')
    ##prev session results
    prevresults = Result.objects.filter(
        session__to_date__lte=request.current_session.from_date
    ).exclude(term=request.current_term).order_by('session__from_date').all()
    ##alresults
    allresults=Result.objects.filter(session=selected_session,current_class=selected_class).order_by('subject__name')
    ##get ranking criteria
    config=SiteConfig.objects.filter(key='grading_criteria').first()
    ranking_type=config.value
    # print(ranking_type)
    # print(prevresults)
    bulk = {}
    allsubjects=Subject.objects.values("name").order_by("name")
    prevscores={}
    if prevresults !=None:
        for result in prevresults:
            test_total = 0
            exam_total = 0
            for subject in prevresults:
                if subject.student == result.student:
                    test_total += subject.test_score
                    exam_total += subject.exam_score
        prevscores.update({result.student.id:(test_total + exam_total)/len(allsubjects)})
    #print('preve',prevscores)
    ##current score
    for result in results:
        test_total = 0
        exam_total = 0
        total_points=0
        subjects = []
        for subject in results:
            if subject.student == result.student:
                subjects.append(subject)
                test_total += subject.test_score
                exam_total += subject.exam_score
                total_points+=result.points_earned
        positions=calculate_positions(selected_class,selected_term,ranking_type)
        session=AcademicSession.objects.get(id=selected_session)
        bulk[result.student.id] = {
            "student": result.student,
            "subjects": subjects,
            "allsubjects":allsubjects,
            "test_total": test_total,
            "exam_total": exam_total,
            "total_total": test_total + exam_total,
            "mean_total": f"{(test_total + exam_total)/len(allsubjects):.2f}",
            "mean_grade": result.mean_grade(result.student,ranking_type),
            "total_points":total_points,
            "mean_points":total_points/len(allsubjects),
            "deviation": f"{(test_total + exam_total)/len(allsubjects)-prevscores.get(result.student.id):.2f}" if len(prevscores) >0  else 0,
            "stream_pos":positions[0].get(result.student.id),
            "overall_rank":positions[1].get(result.student.id),
            "class_total": Result.objects.filter(session=selected_session, term=selected_term,current_class=selected_class).values("student").distinct().count(),
            "stream_total":Result.objects.filter(session=selected_session, term=selected_term,current_class=selected_class,current_section=selected_section).values("student").distinct().count(),
            "term":selected_term,
            "year":session.name[:4]
        }
    context = {"results": bulk}
    return render(request,'result/report-card.html',context)