from app.users.models import User
from sqladmin import ModelView


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email, User.portfolio_id, User.is_sub]
    column_details_exclude_list = [User.password_hashed]
    can_delete = False
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"