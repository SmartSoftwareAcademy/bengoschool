from django.shortcuts import render
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.views import View
from xhtml2pdf import pisa
from django.core import serializers
import json
import ast

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.template.loader import get_template
from django.conf import settings
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from django.contrib.sessions.models import Session
from django.core import signing


def render_to_pdf(template_src, context_dict={}):
	template = get_template(template_src)
	html  = template.render(context_dict)
	result = BytesIO()
	pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
	if not pdf.err:
		return HttpResponse(result.getvalue(), content_type='application/pdf')
	return None


#Opens up page as PDF
class ViewPDF(View):
    def get(self, request, *args, **kwargs):
        from results.views import ResultListView
        rsv=ResultListView.as_view()
        data=rsv(request)
        pdf = render_to_pdf('result/all_results.html', data)
        return HttpResponse(pdf, content_type='application/pdf')

#Automaticly downloads to PDF file
class DownloadPDF(View):
    data={}
    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        from results.views import ResultListView
        rsv=ResultListView.as_view()
        self.data=rsv(request)

    def get(self, request, *args, **kwargs):
        #return render(request, "result/all_results.html", self.data)
        #def post(self, request, *args, **kwargs):
        student_results =self.data
        # Print the student details
        print(student_results)
         # Prepare the PDF response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="transcript.pdf"'

        # Create the PDF document
        p = canvas.Canvas(response, pagesize=A4)

        # Set font and font size
        p.setFont("Helvetica", 12)

        # Draw header - school details
        p.drawString(50, 750, "School Name")
        p.drawString(50, 730, "Address Line 1")
        p.drawString(50, 710, "Address Line 2")
        # ... add other school details

        # Draw table headers
        table_headers = ['Subject', 'Test Score', 'Exam Score', 'Total Score']
        row_height = 20
        col_width = 100
        y = 650
        for header in table_headers:
            p.drawString(col_width, y, header)
            col_width += 100

        # Draw student results
        y -= row_height
        for student_id, result in student_results['results'].items():
            print(result)
            student_adm = result['student'] # Assuming the student name is an attribute of the student object
            p.drawString(50, y, f"Student: {student_adm}")

            for subject in result['subjects']:
                subject_name = subject.subject.name  # Assuming the subject name is an attribute of the subject object
                test_score = subject.test_score
                exam_score = subject.exam_score
                total_score = test_score + exam_score

                # Draw subject details in the table
                col_width = 100
                p.drawString(col_width, y - row_height, subject_name)
                col_width += 100
                p.drawString(col_width, y - row_height, str(test_score))
                col_width += 100
                p.drawString(col_width, y - row_height, str(exam_score))
                col_width += 100
                p.drawString(col_width, y - row_height, str(total_score))

                y -= row_height

            y -= row_height

        # Draw footer - school email
        p.drawString(50, 50, "Email: school@example.com")

        # Save the PDF document
        p.showPage()
        p.save()
        return response




def index(request):
	context = {}
	return render(request, 'reports/reporting.html', context)