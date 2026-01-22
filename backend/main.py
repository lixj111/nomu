"""FastAPI应用入口"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from core.config import settings
from api.v1 import auth, ledgers, accounts, upload, statistics, export

# 创建应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="智账-AI自动记账系统API",
    debug=settings.DEBUG
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
# 配置静态文件服务：获取上传目录的父目录（backend/static）
static_dir = Path(settings.UPLOAD_DIR).parent
# 确保静态文件目录存在
static_dir.mkdir(parents=True, exist_ok=True)
# 挂载静态文件目录到 /static 路径，支持图片等资源访问
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# 注册路由
app.include_router(auth.router, prefix="/api/v1", tags=["认证"])
app.include_router(ledgers.router, prefix="/api/v1", tags=["账本"])
app.include_router(accounts.router, prefix="/api/v1", tags=["账单"])
app.include_router(upload.router, prefix="/api/v1", tags=["上传"])
app.include_router(statistics.router, prefix="/api/v1", tags=["统计"])
app.include_router(export.router, prefix="/api/v1", tags=["导出"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    # 计算超时时间（秒）
    timeout_keep_alive = settings.API_TIMEOUT

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        timeout_keep_alive=timeout_keep_alive,
        limit_concurrency=10
    )
