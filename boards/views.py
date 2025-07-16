#from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from .models import Board, Topic, Post
from django.contrib.auth.decorators import login_required
from .forms import NewTopicForm, PostForm
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseForbidden

def home(request):
    boards = Board.objects.all()
    return render(request, 'boards/home.html', {'boards': boards})

def board_topics(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    topics = board.topics.all().order_by('-created_at')
    return render(request, 'boards/topics.html', {'board': board, 'topics': topics})

@login_required
def new_topic(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()
            
            Post.objects.create(
                message=form.cleaned_data['message'],
                topic=topic,
                created_by=request.user
            )

            #print("✅ POST CREATED:", form.cleaned_data.get("message"))

            return redirect('board_topics', board_id=board.pk)
    else:
        form = NewTopicForm()
    return render(request, 'boards/new_topic.html', {'board': board, 'form': form})

def topic_posts(request, board_id, topic_id):
    topic = get_object_or_404(Topic, board__pk=board_id, pk=topic_id)

    topic.views += 1
    topic.save()

    all_posts = topic.posts.order_by('created_at')
    unique_posts = []
    seen_users = set()

    for post in all_posts:
        if post.created_by_id not in seen_users:
            unique_posts.append(post)
            seen_users.add(post.created_by_id)

    return render(request, 'boards/topic_posts.html', {
        'topic': topic,
        'posts': unique_posts
    })

@login_required
def reply_topic(request, board_id, topic_id):
    topic = get_object_or_404(Topic, board__pk=board_id, pk=topic_id)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()
            return redirect('topic_posts', board_id=board_id, topic_id=topic.pk)
    else:
        form = PostForm()

    posts = topic.posts.order_by('-created_at')  
    return render(request, 'boards/reply_topic.html', {
        'topic': topic,
        'form': form,
        'posts': posts  
    })

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if post.created_by != request.user:
        return HttpResponseForbidden("You are not allowed to edit this post.")

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('topic_posts', board_id=post.topic.board.pk, topic_id=post.topic.pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'boards/edit_post.html', {'post': post, 'form': form})

