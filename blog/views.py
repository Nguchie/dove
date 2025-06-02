from django.shortcuts import render, get_object_or_404
from .models import Post

def blog_list(request):
    posts = Post.objects.filter(published=True).order_by('-created_at')
    return render(request, 'blog/blog_list.html', {
        'posts': posts,
    })


def blog_detail(request, pk):
    post = get_object_or_404(Post, pk=pk, published=True)
    sections = post.sections.all().order_by('id')  # Order sections in defined sequence
    return render(request, 'blog/detail.html', {
        'post': post,
        'sections': sections
    })
