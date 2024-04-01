from rest_framework.response import Response
from rest_framework.views import APIView

class Health(APIView):
    """
    API for checking the app health
    """

    def get(self, request):
        return Response({
            'message': '😊'
        })