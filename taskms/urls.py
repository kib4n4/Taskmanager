#urls.py
from django.urls import path
from . import views
from .views import (
    create_project,
    project_list,
    edit_project,
    delete_project,
    create_task,
    task_list,
    edit_task,
    delete_task,
    login_view
)

urlpatterns = [
    path('projects/create/' ,create_project,name='create_project'),
    path('projects/' , project_list, name='project_list'),
    path('projects/<int:project_id>/edit/' , edit_project, name='edit_project'),
    path('projects/<int:project_id>/delete/' , delete_project, name='delete_project'),
    path('projects/<int:project_id>/tasks/create/' , create_task, name='create_task'),
    path('projects/<int:project_id>/tasks/' , task_list, name='task_list'),
    path('projects/<int:project_id>/tasks/<int:task_id>/edit/' , edit_task, name='edit_task'),
    path('projects/<int:project_id>/tasks/<int:task_id>/delete/' , delete_task, name='delete_task'),
    path('login/', views.login_view, name='login')
]
