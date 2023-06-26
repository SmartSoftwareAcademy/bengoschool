from django.urls import path
from .views import *

urlpatterns = [
	path('reporting/', index,name='reporting'),
    path('invoice-detail/', ViewPDF.as_view(), name="invoice-detail"),
    path('pdf_download/', DownloadPDF.as_view(), name="pdf_download"),
]