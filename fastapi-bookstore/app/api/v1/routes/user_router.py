from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends, status

from app.application.commands.register_user import RegisterUserHandler
from app.schemas import UserRegistrationRequest
from app.application.commands.register_user import RegisterUserCommand
from app.core.container import Container

router = APIRouter()

@router.post("", status_code=status.HTTP_201_CREATED)
@inject
async def create_user(
        user_request: UserRegistrationRequest,
        register_user_handler: RegisterUserHandler = Depends(Provide[Container.register_user_handler])
):
    register_user_handler.handle(RegisterUserCommand(
        email=user_request.email,
        phone=user_request.phone,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
    ))
