from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignupForm, LoginForm
from django.http import HttpResponse
from .models import Project, Task
import logging
from django.contrib import messages
from django.utils import timezone

# Logger setup
logger = logging.getLogger(__name__)

# Home view
def home(request):
    current_date = timezone.now().strftime("%B %d, %Y")  # Format: "April 15, 2022"
    return render(request, 'home.html', {'current_date': current_date})

# Signup view
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            logger.info(f'User {user.username} created')
            messages.success(request, "Account created successfully. Please log in.")
            return redirect('login')  # Redirect to login page
        else:
            messages.error(request, "There was an error creating your account. Please try again.")
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})

# Login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# Logout view
@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')

# Create a new project
@login_required
def create_project(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name:  # Ensure the project has a valid name
            project = Project(name=name, description=description, owner=request.user)
            project.save()
            logger.info(f'Project {name} created by {request.user}')
            messages.success(request, f"Project '{name}' created successfully.")
            return redirect('project_list')
        else:
            messages.error(request, "Project name cannot be empty.")
    return render(request, 'create_project.html')

# List of projects
@login_required
def project_list(request):
    projects = Project.objects.filter(owner=request.user)
    logger.info(f'Projects listed by {request.user}')
    return render(request, 'project_list.html', {'projects': projects})

# Edit a project
@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        if name:  # Ensure the project has a valid name
            project.name = name
            project.description = description
            project.save()
            logger.info(f'Project {name} updated by {request.user}')
            messages.success(request, f"Project '{name}' updated successfully.")
            return redirect('project_list')
        else:
            messages.error(request, "Project name cannot be empty.")
    return render(request, 'edit_project.html', {'project': project})

# Delete a project
@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    logger.info(f'Project {project.name} deleted by {request.user}')
    project_name = project.name
    project.delete()
    messages.success(request, f"Project '{project_name}' deleted successfully.")
    return redirect('project_list')

# Create a task for a project
@login_required
def create_task(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        if title:  # Ensure the task has a valid title
            task = Task.objects.create(title=title, description=description, project=project, assigned_to=request.user)
            logger.info(f'Task created: {task.title} for project {project.name} by {request.user.username}')
            messages.success(request, f"Task '{task.title}' created successfully.")
            return redirect('task_list', project_id=project.id)
        else:
            messages.error(request, "Task title cannot be empty.")
    return render(request, 'create_task.html', {'project': project})

# List tasks for a project
@login_required
def task_list(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    tasks = project.tasks.all()
    logger.info(f'Tasks listed for project {project.name} by {request.user.username}')
    return render(request, 'task_list.html', {'project': project, 'tasks': tasks})

# Edit a task
@login_required
def edit_task(request, task_id, project_id):
    task = get_object_or_404(Task, id=task_id, project__owner=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        status = request.POST.get('status')
        if title:  # Ensure the task has a valid title
            task.title = title
            task.description = description
            task.status = status
            task.save()
            logger.info(f'Task {task.title} updated by {request.user.username}')
            messages.success(request, f"Task '{task.title}' updated successfully.")
            return redirect('task_list', project_id=project_id)
        else:
            messages.error(request, "Task title cannot be empty.")
    return render(request, 'edit_task.html', {'task': task})

# Delete a task
@login_required
def delete_task(request, task_id, project_id):
    task = get_object_or_404(Task, id=task_id, project__owner=request.user)
    logger.info(f'Task {task.title} deleted by {request.user.username}')
    task_title = task.title
    task.delete()
    messages.success(request, f"Task '{task_title}' deleted successfully.")
    return redirect('task_list', project_id=project_id)