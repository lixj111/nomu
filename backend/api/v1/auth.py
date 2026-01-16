"""认证相关API"""
from fastapi import APIRouter, Depends, HTTPException, status
from database.models import User
from database.operations import DatabaseManager
from schemas.user import UserCreate, UserLogin, UserResponse, Token
from schemas.response import ResponseModel
from services.auth_service import AuthService
from api.deps import get_db, get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/register", response_model=ResponseModel[Token])
async def register(
    user_data: UserCreate,
    db: DatabaseManager = Depends(get_db)
):
    """用户注册"""
    try:
        auth_service = AuthService(db)
        user = auth_service.register(
            username=user_data.username,
            password=user_data.password,
            email=user_data.email
        )

        # 自动登录
        login_result = auth_service.login(user_data.username, user_data.password)

        return ResponseModel(
            code=201,
            message="注册成功",
            data=login_result
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=ResponseModel[Token])
async def login(
    user_data: UserLogin,
    db: DatabaseManager = Depends(get_db)
):
    """用户登录"""
    try:
        auth_service = AuthService(db)
        result = auth_service.login(user_data.username, user_data.password)

        return ResponseModel(
            code=200,
            message="登录成功",
            data=result
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/me", response_model=ResponseModel[UserResponse])
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """获取当前用户信息"""
    return ResponseModel(
        code=200,
        message="success",
        data=UserResponse(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            is_active=current_user.is_active
        )
    )
