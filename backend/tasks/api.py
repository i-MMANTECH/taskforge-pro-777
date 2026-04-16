from ninja import Router, Schema
from tasks.models import Project, Task, Team
from tasks.schemas import ProjectIn, ProjectOut, TaskIn, TaskOut
from tasks.auth import AuthBearer, generate_jwt
from django.contrib.auth.models import User
from typing import List
from ninja.errors import HttpError
from django.shortcuts import get_object_or_404
from tasks.schemas import ProjectIn, ProjectOut, TaskIn, TaskOut, UserSchema, TeamSchema

router = Router()

class LoginSchema(Schema):
    username: str
    password: str

@router.post('/login')
def login(request, data: LoginSchema):
    user = User.objects.filter(username=data.username).first()
    if user and user.check_password(data.password):
        return {'token': generate_jwt(user.id)}
    raise HttpError(401, 'Invalid credentials')

# Project CRUD
@router.post('/projects/', auth=AuthBearer(), response=ProjectOut)
def create_project(request, data: ProjectIn):
    user_id = request.auth
    try:
        team = get_object_or_404(Team, id=data.team_id) if data.team_id else None
        project = Project.objects.create(
            name=data.name, description=data.description, start_date=data.start_date,
            end_date=data.end_date, owner_id=user_id, team=team
        )
        # Manually convert to ProjectOut
        return ProjectOut(
            id=project.id,
            name=project.name,
            description=project.description,
            start_date=project.start_date,
            end_date=project.end_date,
            owner=UserSchema(id=project.owner.id, username=project.owner.username),
            team=TeamSchema(id=project.team.id, name=project.team.name, description=project.team.description) if project.team else None
        )
    except Exception as e:
        raise HttpError(400, str(e))

@router.get('/projects/', auth=AuthBearer(), response=List[ProjectOut])
def list_projects(request):
    projects = Project.objects.all()
    return [
        ProjectOut(
            id=p.id,
            name=p.name,
            description=p.description,
            start_date=p.start_date,
            end_date=p.end_date,
            owner=UserSchema(id=p.owner.id, username=p.owner.username),
            team=TeamSchema(id=p.team.id, name=p.team.name, description=p.team.description) if p.team else None
        ) for p in projects
    ]

@router.get('/projects/{project_id}', auth=AuthBearer(), response=ProjectOut)
def get_project(request, project_id: int):
    project = get_object_or_404(Project, id=project_id)
    return ProjectOut(
        id=project.id,
        name=project.name,
        description=project.description,
        start_date=project.start_date,
        end_date=project.end_date,
        owner=UserSchema(id=project.owner.id, username=project.owner.username),
        team=TeamSchema(id=project.team.id, name=project.team.name, description=project.team.description) if project.team else None
    )

@router.put('/projects/{project_id}', auth=AuthBearer(), response=ProjectOut)
def update_project(request, project_id: int, data: ProjectIn):
    project = get_object_or_404(Project, id=project_id)
    # Simple auth check: only owner can update (expand as needed)
    if project.owner.id != request.auth:
        raise HttpError(403, 'Not authorized')
    team = get_object_or_404(Team, id=data.team_id) if data.team_id else None
    project.name = data.name
    project.description = data.description
    project.start_date = data.start_date
    project.end_date = data.end_date
    project.team = team
    project.save()
    return ProjectOut(
        id=project.id,
        name=project.name,
        description=project.description,
        start_date=project.start_date,
        end_date=project.end_date,
        owner=UserSchema(id=project.owner.id, username=project.owner.username),
        team=TeamSchema(id=project.team.id, name=project.team.name, description=project.team.description) if project.team else None
    )

@router.delete('/projects/{project_id}', auth=AuthBearer())
def delete_project(request, project_id: int):
    project = get_object_or_404(Project, id=project_id)
    if project.owner.id != request.auth:
        raise HttpError(403, 'Not authorized')
    project.delete()
    return {'success': True}

