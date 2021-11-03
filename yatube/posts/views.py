from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post

User = get_user_model()

SHOW_POSTS = 10


def index(request):
    template = 'posts/index.html'
    posts_all = Post.objects.all()

    paginator = Paginator(posts_all, SHOW_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj
    }
    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'
    group = get_object_or_404(Group, slug=slug)
    posts_all = group.posts.all()

    paginator = Paginator(posts_all, SHOW_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts_all = author.posts.all()
    posts_count = author.posts.count()

    paginator = Paginator(posts_all, SHOW_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'author': author,
        'posts_count': posts_count,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, pk=post_id)
    posts_count = post.author.posts.count()

    context = {
        'post': post,
        'posts_count': posts_count,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)

    if request.method == 'POST':

        if form.is_valid():
            post_temp = form.save(commit=False)
            post_temp.author = request.user
            post_temp.save()
            return redirect('posts:profile', username=request.user.username)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        return redirect('/posts/' + str(post_id))

    form = PostForm(request.POST or None, instance=post)

    if request.method == 'POST':

        if form.is_valid():
            form.save()
            return redirect('/posts/' + str(post_id))

    return render(request, 'posts/create_post.html', {
        'form': form,
        'post_id': post_id,
    })
