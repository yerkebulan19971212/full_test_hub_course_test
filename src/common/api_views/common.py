import requests
from django.db import transaction
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.views import APIView

from src.common.models import QuizzType, CourseTypeQuizz, Packet
from src.common import filters, serializers


class GetAllActiveQuizzTypes(generics.ListAPIView):
    queryset = CourseTypeQuizz.objects.get_all_active()
    serializer_class = serializers.QuizzTypeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.QuizzTypeFilter


quizz_types_view = GetAllActiveQuizzTypes.as_view()


class PacketListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Packet.objects.all()
    serializer_class = serializers.PacketSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.PacketFilter


packet_view = PacketListView.as_view()


class BuyPacket(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.BuyPacketSerializer

    def post(self, request, *args, **kwargs):
        packet = self.request.data['packet']
        packet_obj = Packet.objects.filter(pk=packet).first()

        user = self.request.user
        if user.balance < packet_obj.price:
            return Response({"detail": "недостаточно баланс"},
                            status=status.HTTP_400_BAD_REQUEST)
        return self.create(request, *args, **kwargs)


buy_packet_view = BuyPacket.as_view()
