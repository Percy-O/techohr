from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import UserRegisterForm, ProfileForm
from django.contrib.auth.decorators import login_required
from .decorators import staff_required
from courses.models import Enrollment, Course, Certificate
from core.models import Service, Project, Contact, Newsletter
from blog.models import Post
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings
from django.urls import reverse

User = get_user_model()

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False # Deactivate until confirmed
            user.is_student = True
            user.save()
            
            # Send Confirmation Email to Student
            current_site = get_current_site(request)
            subject = 'Activate Your TechOhr Account'
            
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            activate_url = request.build_absolute_uri(
                reverse('activate', kwargs={'uidb64': uid, 'token': token})
            )
            
            html_message = render_to_string('emails/student_confirmation.html', {
                'user': user,
                'domain': current_site.domain,
                'activate_url': activate_url
            })
            plain_message = strip_tags(html_message)
            
            try:
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    html_message=html_message,
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Error sending confirmation email: {e}")
                
            # Send Notification Email to Admin
            try:
                dashboard_url = request.build_absolute_uri(reverse('manage_users'))
                admin_html_message = render_to_string('emails/admin_new_student.html', {
                    'user': user,
                    'dashboard_url': dashboard_url
                })
                admin_plain_message = strip_tags(admin_html_message)
                
                send_mail(
                    f'New Student Registration: {user.username}',
                    admin_plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                    html_message=admin_html_message,
                    fail_silently=True,
                )
            except Exception as e:
                print(f"Error sending admin notification: {e}")

            messages.success(request, 'Registration successful. Please check your email to confirm your account.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Your account has been confirmed! Welcome to TechOhr.')
        return redirect('home')
    else:
        messages.error(request, 'Activation link is invalid or has expired.')
        return redirect('home')

def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
        
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f'You are now logged in as {username}.')
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                if user.is_staff:
                    return redirect('admin_dashboard')
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def admin_login(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_dashboard')
        else:
            messages.warning(request, "You are not authorized to access the admin panel.")
            return redirect('dashboard')
            
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_staff:
                    login(request, user)
                    messages.success(request, f'Welcome back, Admin {username}!')
                    next_url = request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    return redirect('admin_dashboard')
                else:
                    messages.error(request, 'Access denied. Staff privileges required.')
            else:
                messages.error(request, 'Invalid credentials.')
        else:
            messages.error(request, 'Invalid credentials.')
    else:
        form = AuthenticationForm()
    return render(request, 'users/admin_login.html', {'form': form})

def user_logout(request):
    logout(request)
    messages.info(request, 'You have successfully logged out.')
    return redirect('home')

@login_required
def dashboard(request):
    # Fetch all enrollments for the user
    enrollments = Enrollment.objects.filter(student=request.user).select_related('course')
    
    active_courses = []
    completed_courses = []
    
    for enrollment in enrollments:
        # Calculate progress dynamically
        progress = enrollment.get_progress()
        enrollment.current_progress = progress # Attach to object for template
        
        # Check if course is completed (either by flag or 100% progress)
        if enrollment.is_completed or progress == 100:
            completed_courses.append(enrollment)
        else:
            active_courses.append(enrollment)
            
    # Fetch certificates
    certificates = Certificate.objects.filter(student=request.user).select_related('course')
    
    context = {
        'active_courses': active_courses,
        'completed_courses': completed_courses,
        'certificates': certificates,
        'total_enrolled': enrollments.count(),
        'total_active': len(active_courses),
        'total_completed': len(completed_courses),
        'total_certificates': certificates.count(),
    }
    return render(request, 'users/dashboard.html', context)

@staff_required
def admin_dashboard(request):
    # Stats
    total_users = User.objects.count()
    total_projects = Project.objects.count()
    total_courses = Course.objects.count()
    total_posts = Post.objects.count()
    total_enrollments = Enrollment.objects.count()
    total_certificates = Certificate.objects.count()
    
    # Recent Data
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_contacts = Contact.objects.order_by('-created_at')[:5]
    recent_subscribers = Newsletter.objects.order_by('-subscribed_at')[:5]
    recent_enrollments = Enrollment.objects.order_by('-enrolled_at')[:5]
    
    context = {
        'total_users': total_users,
        'total_projects': total_projects,
        'total_courses': total_courses,
        'total_posts': total_posts,
        'total_enrollments': total_enrollments,
        'total_certificates': total_certificates,
        'recent_users': recent_users,
        'recent_contacts': recent_contacts,
        'recent_subscribers': recent_subscribers,
        'recent_enrollments': recent_enrollments,
    }
    return render(request, 'users/admin_dashboard.html', context)

from django.core.paginator import Paginator

@staff_required
def manage_users(request):
    user_list = User.objects.all().order_by('-date_joined')
    paginator = Paginator(user_list, 5) # Show 5 users per page.
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    return render(request, 'users/manage_users.html', {'users': users})

@staff_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_superuser:
        messages.error(request, "Cannot delete a superuser.")
    else:
        user.delete()
        messages.success(request, "User deleted successfully.")
    return redirect('manage_users')

@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    
    return render(request, 'users/profile.html', {'form': form})

@staff_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user.is_active:
        user.is_active = False
        messages.warning(request, f"User {user.username} has been deactivated.")
    else:
        user.is_active = True
        messages.success(request, f"User {user.username} has been activated.")
    user.save()
    return redirect('manage_users')
