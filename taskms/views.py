from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import SignupForm, LoginForm
from django.http import HttpResponse
from .models import *
import logging

#logger setup
logger= logging.getLogger(__name__)


# Create your views here.
#homeview
def home(request):
    return render(request, 'home.html')


#create signup view

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            logger.info(f'User {user.username} created')
            return redirect('login')  # Redirect to login page
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


#create login view
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home') 
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


#create a new project and log
@login_required
def create_project(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        project = Project(name=name, description=description, owner=request.user)
        project.save()
        logger.info(f'Project {name} created by {request.user}')
        return redirect('project_list')
    return render(request, 'create_project.html')
    

#List of projects and log
@login_required
def project_list(request):
    projects = Project.objects.filter(owner=request.user)
    logger.info(f'Projects listed by {request.user}')
    return render(request, 'project_list.html', {'projects': projects})

#Edit projects and log
@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        project.name = name
        project.description = description
        project.save()
        logger.info(f'Project {name} updated by {request.user}')
        return redirect('project_list')
    return render(request, 'edit_project.html', {'project': project})


#Delete projects and log
@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    project.delete()
    logger.info(f'Project {project.name} deleted by {request.user}')
    return redirect('project_list')


#create a task for project
@login_required
def create_task(request, project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        task = Task.objects.create(title=title, description=description, project=project, assigned_to=request.user)
        logger.info(f'Task created: {task.title} for project {project.name} by {request.user.username}')
        return redirect('task_list', project_id=project.id)
    return render(request, 'create_task.html', {'project': project})

#Read/list tasks and log
@login_required
def task_list(request,project_id):
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    tasks = project.tasks.all()
    logger.info(f'Tasks listed for project {project.name} by {request.user.username}')
    return render(request, 'task_list.html', {'project': project, 'tasks': tasks})

#Edit tasks and log
@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, project__owner=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        task.status= request.POST.get('status')
        task.title = title
        task.description = description
        task.save()
        logger.info(f'Task {task.title} updated by {request.user.username}')
        return redirect('task_list', project_id=task.project.id)
    return render(request, 'edit_task.html', {'task': task})


#delete tasks and log
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, project__owner=request.user)
    project_id = task.project.id
    task.delete()
    logger.info(f'Task {task.title} deleted by {request.user.username}')
    return redirect('task_list', project_id=project_id)


