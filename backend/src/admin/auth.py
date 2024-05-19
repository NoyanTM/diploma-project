from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from src.services.users import AuthService
from src.models.users import Role
from src.database import async_session_maker
from src.utils.jwt import JWT
from src.dependencies import get_current_active_user_admin_panel
from src.config import settings


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        username, password = form["username"], form["password"]
        
        async with async_session_maker() as session:
            #try:
                user = await AuthService(session=session).authenticate_user(username, password)
                
                if not user.is_active:
                    return False
                if not user.role is Role.ADMIN: # (Role.MODERATOR or Role.ADMIN):
                    return False
                
                if user:
                    access_token = JWT.encode_jwt(
                        secret_key=settings.security.jwt_private, # settings.security.PRIVATE_KEY_LOCAL_PATH.read_text(),
                        data={
                            "sub": user.email, # str(user.id)
                            "role": user.role,
                            "department_id": user.department_id,
                            "rank": user.rank_id,
                        },
                    )
                    request.session.update({"token": access_token})
                return True
            
            #except SQLAlchemyError as e:
            #    print("Database exception:", e)
            #    await session.rollback()
            #    raise DatabaseException
            #finally:
            #    await session.close()
    
    
    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    
    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")
        if not token:
            return False
        
        async with async_session_maker() as session:
            #try:
                user = await get_current_active_user_admin_panel(session=session, token=token)
                
                # logger.debug(f"{user=}")
                if not user:
                    return False
                
                
                return True
            #except SQLAlchemyError as e:
            #    print("Database exception:", e)
            #    await session.rollback()
            #    raise DatabaseException
            #finally:
            #    await session.close()


authentication_backend = AdminAuth(secret_key="...")
