from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Group
from .forms import PostForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model

User = get_user_model()


def index(request):
    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:12]
    paginator = Paginator(posts, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request,
                  "group.html",
                  {
                      "group": group,
                      "posts": posts,
                      "page": page,
                      'paginator': paginator,
                  }
                  )


@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("index")
        return render(request, "new_post.html", {"form": form})
    form = PostForm()
    return render(request, "new_post.html", {"form": form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = Post.objects.order_by('-pub_date').filter(author=author)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(request,
                  'profile.html',
                  {
                      'author': author,
                      'page': page,
                      'paginator': paginator,
                      'post_list': post_list,
                  }
                  )


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=author)
    post_list = Post.objects.order_by('-pub_date').filter(author=author)
    return render(request,
                  'post.html',
                  {
                      'author': author,
                      'post': post,
                      'post_list': post_list,
                  }
                  )

@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(Post, id=post_id, author=author)
    if request.user == author:
        if request.method == 'POST':
            form = PostForm(request.POST or None, instance=post)
            if form.is_valid():
                form.save()
                return redirect('post', username=username, post_id=post_id)
            return render(request,
                          'new_post.html',
                          {
                              'post': post,
                              'update': True,
                              'form': PostForm(instance=post),
                              'author': author,
                          }
                          )
    return render(request,
                  'new_post.html',
                  {
                      'post': post,
                      'update': True,
                      'form': PostForm(instance=post),
                      'author': author,
                  }
                  )
