from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions, generics

from src.course import serializers
from src.course.models import Category


class CategoryListView(generics.ListAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Category.api_objects.all_active()
    serializer_class = serializers.CategorySerializer

    @swagger_auto_schema(tags=["course"])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


category_list_view = CategoryListView.as_view()
