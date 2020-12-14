from django.urls import path,include
from .views import *
from rest_framework import routers




router = routers.DefaultRouter()
router.register('histories',AccountHistoryViewSet,basename='histories')
router.register('pocketmoney',PocketMoneyViewSet,basename='pocketmoney')
router.register('credits',CreditViewSet,basename='credits')
router.register('childs',ChildViewSet,basename='childs')
router.register('parents',ParentViewSet,basename='parents')

urlpatterns = [
    path('api/',include(router.urls)),
    path('api/login/', LoginAPIView.as_view()),
    path('api/logout/', LogoutAPIView.as_view()),
    path('api/register/', RegisterAPIView.as_view()),
    path('api/change-password/', ChangePasswordAPIView.as_view()),
]

