from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .models import UserSubject, Subject
from subjectreg.models import Subject
from django.db import transaction

# Login view
def user_login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('subject_list')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Logout view
def user_logout(request):
    logout(request)
    return redirect('user_login')

# Helper function to check if a user is an admin
def is_admin(user):
    return user.is_staff or user.is_superuser

# Admin login view
def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and is_admin(user):
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid credentials or not an admin')
    return render(request, 'admin_login.html')

# Admin dashboard view to show subjects and registered users
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    subjects = Subject.objects.all()
    return render(request, 'admin_dashboard.html', {'subjects': subjects})

# Subject List and Registration view
@login_required
def subject_list(request):
    subjects = Subject.objects.all()  # Remove the filter to show all subjects
    user_subjects = UserSubject.objects.filter(user=request.user)
    registered_subjects = [us.subject for us in user_subjects]

    return render(request, 'subject_list.html', {
        'subjects': subjects,
        'registered_subjects': registered_subjects
    })

# Register for a subject
@login_required
@transaction.atomic
def register_subject(request, subject_id):
    subject = Subject.objects.get(id=subject_id)

    if subject.max_students > 0:
        UserSubject.objects.create(user=request.user, subject=subject)
        subject.max_students -= 1
        if subject.max_students == 0:
            subject.open_for_registration = False
        subject.save()

    return redirect('subject_list')

# Unregister from a subject
@login_required
@transaction.atomic
def unregister_subject(request, subject_id):
    subject = Subject.objects.get(id=subject_id)
    UserSubject.objects.filter(user=request.user, subject=subject).delete()

    subject.max_students += 1
    subject.open_for_registration = True
    subject.save()

    return redirect('subject_list')
