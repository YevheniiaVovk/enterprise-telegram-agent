import logging
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import User

logger = logging.getLogger(__name__)


class UserRepository:
    """
    Repository for user database operations.
    Handles CRUD operations for users.
    """
    
    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            session: AsyncSession from SQLAlchemy
        """
        self.session = session
    
    async def get_user(self, user_id: int) -> User | None:
        """
        Get user by Telegram ID.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User object or None if not found
        """
        try:
            stmt = select(User).where(User.user_id == user_id)
            result = await self.session.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                logger.info(f"✅ User {user_id} found in database")
            else:
                logger.debug(f"User {user_id} not found in database")
            
            return user
            
        except Exception as e:
            logger.error(f"❌ Error fetching user {user_id}: {e}")
            return None
    
    async def create_user(self, user_id: int, thread_id: str) -> User:
        """
        Create new user in database.
        
        Args:
            user_id: Telegram user ID
            thread_id: LangGraph thread ID for conversation tracking
            
        Returns:
            Created User object
        """
        try:
            user = User(
                user_id=user_id,
                thread_id=thread_id,
                created_at=datetime.utcnow()
            )
            
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
            
            logger.info(f"✅ User {user_id} created with thread {thread_id}")
            return user
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error creating user {user_id}: {e}")
            raise
    
    async def get_or_create_user(self, user_id: int) -> User:
        """
        Get existing user or create new one.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            User object (existing or newly created)
        """
        user = await self.get_user(user_id)
        
        if user:
            return user
        
        # Create new user with thread_id same as user_id
        thread_id = str(user_id)
        return await self.create_user(user_id, thread_id)
    
    async def update_last_interaction(self, user_id: int) -> bool:
        """
        Update user's last interaction timestamp.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            user = await self.get_user(user_id)
            
            if not user:
                logger.warning(f"User {user_id} not found for update")
                return False
            
            user.last_interaction = datetime.utcnow()
            self.session.add(user)
            await self.session.commit()
            
            logger.debug(f"✅ Updated last interaction for user {user_id}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error updating user {user_id}: {e}")
            return False
    
    async def get_all_users(self, limit: int = 100) -> list[User]:
        """
        Get all users from database.
        
        Args:
            limit: Maximum number of users to return
            
        Returns:
            List of User objects
        """
        try:
            stmt = select(User).limit(limit)
            result = await self.session.execute(stmt)
            users = result.scalars().all()
            
            logger.info(f"✅ Fetched {len(users)} users from database")
            return list(users)
            
        except Exception as e:
            logger.error(f"❌ Error fetching users: {e}")
            return []
    
    async def delete_user(self, user_id: int) -> bool:
        """
        Delete user from database.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            user = await self.get_user(user_id)
            
            if not user:
                logger.warning(f"User {user_id} not found for deletion")
                return False
            
            await self.session.delete(user)
            await self.session.commit()
            
            logger.info(f"✅ User {user_id} deleted from database")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"❌ Error deleting user {user_id}: {e}")
            return False