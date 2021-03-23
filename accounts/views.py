from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import get_user_model  # Model 대신
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm  # 로그인 폼, 비번바꾸기 폼
from django.contrib.auth.decorators import login_required  # 로그인 데코레이터
from .forms import CustomUserChangeForm, CustomUserCreationForm  # forms.py 들고오기
from django.views.decorators.http import require_safe, require_POST, require_http_methods
from django.contrib.auth import update_session_auth_hash  # 비밀번호 변경 후 로그인 유지

User = get_user_model()
def index(request):
    users = User.objects.order_by('pk')
    context = { 'users': users }
    return render(request, 'accounts/index.html', context)


@require_http_methods(['GET', 'POST'])
def signup(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('accounts:login')

    else:
        form = CustomUserCreationForm()
    context = { 'form': form }
    return render(request, 'accounts/signup.html', context)


def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            return redirect('accounts:profile')
    else:
        form = AuthenticationForm()
    context = { 'form': form }
    return render(request, 'accounts/login.html', context)

# 로그인 안되어있으면 login.url으로 보냄(GET) => else(GET) => html의 form(POST) => login request.POST 
# ?next=account/profile/
@login_required
def profile(request):
    user = request.user
    context = { 'user': user }
    return render(request, 'accounts/profile.html', context)

@login_required
@require_http_methods(['GET', 'POST'])
def update(request, username):
    user = get_object_or_404(User, username=username)
    context = {'user_profile': user}
    if user == request.user:
        if request.method == "POST":
            form = CustomUserChangeForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                return redirect(request.GET.get('next') or 'accounts:profile')
        else:
            form = CustomUserChangeForm(instance=user)
        context['form'] = form
        return render(request, 'accounts/update.html', context)


@login_required
def logout(request):
    auth_logout(request)
    return redirect('accounts:index')
    

@login_required
@require_POST
def withdraw(request):
    # 삭제 먼저하고 로그아웃시키기
    user = request.user
    user.delete()
    auth_logout(request)
    return redirect('accounts:index')


@login_required
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()  # save먼저 해야 로그인 유지
            update_session_auth_hash(request, form.user)  # 해시 업데이트
            
            return redirect('accounts:index')

    else:
        form = PasswordChangeForm(request.user)
    context = { 'form': form }
    return render(request, 'accounts/change_password.html', context)

