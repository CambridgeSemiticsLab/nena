from django.conf.urls import url, include
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'dialects', views.DialectViewSet)
router.register(r'grammar', views.GrammarFeatureViewSet)

app_name = 'api'

urlpatterns = [
    url(r'^', include(router.urls)),
]
