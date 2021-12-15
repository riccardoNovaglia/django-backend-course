from django.http import JsonResponse
from rest_framework.parsers import JSONParser

from cats.serializers import (
    GreetingRequestSerializer,
    GreetingResponse,
    GreetingResponseSerializer,
)


def cats(request):
    return JsonResponse({"message": "meow"})


def greet(request):
    data = JSONParser().parse(request)
    serializer = GreetingRequestSerializer(data=data)
    if serializer.is_valid():
        greeting = serializer.save()
        name = greeting.name
        response = GreetingResponse(name)
        response_serializer = GreetingResponseSerializer(response)
        return JsonResponse(response_serializer.data)

    return JsonResponse({"errors": serializer.errors}, status=400)
