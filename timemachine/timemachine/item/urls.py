from rest_framework.routers import SimpleRouter
from . import views

router = SimpleRouter()


router.register('item', views.ItemView)

urlpatterns = router.urls