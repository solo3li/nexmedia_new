from django.contrib import admin
from apps.content.models import BlogPost, CustomPage

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title_ar', 'title_en', 'slug', 'category', 'is_published', 'created_at')
    list_filter = ('is_published', 'category')
    search_fields = ('title_en', 'title_ar', 'slug')
    prepopulated_fields = {'slug': ('title_en',)}

@admin.register(CustomPage)
class CustomPageAdmin(admin.ModelAdmin):
    list_display = ('slug', 'title_ar', 'title_en', 'is_published')
    search_fields = ('title_en', 'title_ar', 'slug')
