from django.contrib import admin
from .models import Category, Deed, Collection, Comment
from django.utils.text import slugify


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'category_name','slug', 'count']
    # autocomplete_fields = slugify('slug')


@admin.register(Deed)
class DeedAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'category', 'nature', 'registered', 'intensity', 'likes', 'applauses',
                    'mehs', 'laughs', 'cries']


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['deed', 'price', 'update']


@admin.register(Comment)
class ReflectionAdmin(admin.ModelAdmin):
    list_display = ['user', 'deed']
