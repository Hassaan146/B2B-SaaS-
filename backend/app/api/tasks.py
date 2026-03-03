from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.auth import get_current_user, AuthUser,require_create,require_view,require_edit,require_delete
from app.model.task import Task
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskStatusUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

@router.get("",response_model=List[TaskResponse])
def list_tasks(user:AuthUser=Depends(require_view),db:Session=Depends(get_db)):
    tasks=db.query(Task).filter(Task.org_id==user.org_id).all()
    if tasks is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tasks not found")
    return tasks


@router.post("",response_model=TaskResponse)
def create_task(task:TaskCreate,user:AuthUser=Depends(require_create),db:Session=Depends(get_db)):
    db_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        org_id=user.org_id,
        created_by=user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/{task_id}",response_model=TaskResponse)
def get_task(task_id:str,user:AuthUser=Depends(require_view),db:Session=Depends(get_db)):
    task=db.query(Task).filter(Task.id==task_id,Task.org_id==user.org_id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    return task


@router.put("/{task_id}",response_model=TaskResponse)
def update_task(task_id:str,task_update:TaskUpdate,user:AuthUser=Depends(require_edit),db:Session=Depends(get_db)):
    task=db.query(Task).filter(Task.id==task_id,Task.org_id==user.org_id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    if task_update.title is not None:
        task.title=task_update.title
    if task_update.description is not None:
        task.description=task_update.description
    if task_update.status is not None:
        task.status=task_update.status
    
    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}")
def delete_task(task_id:str,user:AuthUser=Depends(require_delete),db:Session=Depends(get_db)):
    task=db.query(Task).filter(Task.id==task_id,Task.org_id==user.org_id).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    
    db.delete(task)
    db.commit()
    return {"detail": "Task deleted successfully"}