from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignupForm, LoginForm
from django.http import HttpResponse
from .models import Project, Task
import logging
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from django.db.models import Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

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

# List of projects with search and filtering
@login_required
def project_list(request):
    search_query = request.GET.get('search', '').strip()
    sort_by = request.GET.get('sort', 'name')  # Default sort by name
    
    # Base queryset
    projects = Project.objects.filter(owner=request.user).annotate(
        task_count=Count('tasks')
    )

    # Apply search if query exists
    if search_query:
        search_words = search_query.split()
        query = Q()
        for word in search_words:
            query |= Q(name__icontains=word) | Q(description__icontains=word)
        projects = projects.filter(query).distinct()
        logger.info(f'Search performed by {request.user} with query: {search_query}')

    # Apply sorting
    if sort_by == 'tasks':
        projects = projects.order_by('-task_count')
    elif sort_by == 'recent':
        projects = projects.order_by('-created_at')
    else:  # default to name
        projects = projects.order_by('name')

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(projects, 10)  # Show 10 projects per page

    try:
        projects = paginator.page(page)
    except PageNotAnInteger:
        projects = paginator.page(1)
    except EmptyPage:
        projects = paginator.page(paginator.num_pages)

    context = {
        'projects': projects,
        'search_query': search_query,
        'sort_by': sort_by,
        'total_count': paginator.count,
    }

    return render(request, 'project_list.html', context)

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
    active_users = User.objects.filter(is_active=True)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        assigned_to_id = request.POST.get('assigned_to')
        
        if title:
            task = Task.objects.create(
                title=title,
                description=description,
                project=project,
                assigned_to_id=assigned_to_id if assigned_to_id else None
            )
            logger.info(f'Task created: {task.title} for project {project.name} by {request.user.username}')
            messages.success(request, f"Task '{task.title}' created successfully.")
            return redirect('task_list', project_id=project.id)
        else:
            messages.error(request, "Task title cannot be empty.")
    
    return render(request, 'create_task.html', {
        'project': project,
        'active_users': active_users
    })

# List tasks for a project with search and filtering
@login_required
def task_list(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '')
    assignee_filter = request.GET.get('assignee', '')
    sort_by = request.GET.get('sort', 'created')  # Default sort by creation date

    # Base queryset
    tasks = project.tasks.all()

    # Apply search if query exists
    if search_query:
        search_words = search_query.split()
        query = Q()
        for word in search_words:
            query |= Q(title__icontains=word) | Q(description__icontains=word)
        tasks = tasks.filter(query).distinct()
        logger.info(f'Task search performed by {request.user} with query: {search_query}')

    # Apply filters
    if status_filter:
        tasks = tasks.filter(status=status_filter)
    
    if assignee_filter:
        if assignee_filter == 'unassigned':
            tasks = tasks.filter(assigned_to__isnull=True)
        else:
            tasks = tasks.filter(assigned_to_id=assignee_filter)

    # Apply sorting
    if sort_by == 'title':
        tasks = tasks.order_by('title')
    elif sort_by == 'status':
        tasks = tasks.order_by('status')
    elif sort_by == 'assignee':
        tasks = tasks.order_by('assigned_to__username')
    else:  # default to created date
        tasks = tasks.order_by('-created_at')

    # Pagination
    page = request.GET.get('page', 1)
    paginator = Paginator(tasks, 10)  # Show 10 tasks per page

    try:
        tasks = paginator.page(page)
    except PageNotAnInteger:
        tasks = paginator.page(1)
    except EmptyPage:
        tasks = paginator.page(paginator.num_pages)

    # Get all active users for assignee filter
    active_users = User.objects.filter(is_active=True)

    context = {
        'project': project,
        'tasks': tasks,
        'search_query': search_query,
        'status_filter': status_filter,
        'assignee_filter': assignee_filter,
        'sort_by': sort_by,
        'active_users': active_users,
        'total_count': paginator.count,
        'status_choices': Task.STATUS_CHOICES,
    }

    return render(request, 'task_list.html', context)

# Edit a task
@login_required
def edit_task(request, task_id, project_id):
    task = get_object_or_404(Task, id=task_id, project__owner=request.user)
    active_users = User.objects.filter(is_active=True)
    
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        status = request.POST.get('status')
        assigned_to_id = request.POST.get('assigned_to')
        
        if title:
            task.title = title
            task.description = description
            task.status = status
            task.assigned_to_id = assigned_to_id if assigned_to_id else None
            task.save()
            logger.info(f'Task {task.title} updated by {request.user.username}')
            messages.success(request, f"Task '{task.title}' updated successfully.")
            return redirect('task_list', project_id=project_id)
        else:
            messages.error(request, "Task title cannot be empty.")
    
    return render(request, 'edit_task.html', {
        'task': task,
        'active_users': active_users
    })

# Delete a task
@login_required
def delete_task(request, task_id, project_id):
    task = get_object_or_404(Task, id=task_id, project__owner=request.user)
    logger.info(f'Task {task.title} deleted by {request.user.username}')
    task_title = task.title
    task.delete()
    messages.success(request, f"Task '{task_title}' deleted successfully.")
    return redirect('task_list', project_id=project_id)

# Utility function for search
def perform_search(queryset, search_query, search_fields):
    """
    Utility function to perform search across specified fields
    """
    if search_query:
        search_words = search_query.strip().split()
        query = Q()
        for word in search_words:
            word_query = Q()
            for field in search_fields:
                word_query |= Q(**{f'{field}__icontains': word})
            query |= word_query
        return queryset.filter(query).distinct()
    return queryset