from django.urls import path

from .views import UserEdit, UserView


urlpatterns = [
    path('<id>/', UserView.as_view(), name='user_view'),
    path('<id>/edit/', UserEdit.as_view(), name='user_edit'),
]
