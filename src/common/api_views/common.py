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


quizz_types_view = GetAllActiveQuizzTypes.as_view()


class PacketListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Packet.objects.filter(is_active=True)
    serializer_class = serializers.PacketSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.PacketFilter

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset=queryset)
        if queryset.first().quizz_type.quizz_type.name_code == 'full_test':
            rating_period = RatingTest.objects.all().order_by('id').last()
            p = Packet.objects.filter(
                name_code='rating',
                bought_packets__rating_test=rating_period,
                bought_packets__user=self.request.user,
                bought_packets__status=True,
                is_active=True,
            )
            return queryset.union(p).order_by('order')
        return queryset.order_by('order')


packet_view = PacketListView.as_view()


class PacketListView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Packet.objects.all()
    serializer_class = serializers.PacketSerializer
    lookup_field = 'uuid'


packet_one_view = PacketListView.as_view()


class BuyPacket(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = serializers.BuyPacketSerializer

    def post(self, request, *args, **kwargs):
        packet = self.request.data['packet']
        packet_obj = Packet.objects.filter(pk=packet).first()

        user = self.request.user
        price = packet_obj.second_price if packet_obj.second_price is not None else packet_obj.price
        if user.balance < price:
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
