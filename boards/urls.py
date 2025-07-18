from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('boards/<int:board_id>/', views.board_topics, name='board_topics'),
    path('boards/<int:board_id>/new/', views.new_topic, name='new_topic'),
    path('boards/<int:board_id>/topics/<int:topic_id>/', views.topic_posts, name='topic_posts'),
    path('boards/<int:board_id>/topics/<int:topic_id>/reply/', views.reply_topic, name='reply_topic'),
    path('posts/<int:post_id>/edit/', views.edit_post, name='edit_post'),
]

