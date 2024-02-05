import django_filters
from django.db.models import Q
from django_filters import rest_framework as filters, CharFilter

from src.accounts.models import User


class UserStudentFilter(django_filters.FilterSet):
    q = CharFilter(method='search_filter')
    phone = CharFilter(field_name="phone", lookup_expr="icontains")

    class Meta:
        model = User
        fields = (
            'phone',
            'user_id'
        )

    def search_filter(self, queryset, name, value):
        value_name_last_name = value.split(" ")
        if len(value_name_last_name) > 1:
            queryset = queryset.filter(
                Q(first_name__icontains=value_name_last_name[0]),
                Q(last_name__icontains=value_name_last_name[1])
            )
        else:
            queryset = queryset.filter(
                Q(first_name__icontains=value.capitalize()) |
                Q(last_name__icontains=value.capitalize())
            )
        return queryset
