from rest_framework import serializers

from src.accounts.models import User
from src.common.models import Blog, BlogCategory


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = (
            'name_ru',
            'name_kz',
            'name_en'
        )


class BlogSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Blog
        fields = [
            'id',
            'title',
            'name_code',
            'image',
            'duration_length',
            'views',
            'created',
            'author',
            'category',
        ]

class BlogOneSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Blog
        fields = [
            'id',
            'title',
            'image',
            'name_code',
            'duration_length',
            'views',
            'created',
            'author',
            'category',
            'description'
        ]