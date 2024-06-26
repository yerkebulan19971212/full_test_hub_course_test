from rest_framework import serializers

from src.accounts.models import User
from src.common.abstract_serializer import NameSerializer
from src.common.models import Blog, BlogCategory


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name',
            'avatar',
            'last_name'
        )


class CategorySerializer(NameSerializer):
    class Meta:
        model = BlogCategory
        fields = (
            'name',
        )
        ref_name = 'CategorySerializer'


class BlogSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = [
            'uuid',
            'title',
            'name_code',
            'image',
            'duration_length',
            'views',
            'created',
            'author',
            'category',
        ]
        ref_name = 'BlogSerializer'

    def get_category(self, obj):
        return CategorySerializer(obj.category, context=self.context).data['name']


class BlogOneSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    category = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = [
            'uuid',
            'title',
            'image',
            'name_code',
            'duration_length',
            'views',
            'created',
            'author',
            'category',
            'description',
            'author',
            'category',
        ]
        ref_name = 'BlogOneSerializer'

    def get_category(self, obj):
        return CategorySerializer(obj.category, context=self.context).data['name']
