from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from simpleauth.serializers import SimpleLoginSerializer, simple_token_response_for_user


class SimpleLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SimpleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        return Response(simple_token_response_for_user(user), status=status.HTTP_200_OK)
