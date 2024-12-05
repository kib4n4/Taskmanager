from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Project, Task

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at', 'updated_at')
    search_fields = ('name', 'description')
    list_filter = ('owner', 'created_at')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'assigned_to', 'status', 'due_date', 'created_at', 'updated_at')
    search_fields = ('title', 'description')
    list_filter = ('project', 'assigned_to', 'status', 'due_date')
    list_editable = ('status', 'assigned_to')
