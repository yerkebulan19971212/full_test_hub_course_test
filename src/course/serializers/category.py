from rest_framework import serializers

from src.common.abstract_serializer import NameSerializer
from src.course.models import Category


class RecursiveSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CategorySerializer(NameSerializer):
    children = RecursiveSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = (
            'uuid',
            'name',
            'parent',
            'children'
        )
