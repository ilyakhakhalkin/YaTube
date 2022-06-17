from django.shortcuts import get_object_or_404, render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Comment, Follow, Group, Post, User
from .forms import PostForm, CommentForm
from .paginator_custom import paginator_custom


@cache_page(20, key_prefix="index_page")
def index(request):
    template = 'posts/index.html'

    post_list = Post.objects.all()
    page_obj = paginator_custom(request, post_list)

    context = {
        'page_obj': page_obj,
    }

    return render(request, template, context)


def group_posts(request, slug):
    template = 'posts/group_list.html'

    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.all()
    page_obj = paginator_custom(request, post_list)

    context = {
        'group': group,
        'page_obj': page_obj,
    }

    return render(request, template, context)


def profile(request, username):
    current_user = get_object_or_404(User, username=username)
    post_list = current_user.posts.all()
    page_obj = paginator_custom(request, post_list)

    context = {
        'page_obj': page_obj,
        'author': current_user,
    }

    if not request.user.is_anonymous:
        try:
            following = Follow.objects.get(author=current_user, user=request.user)
        except Follow.DoesNotExist:
            following = False

        context['following'] = following

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = Comment.objects.filter(post=post)
    # following = Follow.objects.get(author=post_id.author, user=request.user)

    form = CommentForm()

    context = {
        'post': post,
        'comments': comments,
        'form': form,
        # 'following': following
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

    subscriptions = Follow.objects.filter(user=request.user)
    authors = []
    for sub in subscriptions:
        authors.append(sub.author)

    posts = Post.objects.filter(author__in=authors)
    if len(posts) == 0:
        empty_page = paginator_custom(request, [])
        context = {
            'NO_SUBSCRIPTIONS': True,
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
        return follow_index(request)

    if not Follow.objects.filter(author=author, user=request.user).exists():
        subscription = Follow(author=author, user=request.user)
        subscription.save()

    return follow_index(request)


@login_required
def profile_unfollow(request, username):
    """Дизлайк, отписка"""

    author = get_object_or_404(User, username=username)
    try:
        Follow.objects.get(author=author, user=request.user).delete()
        return follow_index(request)

    except Follow.DoesNotExist:
        context = {
            'NO_SUBSCRIPTIONS': True,
        }
        return render(request, 'posts/follow.html', context)
