from rest_framework import authentication, mixins, permissions, viewsets

from core.models import Ingredient, Recipe, Tag
from recipe.serializers import (
    IngredientSerializer,
    RecipeDetailSerializer,
    RecipeSerializer,
    TagSerializer,
)


class AuthenticatedListCreateView(viewsets.GenericViewSet,
                                  mixins.ListModelMixin,
                                  mixins.CreateModelMixin):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagView(AuthenticatedListCreateView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientView(AuthenticatedListCreateView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeView(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('-title')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RecipeDetailSerializer

        return RecipeSerializer
