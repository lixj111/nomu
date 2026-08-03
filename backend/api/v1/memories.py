"""回忆相关API"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import List
from database.models import User, Memory, MemoryEvent, MemoryPhoto
from database.operations import DatabaseManager
from schemas.memory import (
    MemoryCreate, MemoryUpdate, MemoryResponse,
    MemoryEventCreate, MemoryEventUpdate, MemoryEventResponse,
    MemoryPhotoResponse
)
from schemas.response import ResponseModel
from services.image_service import ImageService
from api.deps import get_db, get_current_user

router = APIRouter(prefix="/memories", tags=["回忆"])

logger = logging.getLogger(__name__)


def _build_event_response(event: MemoryEvent, db: DatabaseManager) -> MemoryEventResponse:
    """构造事件响应（含照片列表）"""
    photos = db.get_photos_by_event(event.id)
    return MemoryEventResponse(
        id=event.id,
        memory_id=event.memory_id,
        title=event.title,
        event_date=event.event_date,
        description=event.description,
        location=event.location,
        cover_path=event.cover_path,
        author=event.author,
        photos=[MemoryPhotoResponse(
            id=p.id,
            event_id=p.event_id,
            image_path=p.image_path,
            caption=p.caption,
            created_at=p.created_at
        ) for p in photos],
        created_at=event.created_at,
        updated_at=event.updated_at
    )


def _memory_to_response(memory: Memory) -> MemoryResponse:
    """构造回忆空间响应"""
    return MemoryResponse(
        id=memory.id,
        user_id=memory.user_id,
        partner_name=memory.partner_name,
        partner_avatar=memory.partner_avatar,
        story=memory.story,
        created_at=memory.created_at,
        updated_at=memory.updated_at
    )


def _assert_event_owned(event: MemoryEvent, current_user: User, db: DatabaseManager):
    """校验事件归属当前用户，校验失败抛 403"""
    memory = db.get_memory_by_id(event.memory_id)
    if not memory or memory.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权操作该事件")


# ==================== 回忆空间 ====================

@router.get("", response_model=ResponseModel[dict])
async def get_memory(
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """获取当前用户的回忆空间及事件列表（一次返回供前端渲染时间线）"""
    memory = db.get_memory_by_user(current_user.id)
    if not memory:
        return ResponseModel(code=200, message="success", data={"memory": None, "events": []})

    events = db.get_memory_events(memory.id)
    event_list = [_build_event_response(e, db) for e in events]
    return ResponseModel(
        code=200,
        message="success",
        data={"memory": _memory_to_response(memory), "events": event_list}
    )


@router.post("", response_model=ResponseModel[MemoryResponse])
async def create_memory(
    memory_data: MemoryCreate,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """创建回忆空间（一人一回忆）"""
    if db.get_memory_by_user(current_user.id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="回忆空间已存在")

    memory = Memory(
        user_id=current_user.id,
        partner_name=memory_data.partner_name,
        partner_avatar=memory_data.partner_avatar,
        story=memory_data.story
    )
    memory_id = db.create_memory(memory)
    created = db.get_memory_by_id(memory_id)
    return ResponseModel(code=201, message="创建成功", data=_memory_to_response(created))


@router.put("", response_model=ResponseModel[MemoryResponse])
async def update_memory(
    memory_data: MemoryUpdate,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """更新回忆空间（对象名/头像/寄语）"""
    memory = db.get_memory_by_user(current_user.id)
    if not memory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="回忆空间不存在")

    if memory_data.partner_name is not None:
        memory.partner_name = memory_data.partner_name
    if memory_data.partner_avatar is not None:
        memory.partner_avatar = memory_data.partner_avatar
    if memory_data.story is not None:
        memory.story = memory_data.story

    db.update_memory(memory.id, memory)
    updated = db.get_memory_by_id(memory.id)
    return ResponseModel(code=200, message="更新成功", data=_memory_to_response(updated))


# ==================== 回忆事件 ====================

@router.post("/events", response_model=ResponseModel[MemoryEventResponse])
async def create_event(
    event_data: MemoryEventCreate,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """新建回忆事件"""
    memory = db.get_memory_by_user(current_user.id)
    if not memory:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="请先创建回忆空间")

    event = MemoryEvent(
        memory_id=memory.id,
        title=event_data.title,
        event_date=event_data.event_date,
        description=event_data.description,
        location=event_data.location,
        cover_path=event_data.cover_path,
        author=event_data.author
    )
    event_id = db.create_memory_event(event)
    created = db.get_memory_event_by_id(event_id)
    return ResponseModel(code=201, message="创建成功", data=_build_event_response(created, db))


@router.put("/events/{event_id}", response_model=ResponseModel[MemoryEventResponse])
async def update_event(
    event_id: int,
    event_data: MemoryEventUpdate,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """更新回忆事件"""
    event = db.get_memory_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="事件不存在")
    _assert_event_owned(event, current_user, db)

    if event_data.title is not None:
        event.title = event_data.title
    if event_data.event_date is not None:
        event.event_date = event_data.event_date
    if event_data.description is not None:
        event.description = event_data.description
    if event_data.location is not None:
        event.location = event_data.location
    if event_data.cover_path is not None:
        event.cover_path = event_data.cover_path
    if event_data.author is not None:
        event.author = event_data.author

    db.update_memory_event(event_id, event)
    updated = db.get_memory_event_by_id(event_id)
    return ResponseModel(code=200, message="更新成功", data=_build_event_response(updated, db))


@router.delete("/events/{event_id}", response_model=ResponseModel[dict])
async def delete_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """删除回忆事件（级联软删其照片）"""
    event = db.get_memory_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="事件不存在")
    _assert_event_owned(event, current_user, db)

    db.delete_memory_event(event_id)
    return ResponseModel(code=200, message="删除成功", data=None)


# ==================== 回忆照片 ====================

@router.post("/events/{event_id}/photos", response_model=ResponseModel[List[MemoryPhotoResponse]])
async def upload_event_photos(
    event_id: int,
    files: List[UploadFile] = File(...),
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """为事件上传照片（可批量，复用 ImageService 保存）"""
    event = db.get_memory_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="事件不存在")
    _assert_event_owned(event, current_user, db)

    if len(files) > 20:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="单次最多上传20张照片")

    image_service = ImageService()
    result = []
    try:
        for file in files:
            relative_path = await image_service.save_upload_file(file)
            photo_id = db.create_memory_photo(MemoryPhoto(event_id=event_id, image_path=relative_path))
            created = db.get_memory_photo_by_id(photo_id)
            result.append(MemoryPhotoResponse(
                id=created.id,
                event_id=created.event_id,
                image_path=created.image_path,
                caption=created.caption,
                created_at=created.created_at
            ))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传回忆照片失败: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"上传失败: {str(e)}")

    return ResponseModel(code=201, message=f"成功上传 {len(result)} 张照片", data=result)


@router.delete("/photos/{photo_id}", response_model=ResponseModel[dict])
async def delete_photo(
    photo_id: int,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db)
):
    """删除单张回忆照片（同时清理磁盘文件）"""
    photo = db.get_memory_photo_by_id(photo_id)
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="照片不存在")

    event = db.get_memory_event_by_id(photo.event_id)
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="事件不存在")
    _assert_event_owned(event, current_user, db)

    db.delete_memory_photo(photo_id)
    # 清理磁盘文件
    ImageService().delete_file(photo.image_path)

    return ResponseModel(code=200, message="删除成功", data=None)
