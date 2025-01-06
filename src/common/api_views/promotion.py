import datetime

from rest_framework import generics, permissions, status
from rest_framework.response import Response

from src.accounts.models import User
from src.common.constant import PromoCodeType
from src.common.exception import PromoCodeDoesNotExistError, UserNotExistError
from src.common.models import PromoCode
from src.common.models.promotion import TelegramPromoCode
from src.common.serializers import PromoCodeSerializer
from src.common.serializers.common import TelegramPromoCodeSerializer


class PromoCodeView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PromoCodeSerializer

    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)
        return Response({'message': 'Success'}, status=status.HTTP_200_OK)


promo_code_view = PromoCodeView.as_view()


class GetTelegramPromoCodeView(generics.RetrieveAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    serializer_class = TelegramPromoCodeSerializer

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        now = datetime.datetime.now()
        promo_codes = PromoCode.objects.filter(
            start_date__lte=now.date(),
            end_date__gte=now.date(),
            promo_type=PromoCodeType.TELEGRAM,
            is_active=True,
        ).exclude(telegram_promo_code__telegram_user_id=user_id)
        if not promo_codes.exists():
            raise PromoCodeDoesNotExistError()
        promo_code = promo_codes.first()
        TelegramPromoCode.objects.create(
            promo_code=promo_code,
            telegram_user_id=user_id
        )
        return promo_code


get_telegram_promo_code_view = GetTelegramPromoCodeView.as_view()
