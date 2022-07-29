from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from .models import Item
from .serializers import BulKPartialRollbackSerializer, ItemSerializer, ItemRollbackSerializer, PartialRollbackSerializer
# Create your views here.


class ItemView(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    serializer_classes = {
        'rollback': ItemRollbackSerializer,
        'partial_rollback': PartialRollbackSerializer,
        'bulk_rollback': BulKPartialRollbackSerializer
    }

    def get_serializer_class(self):
        if self.serializer_classes.get(self.action):
            return self.serializer_classes.get(self.action)
        return super().get_serializer_class()

    @action(detail=True, methods=['PUT'])
    def rollback(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @action(detail=True, methods=['PATCH'])
    def partial_rollback(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @action(detail=False, methods=['POST'])
    def bulk_rollback(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)