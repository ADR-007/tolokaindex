from django.apps import AppConfig


class PostsConfig(AppConfig):
    name = 'tolokaindex.apps.posts'

    def ready(self):
        import tolokaindex.apps.posts.signals
