from django.urls import path

from .views import *
from reports.views import *

urlpatterns = [
    path("create/", create_result, name="create-result"),
    path("edit-results/", edit_results, name="edit-results"),
    path('result/cards/filters/',results_cards_filter,name='load-cards-filter'),
    path("view/result/filter/", results_view_filter, name="view-results-filter"),
    #path("view/all/results/", ResultListView.as_view(), name="view-results"),
    path("view/results/pdf/", ViewPDF.as_view(), name="view_pdf"),
    path("view/all/results/", ResultListView.as_view(), name="view-results"),
    path('result/reportcard/all/',load_student_card,name='load-cards'),
]
