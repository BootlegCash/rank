# accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import RegistrationForm, StatsUpdateForm, SendFriendRequestForm
from .models import Profile, FriendRequest

# Registration view
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user


            # Create a profile for the user
            Profile.objects.create(user=user)

            messages.success(request, f'Account created for {user.username}!')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to the URL specified in the 'next' parameter
            next_url = request.GET.get('next', 'welcome')  # Default to 'welcome' if 'next' is not provided
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/login.html')

# Logout view
def logout_view(request):
    logout(request)
    return redirect('login')

# Welcome view
@login_required
def welcome(request):
    return render(request, 'accounts/welcome.html', {'username': request.user.username})

# Profile view
@login_required
def profile(request):
    # Get the user's profile
    user_profile = Profile.objects.get(user=request.user)
    return render(request, 'accounts/profile.html', {'profile': user_profile})

@login_required
def update_stats(request):
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':
        form = StatsUpdateForm(request.POST)
        if form.is_valid():
            # Add the new values to the existing ones
            user_profile.beer += form.cleaned_data['beer']
            user_profile.floco += form.cleaned_data['floco']
            user_profile.rum += form.cleaned_data['rum']
            user_profile.whiskey += form.cleaned_data['whiskey']
            user_profile.vodka += form.cleaned_data['vodka']
            user_profile.tequila += form.cleaned_data['tequila']
            user_profile.shotguns += form.cleaned_data['shotguns']
            user_profile.snorkels += form.cleaned_data['snorkels']
            user_profile.thrown_up += form.cleaned_data['thrown_up']

            # Save the updated profile
            user_profile.save()

            messages.success(request, 'Your stats have been updated!')
            return redirect('profile')
    else:
        # Pre-fill the form with the current values (optional)
        form = StatsUpdateForm(initial={
            'beer': 0,
            'floco': 0,
            'rum': 0,
            'whiskey': 0,
            'vodka': 0,
            'tequila': 0,
            'shotguns': 0,
            'snorkels': 0,
            'thrown_up': 0,
        })

    return render(request, 'accounts/update_stats.html', {'form': form})

# Send friend request view
@login_required
def send_friend_request(request):
    if request.method == 'POST':
        form = SendFriendRequestForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                to_user = User.objects.get(username=username)
                to_profile = Profile.objects.get(user=to_user)
                from_profile = Profile.objects.get(user=request.user)

                # Check if a friend request already exists
                if FriendRequest.objects.filter(from_user=from_profile, to_user=to_profile).exists():
                    messages.error(request, "Friend request already sent.")
                elif from_profile == to_profile:
                    messages.error(request, "You cannot send a friend request to yourself.")
                else:
                    FriendRequest.objects.create(from_user=from_profile, to_user=to_profile)
                    messages.success(request, f"Friend request sent to {username}!")
            except User.DoesNotExist:
                messages.error(request, "User not found.")
        return redirect('friend_list')
    else:
        form = SendFriendRequestForm()
    return render(request, 'accounts/send_friend_request.html', {'form': form})

# Accept friend request view
@login_required
def accept_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user.profile)
    
    # Mark the request as accepted
    friend_request.accepted = True
    friend_request.save()

    # Add each user to the other's friends list
    friend_request.from_user.friends.add(friend_request.to_user)
    friend_request.to_user.friends.add(friend_request.from_user)

    messages.success(request, f"You are now friends with {friend_request.from_user.user.username}!")
    return redirect('friend_list')

# Reject friend request view
@login_required
def reject_friend_request(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user.profile)
    friend_request.delete()
    messages.success(request, "Friend request rejected.")
    return redirect('friend_list')

# Friend list view
@login_required
def friend_list(request):
    profile = Profile.objects.get(user=request.user)
    friends = profile.friends.all()
    received_requests = FriendRequest.objects.filter(to_user=profile, accepted=False)
    sent_requests = FriendRequest.objects.filter(from_user=profile, accepted=False)

    return render(request, 'accounts/friend_list.html', {
        'friends': friends,
        'received_requests': received_requests,
        'sent_requests': sent_requests,
    })

# accounts/views.py
@login_required
def leaderboard(request):
    # Get the current user's profile
    user_profile = Profile.objects.get(user=request.user)
    
    # Get the user's friends
    friends = user_profile.friends.all()
    
    # Fetch profiles of friends, ordered by XP in descending order
    friend_profiles = Profile.objects.filter(user__profile__in=friends).order_by('-xp')
    
    return render(request, 'accounts/leaderboard.html', {'profiles': friend_profiles})