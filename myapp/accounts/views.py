from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import RegistrationForm, StatsUpdateForm, SendFriendRequestForm
from .models import Profile, FriendRequest
from .models import Post
from .forms import PostForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.forms import UserCreationForm
import random

def register(request):
    if request.user.is_authenticated:
        return redirect('welcome')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('welcome')
    else:
        form = UserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
        messages.error(request, 'Invalid credentials')
    return render(request, 'accounts/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('login')

@login_required
def profile(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'accounts/profile.html', {'profile': profile})

@login_required
def update_stats(request):
    profile = get_object_or_404(Profile, user=request.user)
    
    if request.method == 'POST':
        form = StatsUpdateForm(request.POST, instance=profile)
        if form.is_valid():
            # Calculate XP changes before saving
            new_profile = form.save(commit=False)
            new_profile.save()  # Triggers auto XP/rank calculation
            messages.success(request, 'Stats updated!')
            return redirect('profile')
    else:
        form = StatsUpdateForm(instance=profile)
        
    return render(request, 'accounts/update_stats.html', {'form': form})

@login_required
def leaderboard(request):
    profile = get_object_or_404(Profile, user=request.user)
    friends = profile.friends.all()
    friend_profiles = Profile.objects.filter(user__in=[f.user for f in friends]).order_by('-xp')
    return render(request, 'accounts/leaderboard.html', {
        'profiles': friend_profiles,
        'user_profile': profile
    })

@login_required
def friend_list(request):
    profile = get_object_or_404(Profile, user=request.user)
    received_requests = FriendRequest.objects.filter(to_user=profile, accepted=False)
    sent_requests = FriendRequest.objects.filter(from_user=profile, accepted=False)
    return render(request, 'accounts/friend_list.html', {
        'friends': profile.friends.all(),
        'received_requests': received_requests,
        'sent_requests': sent_requests
    })

@login_required
def send_friend_request(request):
    if request.method == 'POST':
        form = SendFriendRequestForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                to_user = User.objects.get(username=username).profile
                if to_user == request.user.profile:
                    messages.error(request, "You can't send a request to yourself")
                elif FriendRequest.objects.filter(from_user=request.user.profile, to_user=to_user).exists():
                    messages.error(request, "Friend request already sent")
                elif to_user in request.user.profile.friends.all():
                    messages.error(request, "You're already friends")
                else:
                    FriendRequest.objects.create(
                        from_user=request.user.profile,
                        to_user=to_user
                    )
                    messages.success(request, 'Friend request sent!')
            except User.DoesNotExist:
                messages.error(request, 'User not found')
            return redirect('friend_list')
    else:
        form = SendFriendRequestForm()
    return render(request, 'accounts/send_friend_request.html', {'form': form})

@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(
        FriendRequest,
        id=request_id,
        to_user=request.user.profile
    )
    try:
        friend_request.accept()
        messages.success(request, f"You're now friends with {friend_request.from_user.user.username}!")
    except Exception as e:
        messages.error(request, f"Error accepting request: {str(e)}")
    return redirect('friend_list')

@login_required
def reject_friend_request(request, request_id):
    friend_request = get_object_or_404(
        FriendRequest,
        id=request_id,
        to_user=request.user.profile
    )
    friend_request.delete()
    messages.success(request, "Friend request rejected")
    return redirect('friend_list')

@login_required
def wheel_of_dares(request):
    DARES = [
        "Take a waterfall shot!",
        "Do your best dance for 30 seconds",
        "Tell an embarrassing story",
        "Sing the chorus of your favorite song",
        "Arm wrestle the person to your left"
    ]
    if request.method == 'POST':
        dare = random.choice(DARES)
        profile = request.user.profile
        profile.xp += 25  # Bonus XP for completing dare
        profile.save()
        return render(request, 'accounts/wheel_result.html', {'dare': dare})
    return render(request, 'accounts/wheel_spin.html')

@login_required
def welcome(request):
    """Welcome page after login"""
    if not request.user.is_authenticated:
        return redirect('login')
        
    # Friend posts (users you follow)
    friend_posts = Post.objects.filter(
        user__in=request.user.profile.friends.all()
    ).order_by('-created_at')
    
    # User's own posts
    user_posts = Post.objects.filter(
        user=request.user.profile
    ).order_by('-created_at')
    
    # Combine and sort all relevant posts
    all_posts = (friend_posts | user_posts).distinct().order_by('-created_at')
    
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user.profile
            post.save()
            return redirect('welcome')
    else:
        form = PostForm()
    
    return render(request, 'accounts/welcome.html', {
        'posts': all_posts,
        'form': form
    })

@require_POST
@login_required
def like_post(request, post_id):
    from .models import Post
    post = Post.objects.get(id=post_id)
    profile = request.user.profile
    
    if profile in post.likes.all():
        post.likes.remove(profile)
        liked = False
    else:
        post.likes.add(profile)
        liked = True
    
    return JsonResponse({
        'liked': liked,
        'like_count': post.likes.count()
    })

class CreatePostView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'accounts/compose_post.html'
    success_url = reverse_lazy('welcome')

    def form_valid(self, form):
        form.instance.user = self.request.user.profile
        return super().form_valid(form)
    
