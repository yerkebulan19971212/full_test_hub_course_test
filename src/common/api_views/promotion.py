from rest_framework import generics, permissions, status
from rest_framework.response import Response

from src.common.serializers import PromoCodeSerializer


class PromoCodeView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PromoCodeSerializer

    def post(self, request, *args, **kwargs):
        self.create(request, *args, **kwargs)
        return Response({'message': 'Success'}, status=status.HTTP_200_OK)


promo_code_view = PromoCodeView.as_view()
