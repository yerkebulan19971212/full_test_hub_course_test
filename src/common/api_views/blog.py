from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework import generics
from rest_framework.response import Response

from src.common.models import Blog
from src.common.serializers.blog import BlogSerializer, BlogOneSerializer


class BlocListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BlogSerializer
    queryset = Blog.objects.filter(is_active=True)

    @swagger_auto_schema(tags=["blog"])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


blog_list_view = BlocListView.as_view()


class BlocDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BlogOneSerializer
    queryset = Blog.objects.filter(is_active=True)
    lookup_field = 'uuid'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        uuid = self.kwargs['uuid']
        blog = Blog.objects.get(uuid=uuid)
        blog.views += 1
        blog.save()
        return Response(serializer.data)

    @swagger_auto_schema(tags=["blog"])
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


blog_detail_view = BlocDetailView.as_view()


class BlocRecommendationView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BlogSerializer
    queryset = Blog.objects.filter(is_active=True)

    def get_queryset(self):
        uuid = self.kwargs['uuid']
        blog = Blog.objects.get(uuid=uuid)
        return super().get_queryset().exclude(id=blog.id).order_by('?')[:3]

    @swagger_auto_schema(tags=["blog"])
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


blog_recommendation_view = BlocRecommendationView.as_view()
