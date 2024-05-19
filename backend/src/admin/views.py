from starlette.requests import Request
from sqladmin import ModelView

from src.models.users import User
from src.models.reports import Report
from src.models.departments import Department
from src.models.ranks import Rank
from src.utils.password import ArgonPasswordHashing


class UserAdmin(ModelView, model=User):
    column_list = [c.name for c in User.__table__.c] + [User.rank, User.department]    
    name = "Пользователь"
    name_plural = "Пользователи"
    icon = "fa-solid fa-user"
    
    # async def on_model_change(self, data: dict, model: Any, is_created: bool, request: Request) -> None: 
        
    #     # if value != oldvalue:
    #     # if is_created:
    #     # if value != oldvalue:
    #     #     return generate_password_hash(value)
    #     # return value
        
    #     # if form.password2.data is not None:
    #     #     User.set_password(form.password2.data)
            
    #     data["hashed_password"] = ArgonPasswordHashing.hash_password(data["hashed_password"])
        


class ReportAdmin(ModelView, model=Report):
    column_list = [c.name for c in Report.__table__.c] + [Report.department]
    name = "Отчёт"
    name_plural = "Отчёты"
    icon = "fa-solid fa-layer-group"


class DepartmentAdmin(ModelView, model=Department):
    column_list = [c.name for c in Department.__table__.c] + [Department.user, Department.report]
    name = "Департамент"
    name_plural = "Департаменты"
    icon = "fa-solid fa-people-group"


class RankAdmin(ModelView, model=Rank):
    column_list = [c.name for c in Rank.__table__.c] + [Rank.user]
    name = "Звание"
    name_plural = "Звания"
    icon = "fa-solid fa-star"
