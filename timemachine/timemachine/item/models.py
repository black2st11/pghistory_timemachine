from django.db import models
import pghistory
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import QuerySet
# Create your models here.


@pghistory.track(
    pghistory.Snapshot('item.snapshot')
)
class Item(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=50)
    detail_address = models.CharField(max_length=50)
    phone = PhoneNumberField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    

class ItemEvent(pghistory.get_event_model(
    Item,
    pghistory.Snapshot('item.snaphot')
)):
    objects = QuerySet.as_manager()