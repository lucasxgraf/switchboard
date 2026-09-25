from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.keys.authentication import ApiKeyAuthentication


class ChatCompletionsView(APIView):
    authentication_classes = [ApiKeyAuthentication]

    def post(self, request: Request) -> Response:
        return Response()
