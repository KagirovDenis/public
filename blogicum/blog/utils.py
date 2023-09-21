from django.db.models import Count
from django.utils import timezone

from blog.models import Post


def getting_a_list_of_posts():
    return Post.objects.select_related(
        'category',
        'location',
        'author',
    ).filter(
        is_published=True,
        category__is_published=True,
        pub_date__lte=timezone.now()
    ).order_by('-created_at').annotate(
        comment_count=Count('comments')
        )
