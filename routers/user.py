from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from slugify import slugify
from backend.db_depends import get_async_db
from typing import Annotated
from models.user import User  # Correct import statement
from models.task import Task  # Import Task model for tasks deletion
from schemas.user import CreateUser, UpdateUser
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix='/user', tags=['user'])

@router.get('/', summary="Get all users", description="Retrieve a list of all users.")
async def all_users(db: Annotated[AsyncSession, Depends(get_async_db)]):
    try:
        result = await db.execute(select(User))
        users = result.scalars().all()
        if not users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There are no users'
            )
        # Convert users to a list of dictionaries
        users_dicts = [user.__dict__ for user in users]
        return users_dicts
    except Exception as e:
        logger.error(f"Error fetching all users: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.post('/create', summary="Create a new user", description="Create a new user with the provided details.")
async def create_user(db: Annotated[AsyncSession, Depends(get_async_db)], create_user: CreateUser):
    try:
        await db.execute(insert(User).values(
            username=create_user.username,
            firstname=create_user.firstname,
            lastname=create_user.lastname,
            age=create_user.age,
            slug=slugify(create_user.firstname)
        ))
        await db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating user: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get('/{user_id}', summary="Get user by ID", description="Retrieve a user by their ID.")
async def user_by_id(db: Annotated[AsyncSession, Depends(get_async_db)], user_id: int):
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )
        # Convert user to a dictionary
        user_dict = user.__dict__
        return user_dict
    except Exception as e:
        logger.error(f"Error fetching user by ID {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.put('/update/{user_id}', summary="Update a user", description="Update an existing user by their ID.")
async def update_user(db: Annotated[AsyncSession, Depends(get_async_db)], user_id: int, update_user_model: UpdateUser):
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user_update = result.scalar()
        if user_update is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )

        await db.execute(update(User).where(User.id == user_id)
                   .values(
                       firstname=update_user_model.firstname,
                       lastname=update_user_model.lastname,
                       age=update_user_model.age,
                       slug=slugify(update_user_model.firstname)
                   ))
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'User update is successful'
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.delete('/delete/{user_id}', summary="Delete a user and all associated tasks", description="Delete a user by their ID and all tasks associated with that user.")
async def delete_user(db: Annotated[AsyncSession, Depends(get_async_db)], user_id: int):
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user_delete = result.scalar()
        if user_delete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )
        # Delete all tasks associated with the user
        await db.execute(delete(Task).where(Task.user_id == user_id))
        await db.execute(delete(User).where(User.id == user_id))
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'User and associated tasks delete is successful'
        }
    except Exception as e:
        await db.rollback()
        logger.error(f"Error deleting user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@router.get('/{user_id}/tasks', summary="Get all tasks for a user", description="Retrieve all tasks for a specific user by user ID.")
async def tasks_by_user_id(db: Annotated[AsyncSession, Depends(get_async_db)], user_id: int):
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar()
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )
        result = await db.execute(select(Task).where(Task.user_id == user_id))
        tasks = result.scalars().all()
        # Convert tasks to a list of dictionaries
        tasks_dicts = [task.__dict__ for task in tasks]
        return tasks_dicts
    except Exception as e:
        logger.error(f"Error fetching tasks for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")