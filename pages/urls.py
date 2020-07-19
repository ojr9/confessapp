from django.urls import path
from .views import Index, Todoes, BizCase, ToDo2


urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('todo/', Todoes.as_view(), name='todoes'),
    path('bizcase/', BizCase.as_view(), name='bizcase'),
    path('td2/', ToDo2.as_view(), name='td2'),
]
