from django import forms
from django.forms import modelformset_factory

from academics.models import AcademicSession, AcademicTerm,StudentClass,ClassSection
from authman.models import *
from .models import Result


class CreateResults(forms.Form):
    session = forms.ModelChoiceField(queryset=AcademicSession.objects.all())
    term = forms.ModelChoiceField(queryset=AcademicTerm.objects.all())
    subjects = forms.ModelMultipleChoiceField(
        queryset=Subject.objects.all(), widget=forms.CheckboxSelectMultiple
    )


EditResults = modelformset_factory(
    Result, fields=("test_score", "exam_score"), extra=0, can_delete=True
)


class ResultsFilterForm(forms.Form):
    session = forms.ModelChoiceField(queryset=AcademicSession.objects.all())
    term = forms.ModelChoiceField(queryset=AcademicTerm.objects.all())
    Class=forms.ModelChoiceField(queryset=StudentClass.objects.all())
    Section=forms.ModelChoiceField(queryset=ClassSection.objects.all())