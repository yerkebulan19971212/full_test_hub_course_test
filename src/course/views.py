from rest_framework import generics, status
from rest_framework.response import Response

from src.common.super_admin_views import QuestionAnswerImageSerializer


class SaveImageView(generics.CreateAPIView):
    serializer_class = QuestionAnswerImageSerializer

    def post(self, request, *args, **kwargs):
        data = self.create(request, *args, **kwargs).data
        filename = request.data['upload'].name
        return Response(
            data={
                "filename": filename,
                "upload": 1,
                "url": data.get('upload')
            },
            status=status.HTTP_200_OK
        )


save_image_view = SaveImageView.as_view()
