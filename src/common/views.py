from django.shortcuts import render
from rest_framework import generics, permissions, serializers
from rest_framework.response import Response
from rest_framework.views import APIView

from src.common.models import Blog, blog, KaspiPay
from src.common.serializers.blog import BlogSerializer, BlogOneSerializer
from src.common.serializers.common import SupportSerializer
from src.services.gmail import add_balance


# Create your views here.
class SupportView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SupportSerializer


support_view = SupportView.as_view()


class BlocList(APIView):
    def get(self, request, format=None):
        from src.common.models import Blog
        blocks = Blog.objects.all()
        blocks_serializer = BlogSerializer(blocks, many=True, context={'request': request})
        return Response(blocks_serializer.data)


#
class BlogOne(APIView):
    def get(self, request, id, format=None):
        blog_one = Blog.objects.filter(id=id).first()
        blog_one.views += 1
        blog_one.save()
        block_one_serializer = BlogOneSerializer(blog_one, context={'request': request})
        return Response(block_one_serializer.data)


class BlogRecomendationList(APIView):
    def get(self, request, id, format=None):
        blocks = Blog.objects.exclude(id=id).order_by('?')[:3]
        blocks_serializer = BlogSerializer(blocks, many=True, context={'request': request})
        return Response(blocks_serializer.data)


class TestView(APIView):

    def get(self, request, format=None):
        add_balance()
        return Response({'status': 'ok'})


test_view = TestView.as_view()
