"""AI 分析对话 API（SSE 流式 + 会话持久化）"""
import json
from typing import Iterator, List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from agent.conversation_agent import ConversationAgent
from api.deps import get_db, get_current_user
from core.config import settings
from database.models import User
from database.operations import DatabaseManager
from schemas.ai_chat import (
    AIChatRequest,
    ChatMessageOut,
    ChatSessionCreate,
    ChatSessionOut,
)
from schemas.response import ResponseModel

router = APIRouter(prefix="/ai", tags=["AI分析"])


def sse_frame(evt: dict) -> str:
    """将事件 dict 编码为 SSE 帧"""
    return f"data: {json.dumps(evt, ensure_ascii=False)}\n\n"


def _persist_chat(db: DatabaseManager, session_id: int, user_id: int, user_msg: str, reply: str):
    """将一轮对话写入数据库：user 提问 + assistant 回复，并维护会话标题与时间"""
    db.add_chat_message(session_id, "user", user_msg)
    db.add_chat_message(session_id, "assistant", reply)
    db.touch_chat_session(session_id)
    sess = db.get_chat_session(session_id, user_id)
    if sess and (not sess.title or sess.title == "新会话"):
        db.update_chat_session_title(session_id, (user_msg or "新会话")[:20])


def generate_sse(payload: AIChatRequest, user: User, db: DatabaseManager) -> Iterator[str]:
    """SSE 事件生成器（同步，由 Starlette 线程池迭代）"""
    agent = ConversationAgent(
        api_key=settings.DEEPSEEK_API_KEY or "",
        base_url=settings.DEEPSEEK_BASE_URL,
        model=settings.CHAT_MODEL,
        max_iterations=settings.AI_MAX_ITERATIONS,
        timeout=settings.AI_TIMEOUT,
    )
    messages = [{"role": m.role, "content": m.content} for m in payload.messages]

    session_id = payload.session_id
    ledger_hint = payload.ledger_id
    if session_id:
        sess = db.get_chat_session(session_id, user.id)
        if not sess:
            yield sse_frame({"type": "error", "message": "会话不存在或无权访问"})
            return
        # 会话一旦绑定账本即锁定：后续查询一律使用该账本，前端传值不再生效
        if sess.ledger_id:
            ledger_hint = sess.ledger_id

    yield sse_frame({"type": "start"})
    try:
        for evt in agent.run_stream(
            messages, user_id=user.id, db=db, ledger_hint=ledger_hint
        ):
            yield sse_frame(evt)
            if evt.get("type") == "done" and session_id:
                _persist_chat(
                    db,
                    session_id,
                    user.id,
                    payload.user_message or "",
                    evt.get("content") or "",
                )
    except GeneratorExit:
        pass  # 客户端断开，静默终止


@router.post("/chat")
def chat(
    payload: AIChatRequest,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db),
):
    """AI 对话流式接口，返回 SSE 事件流：start / tool_call / tool_result / delta / done / error"""
    return StreamingResponse(
        generate_sse(payload, current_user, db),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/sessions", response_model=ResponseModel[List[ChatSessionOut]])
def list_sessions(
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db),
):
    """获取当前用户的会话列表（按最近活动倒序）"""
    sessions = db.list_chat_sessions(current_user.id)
    data = [
        ChatSessionOut(
            id=s["id"],
            title=s["title"],
            ledger_id=s["ledger_id"],
            message_count=s["message_count"],
            created_at=s["created_at"],
            updated_at=s["updated_at"],
        )
        for s in sessions
    ]
    return ResponseModel(code=200, message="success", data=data)


@router.post("/sessions", response_model=ResponseModel[ChatSessionOut])
def create_session(
    payload: ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db),
):
    """新建会话"""
    sid = db.create_chat_session(current_user.id, payload.title, payload.ledger_id)
    sess = db.get_chat_session(sid, current_user.id)
    if not sess:
        raise HTTPException(status_code=500, detail="会话创建失败")
    return ResponseModel(
        code=201,
        message="创建成功",
        data=ChatSessionOut(
            id=sess.id,
            title=sess.title,
            ledger_id=sess.ledger_id,
            message_count=0,
            created_at=sess.created_at,
            updated_at=sess.updated_at,
        ),
    )


@router.get("/sessions/{session_id}/messages", response_model=ResponseModel[List[ChatMessageOut]])
def get_session_messages(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db),
):
    """获取指定会话的全部消息"""
    if not db.get_chat_session(session_id, current_user.id):
        raise HTTPException(status_code=404, detail="会话不存在")
    msgs = db.list_chat_messages(session_id)
    data = [
        ChatMessageOut(id=m.id, role=m.role, content=m.content, created_at=m.created_at)
        for m in msgs
    ]
    return ResponseModel(code=200, message="success", data=data)


@router.delete("/sessions/{session_id}", response_model=ResponseModel[dict])
def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: DatabaseManager = Depends(get_db),
):
    """删除会话及其消息"""
    if not db.delete_chat_session(session_id, current_user.id):
        raise HTTPException(status_code=404, detail="会话不存在")
    return ResponseModel(code=200, message="删除成功", data=None)
