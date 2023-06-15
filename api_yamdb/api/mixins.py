from rest_framework import filters, mixins, viewsets

from .permissions import IsAdminOrReadOnly, IsAnonymous


class CreateListDestroyMixinSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
    permission_classes = [IsAnonymous | IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'
