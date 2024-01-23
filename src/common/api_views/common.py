from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend

from src.common.exception import NotEnoughBalance
from src.common.models import CourseTypeQuizz, Packet, City, School, RatingTest
from src.common import filters, serializers


class GetAllActiveQuizzTypes(generics.ListAPIView):
    queryset = CourseTypeQuizz.objects.get_all_active_without_rating()
    serializer_class = serializers.QuizzTypeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.QuizzTypeFilter

    def get(self, request, *args, **kwargs):
        cache_key = f'quizze_type{self.request.build_absolute_uri()}'
        cached_data = cache.get(cache_key)

        if cached_data is not None:
            return Response(cached_data)
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=3600)  # Cache for 60 seconds
        return response


quizz_types_view = GetAllActiveQuizzTypes.as_view()


class PacketListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Packet.objects.all()
    serializer_class = serializers.PacketSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.PacketFilter

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset=queryset)
        if queryset.first().quizz_type.quizz_type.name_code == 'full_test':
            p = Packet.objects.filter(
                name_code='rating',
                bought_packets__user=self.request.user,
                bought_packets__status=True,
            )
            return queryset.union(p)
        return queryset


packet_view = PacketListView.as_view()


class BuyPacket(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.BuyPacketSerializer

    def post(self, request, *args, **kwargs):
        packet = self.request.data['packet']
        packet_obj = Packet.objects.filter(pk=packet).first()

        user = self.request.user
        if user.balance < packet_obj.price:
            raise NotEnoughBalance()
        return self.create(request, *args, **kwargs)


buy_packet_view = BuyPacket.as_view()


class GetAllCitiesView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = City.objects.all()
    serializer_class = serializers.CitySerializer


get_all_cities_view = GetAllCitiesView.as_view()


class GetAllSchoolView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = School.objects.all()
    serializer_class = serializers.SchoolSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.SchoolFilter


get_all_school_view = GetAllSchoolView.as_view()


class GetAllRatingTestView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = RatingTest.objects.all().order_by('-id')
    serializer_class = serializers.RatingTestSerializer


get_all_rating_test_view = GetAllRatingTestView.as_view()
