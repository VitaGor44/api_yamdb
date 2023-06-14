from rest_framework import filters, mixins, viewsets

from .permissions import IsAdminOnly, IsAnonymous


class CreateListDestroyMixinSet(mixins.CreateModelMixin,
                                mixins.ListModelMixin,
                                mixins.DestroyModelMixin,
                                viewsets.GenericViewSet):
    permission_classes = [IsAnonymous | IsAdminOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    lookup_field = 'slug'
