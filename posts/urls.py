from django.urls import path
from posts.views import post_comment_create_and_list_view, like_unlike_post, PostDeleteView, PostUpdateView


urlpatterns = [
    path("", post_comment_create_and_list_view, name="main-post-view"),
    path("like/", like_unlike_post, name="like-post-view"),
    path("<pk>/delete/", PostDeleteView.as_view(), name="post_delete"),
    path("<pk>/update/", PostUpdateView.as_view(), name="post_update"),
]