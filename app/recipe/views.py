from rest_framework import authentication, permissions, viewsets, mixins

from core.models import Tag, Ingredient
from recipe.serializers import TagSerializer, IngredientSerializer


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
