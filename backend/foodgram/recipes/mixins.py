from rest_framework import mixins, viewsets


class ListRetrieveModelViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        viewsets.GenericViewSet):
    pass
