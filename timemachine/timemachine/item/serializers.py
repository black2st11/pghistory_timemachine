from rest_framework import serializers
from django.db.models import OuterRef, Subquery, F
from pghistory.models import Context
from rest_framework.serializers import ValidationError
from rest_framework import status
from .models import Item, ItemEvent

class ItemSerializer(serializers.ModelSerializer):
    phone = serializers.SerializerMethodField()

    class Meta:
        model = Item
        fields = '__all__'

    def get_phone(self, obj):
        return obj.phone.as_national

class ItemRollbackSerializer(serializers.Serializer):
    rollback_time = serializers.DateTimeField(write_only=True)
    item = ItemSerializer(read_only=True)
    
    def save(self, **kwargs):
        rollback_time = self.validated_data['rollback_time']
        rollback_item = ItemEvent.objects.filter(pgh_created_at__lte=rollback_time).order_by('-pgh_created_at').first()
        for field in Item._meta.fields:
            setattr(self.instance, field.attname, getattr(rollback_item, field.attname))
        self.instance.save()

        self.instance = {'item': self.instance}

class PartialRollbackSerializer(serializers.Serializer):
    rollback_time = serializers.DateTimeField(write_only=True)
    fields = serializers.ListField(write_only=True)
    item = ItemSerializer(read_only=True)

    def validate_fields(self, values):
        for value in values:
            if value not in [field.attname for field in Item._meta.fields]:
                raise ValidationError('invalide fields', code=status.HTTP_400_BAD_REQUEST)
        return values

    def save(self, **kwargs):
        rollback_time = self.validated_data['rollback_time']
        rollback_item = ItemEvent.objects.filter(pgh_created_at__lte=rollback_time).order_by('-pgh_created_at').first()
        for field in self.validated_data['fields']:
            setattr(self.instance, field, getattr(rollback_item, field))
        self.instance.save()

        self.instance = {'item': self.instance}

class BulKPartialRollbackSerializer(serializers.Serializer):
    context = serializers.UUIDField(write_only=True)
    fields = serializers.ListField(write_only=True)
    items = ItemSerializer(read_only=True, many=True)

    def validate_context(self, value):
        try:
            context = Context.objects.get(id=value)
            return context
        except Context.DoesNotExist:
            raise ValidationError('invalide context', code=status.HTTP_400_BAD_REQUEST)

    def validate_fields(self, values):
        for value in values:
            if value not in [field.attname for field in Item._meta.fields]:
                raise ValidationError('invalide fields', code=status.HTTP_400_BAD_REQUEST)
        return values

    def save(self, **kwargs):
        item_events = ItemEvent.objects.filter(pgh_created_at__lt=self.validated_data['context'].created_at)
        items = Item.objects.filter(id__in=[event.id for event in item_events])
        item_events = item_events.filter(id=OuterRef('id'))

        annotate_kwargs = {}
        update_kwargs = {}

        for field in self.validated_data['fields']:
            annotate_kwargs.update({
                f'last_{field}': Subquery(item_events.values(field)[:1])
            })

            update_kwargs.update({
                field: F(f'last_{field}')
            })

        items.annotate(**annotate_kwargs).update(**update_kwargs)

        self.instance = {'items' : items}


