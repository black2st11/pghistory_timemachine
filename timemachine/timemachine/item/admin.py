from django.contrib import admin
from .models import Item, ItemEvent
from pghistory.models import Context

# Register your models here.

admin.site.register(Item)
admin.site.register(ItemEvent)
admin.site.register(Context)