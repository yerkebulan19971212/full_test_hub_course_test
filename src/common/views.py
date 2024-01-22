from django.shortcuts import render
from rest_framework import generics, permissions

from src.common.serializers.common import SupportSerializer


# Create your views here.
class SupportView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SupportSerializer


support_view = SupportView.as_view()