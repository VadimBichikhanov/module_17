from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from backend.db_depends import get_async_db
from typing import Annotated
from models.task import Task  # Correct import statement
from models.user import User  # Import User model for user existence check
from schemas.task import CreateTask, UpdateTask
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix='/task', tags=['task'])

@router.get('/', summary="Get all tasks", description="Retrieve a list of all tasks.")
async def all_tasks(db: Annotated[AsyncSession, Depends(get_async_db)]):
    try:
        result = await db.execute(select(Task))
        tasks = result.scalars().all()
        if not tasks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There are no tasks'
            )
        # Convert tasks to a list of dictionaries
        tasks_dicts = [task.__dict__ for task in tasks]
        return tasks_dicts
    except Exception as e:
        logger.error(f"Error fetching all tasks: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post('/create', summary="Create a new task", description="Create a new task with the provided details.")
async def create_task(db: Annotated[AsyncSession, Depends(get_async_db)], create_task: CreateTask):
    try:
        # Check if the user exists
        result = await db.execute(select(User).where(User.id == create_task.user_id))
        user = result.scalar()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User was not found'
            )

        await db.execute(insert(Task).values(
            title=create_task.title,
            content=create_task.content,
            priority=create_task.priority,
            user_id=create_task.user_id
        ))
        await db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get('/{task_id}', summary="Get task by ID", description="Retrieve a task by its ID.")
async def task_by_id(db: Annotated[AsyncSession, Depends(get_async_db)], task_id: int):
    try:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task = result.scalar()
        if task is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Task not found'
            )
        # Convert task to a dictionary
        task_dict = task.__dict__
        return task_dict
    except Exception as e:
        logger.error(f"Error fetching task by ID {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.put('/update/{task_id}', summary="Update a task", description="Update an existing task by its ID.")
async def update_task(db: Annotated[AsyncSession, Depends(get_async_db)], task_id: int, update_task_model: UpdateTask):
    try:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task_update = result.scalar()
        if task_update is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Task not found'
            )

        await db.execute(update(Task).where(Task.id == task_id)
                   .values(
                       title=update_task_model.title,
                       content=update_task_model.content,
                       priority=update_task_model.priority
                   ))
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Task update is successful'
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.delete('/delete/{task_id}', summary="Delete a task", description="Delete a task by its ID.")
async def delete_task(db: Annotated[AsyncSession, Depends(get_async_db)], task_id: int):
    try:
        result = await db.execute(select(Task).where(Task.id == task_id))
        task_delete = result.scalar()
        if task_delete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Task not found'
            )
        await db.execute(delete(Task).where(Task.id == task_id))
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Task delete is successful'
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")