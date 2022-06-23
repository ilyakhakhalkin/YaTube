from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .models import Follow, Group, Post, User
from .forms import PostForm, CommentForm
from .paginator_custom import paginator_custom


def index(request):
    template = 'posts/index.html'

    post_list = Post.objects.select_related('author', 'group')
    page_obj = paginator_custom(request, post_list)

    context = {
        'page_obj': page_obj,
    }

    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'

    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.select_related('author').filter(group=group)
    page_obj = paginator_custom(request, post_list)

    context = {
        'group': group,
        'page_obj': page_obj,
    }

    return render(request, template, context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group').filter(author=author)
    page_obj = paginator_custom(request, post_list)

    following = (
        request.user.is_authenticated
        and Follow.objects.filter(
            author=author,
            user=request.user
        ).exists
    )

    context = {
        'page_obj': page_obj,
        'author': author,
        'following': following
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'form': form,
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )

    if not request.user == post.author:
        return redirect('posts:post_detail', post_id)

    if form.is_valid():
        post = form.save()
        return redirect('posts:post_detail', post_id)

    context = {
        'is_edit': True,
        'form': form,
        'post_id': post_id,
    }
    return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = Post.objects.get(pk=post_id)

    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()

    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Публикации избранных авторов"""

    posts = Post.objects.filter(author__following__user=request.user)

    if len(posts) == 0:
        empty_page = paginator_custom(request, [])
        context = {
            'page_obj': empty_page,
        }
    else:
        page_obj = paginator_custom(request, posts)
        context = {
            'page_obj': page_obj,
        }

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    """Подписаться на автора"""

    author = get_object_or_404(User, username=username)

    if request.user == author:
        return redirect('/follow/')

    Follow.objects.get_or_create(
        author=author,
        user=request.user,
    )

    return redirect('/follow/')


@login_required
def profile_unfollow(request, username):
    """Дизлайк, отписка"""

    author = get_object_or_404(User, username=username)
    Follow.objects.filter(author=author, user=request.user).delete()

    return render(request, 'posts/follow.html')
