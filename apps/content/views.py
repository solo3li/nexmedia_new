from django.shortcuts import render, get_object_or_404
from apps.content.models import BlogPost, CustomPage

def blog_list_view(request):
    posts = BlogPost.objects.filter(is_published=True).order_by('-created_at')
    return render(request, 'content/blog_list.html', {'posts': posts})

def blog_detail_view(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, is_published=True)
    return render(request, 'content/blog_detail.html', {'post': post})

def custom_page_view(request, slug):
    page = get_object_or_404(CustomPage, slug=slug, is_published=True)
    return render(request, 'content/custom_page.html', {'page': page})