# Task CRUD
@router.post('/tasks/', auth=AuthBearer(), response=TaskOut)
def create_task(request, data: TaskIn):
    try:
        project = get_object_or_404(Project, id=data.project_id)
        assigned_to = get_object_or_404(User, id=data.assigned_to_id) if data.assigned_to_id else None
        task = Task.objects.create(
            title=data.title, description=data.description, status=data.status,
            priority=data.priority, due_date=data.due_date, project=project, assigned_to=assigned_to
        )
        # Manually convert to TaskOut
        return TaskOut(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            project=ProjectOut(
                id=task.project.id,
                name=task.project.name,
                description=task.project.description,
                start_date=task.project.start_date,
                end_date=task.project.end_date,
                owner=UserSchema(id=task.project.owner.id, username=task.project.owner.username),
                team=TeamSchema(id=task.project.team.id, name=task.project.team.name, description=task.project.team.description) if task.project.team else None
            ),
            assigned_to=UserSchema(id=task.assigned_to.id, username=task.assigned_to.username) if task.assigned_to else None
        )
    except Exception as e:
        raise HttpError(400, str(e))

@router.get('/tasks/', auth=AuthBearer(), response=List[TaskOut])
def list_tasks(request):
    tasks = Task.objects.all()
    return [
        TaskOut(
            id=t.id,
            title=t.title,
            description=t.description,
            status=t.status,
            priority=t.priority,
            due_date=t.due_date,
            project=ProjectOut(
                id=t.project.id,
                name=t.project.name,
                description=t.project.description,
                start_date=t.project.start_date,
                end_date=t.project.end_date,
                owner=UserSchema(id=t.project.owner.id, username=t.project.owner.username),
                team=TeamSchema(id=t.project.team.id, name=t.project.team.name, description=t.project.team.description) if t.project.team else None
            ),
            assigned_to=UserSchema(id=t.assigned_to.id, username=t.assigned_to.username) if t.assigned_to else None
        ) for t in tasks
    ]

@router.get('/tasks/{task_id}', auth=AuthBearer(), response=TaskOut)
def get_task(request, task_id: int):
    task = get_object_or_404(Task, id=task_id)
    return TaskOut(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        project=ProjectOut(
            id=task.project.id,
            name=task.project.name,
            description=task.project.description,
            start_date=task.project.start_date,
            end_date=task.project.end_date,
            owner=UserSchema(id=task.project.owner.id, username=task.project.owner.username),
            team=TeamSchema(id=task.project.team.id, name=task.project.team.name, description=task.project.team.description) if task.project.team else None
        ),
        assigned_to=UserSchema(id=task.assigned_to.id, username=task.assigned_to.username) if task.assigned_to else None
    )

@router.put('/tasks/{task_id}', auth=AuthBearer(), response=TaskOut)
def update_task(request, task_id: int, data: TaskIn):
    task = get_object_or_404(Task, id=task_id)
    # Simple auth check: only project owner or assigned can update (expand as needed)
    if task.project.owner.id != request.auth and (not task.assigned_to or task.assigned_to.id != request.auth):
        raise HttpError(403, 'Not authorized')
    project = get_object_or_404(Project, id=data.project_id)
    assigned_to = get_object_or_404(User, id=data.assigned_to_id) if data.assigned_to_id else None
    task.title = data.title
    task.description = data.description
    task.status = data.status
    task.priority = data.priority
    task.due_date = data.due_date
    task.project = project
    task.assigned_to = assigned_to
    task.save()
    return TaskOut(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        due_date=task.due_date,
        project=ProjectOut(
            id=task.project.id,
            name=task.project.name,
            description=task.project.description,
            start_date=task.project.start_date,
            end_date=task.project.end_date,
            owner=UserSchema(id=task.project.owner.id, username=task.project.owner.username),
            team=TeamSchema(id=task.project.team.id, name=task.project.team.name, description=task.project.team.description) if task.project.team else None
        ),
        assigned_to=UserSchema(id=task.assigned_to.id, username=task.assigned_to.username) if task.assigned_to else None
    )

@router.delete('/tasks/{task_id}', auth=AuthBearer())
def delete_task(request, task_id: int):
    task = get_object_or_404(Task, id=task_id)
    if task.project.owner.id != request.auth:
        raise HttpError(403, 'Not authorized')
    task.delete()
    return {'success': True}