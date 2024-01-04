from django import forms
from django_filters import FilterSet, DateFilter, ModelMultipleChoiceFilter
from .models import Post, Category


class PostFilter(FilterSet):
    categories = ModelMultipleChoiceFilter(
        field_name='postcategory__category',
        queryset=Category.objects.all(),
        label='Categories',
    )

    start_date = DateFilter(
        field_name='date_of_creation',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        lookup_expr='gt',
        label='Start Date',
    )

    end_date = DateFilter(
        field_name='date_of_creation',
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        lookup_expr='lt',
        label='End Date',
    )

    class Meta:
        model = Post
        fields = {
            'type_post': ['exact'],
            'title': ['icontains'],
        }
