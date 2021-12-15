from rest_framework import serializers


class GreetingRequest:
    def __init__(self, name):
        self.name = name


class GreetingRequestSerializer(serializers.Serializer):
    name = serializers.CharField()

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        return instance

    def create(self, validated_data):
        return GreetingRequest(**validated_data)


class GreetingResponse:
    def __init__(self, name):
        self.greeting = f'hello {name}'


class GreetingResponseSerializer(serializers.Serializer):
    greeting = serializers.CharField()
