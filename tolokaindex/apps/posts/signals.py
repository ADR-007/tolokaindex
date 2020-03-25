from django.db.models.signals import post_save
from django.dispatch import receiver

from tolokaindex.apps.posts.models import Post
from tolokaindex.apps.raw_posts.models import RawPost


@receiver(post_save, sender=RawPost, dispatch_uid="update_post_on_raw_post_update")
def update_post(instance: RawPost, **_):
    try:
        Post.update_from_raw(instance)
    except:
        print(f'Wrong: {instance.title}')
