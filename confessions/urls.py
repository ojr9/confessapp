from django.urls import path

from .views import NewDeed, ViewDeed, react, UpdateDeed, ListDeed, ListDeedPersonal, ListCategories, Reflection,\
    UpdateReflection, comment


urlpatterns = [
    path('new/', NewDeed.as_view(), name='new_deed'),
    path('mylist/', ListDeedPersonal.as_view(), name='mylist_deed'),
    path('categories/', ListCategories.as_view(), name='list_categories'),
    path('<id>/', ViewDeed.as_view(), name='view_deed'),
    path('<id>/update/', UpdateDeed.as_view(), name='update_deed'),
    path('<id>/<reaction>/', react, name='react'),
    path('<id>/reflect/', Reflection.as_view(), name='new_reflection'),
    path('<id>/reflection/update/', UpdateReflection.as_view(), name='update_reflection'),
    path('<id>/comment/', comment, name='comment'),
    path('', ListDeed.as_view(), name='list_deed'),
]

