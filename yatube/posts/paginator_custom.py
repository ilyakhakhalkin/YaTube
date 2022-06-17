from django.core.paginator import Paginator
from django.conf import settings


def paginator_custom(request, post_list):
    paginator = Paginator(post_list, settings.POSTS_AMOUNT)
    page_num = request.GET.get('page')

    return paginator.get_page(page_num)
