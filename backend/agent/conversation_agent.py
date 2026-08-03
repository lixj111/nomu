"""AI 对话智能体：工具调用循环 + 流式事件输出"""
import json
from datetime import datetime, timedelta
from typing import Iterator, Optional

from openai import OpenAI

from .tools import TOOLS, execute_tool, summarize_tool_result


SYSTEM_PROMPT = """你是"智账"记账应用的 AI 分析助手，帮助用户理解消费、分析趋势并给出建议。

【工具使用】
- 需要数据时，必须先调用工具获取真实数据，禁止编造数字。
- 账本范围：如果系统注入了【当前账本】，直接使用该账本ID，不要重复调用 list_ledgers；仅当用户明确要求查看其他账本时，才调用 list_ledgers 查找并切换。
- 用户未指定时间范围时：默认取最近 30 天，并在回答中说明该假设。
- 一次回答只需调用 3~5 次工具拿到核心数据（收支概况、分类、趋势）即可，拿到后立即停止调用工具并组织回答。
- 禁止对同一工具使用完全相同的参数重复调用；若某次查询结果为空或数据很少，如实向用户说明并给出建议即可，不要反复扩大范围翻找数据。
- 若当前账本没有足够数据，直接说明该情况并结束，不要再尝试其他工具。

【回答组织】按以下顺序组织分析：
1. 消费概况（总收入、总支出、结余）
2. 分类占比 / 主要花销
3. 趋势变化
4. 异常或值得注意的点
5. 可执行的建议

【其他】用中文回答，语言简洁口语化；结论仅依据工具返回的数据。"""


class ConversationAgent:
    """对话智能体，单次请求内执行工具调用循环并产出 SSE 事件"""

    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        max_iterations: int = 5,
        timeout: float = 120.0,
    ):
        self.client = OpenAI(api_key=api_key, base_url=base_url, timeout=timeout)
        self.model = model
        self.max_iterations = max_iterations

    def run_stream(
        self,
        messages: list,
        user_id: int,
        db,
        ledger_hint: Optional[int] = None,
    ) -> Iterator[dict]:
        """逐事件产出：tool_call / tool_result / delta / done / error

        采用真流式（stream=True）：最终回答按 token 实时下发形成打字机效果；
        工具调用阶段则流式组装 tool_calls 分片后执行，循环至模型给出最终回答。
        """
        msgs = self._build_messages(messages, ledger_hint)
        try:
            for _ in range(self.max_iterations):
                content_parts = []
                tool_calls_map = {}

                stream = self.client.chat.completions.create(  # type: ignore[call-overload]
                    model=self.model,
                    messages=msgs,
                    tools=TOOLS,
                    stream=True,
                    tool_choice="auto",
                )
                for chunk in stream:
                    if not chunk.choices:
                        continue
                    choice = chunk.choices[0]
                    delta = choice.delta
                    # 推理模型先输出 reasoning_content：实时下发思考过程，避免正文前的长时间空白
                    if getattr(delta, "reasoning_content", None):
                        yield {"type": "thinking", "content": delta.reasoning_content}
                    # 最终回答文本：逐 token 实时下发，形成打字机效果
                    if getattr(delta, "content", None):
                        content_parts.append(delta.content)
                        yield {"type": "delta", "content": delta.content}
                    # 工具调用：流式分片按 index 合并
                    if getattr(delta, "tool_calls", None):
                        for tc in delta.tool_calls:
                            idx = tc.index if tc.index is not None else len(tool_calls_map)
                            slot = tool_calls_map.setdefault(
                                idx, {"id": "", "name": "", "arguments": ""}
                            )
                            if tc.id:
                                slot["id"] = tc.id
                            if tc.function:
                                if tc.function.name:
                                    slot["name"] += tc.function.name
                                if tc.function.arguments:
                                    slot["arguments"] += tc.function.arguments

                content = "".join(content_parts)

                # 本轮无工具调用 → 最终回答已流式输出完毕
                if not tool_calls_map:
                    yield {"type": "done", "content": content}
                    return

                # 本轮是工具调用：回填 assistant 消息并依次执行
                assembled = list(tool_calls_map.values())
                msgs.append(
                    {
                        "role": "assistant",
                        "content": content or None,
                        "tool_calls": [
                            {
                                "id": t["id"],
                                "type": "function",
                                "function": {"name": t["name"], "arguments": t["arguments"]},
                            }
                            for t in assembled
                        ],
                    }
                )
                for t in assembled:
                    fn_name = t["name"]
                    try:
                        result = execute_tool(fn_name, t["arguments"], db, user_id)
                        ok = True
                        summary = summarize_tool_result(fn_name, result)
                    except Exception as e:
                        result = {"error": str(e)}
                        ok = False
                        summary = f"执行失败：{e}"
                    yield {"type": "tool_call", "tool": fn_name, "args": self._parse_args(t["arguments"])}
                    yield {"type": "tool_result", "tool": fn_name, "ok": ok, "summary": summary}
                    msgs.append(
                        {
                            "role": "tool",
                            "tool_call_id": t["id"],
                            "content": json.dumps(result, ensure_ascii=False),
                        }
                    )

            yield {"type": "error", "message": "工具调用轮数已达上限，请缩小问题范围后重试。"}
        except Exception as e:
            yield {"type": "error", "message": f"AI 调用失败：{e}"}

    def _build_messages(self, messages: list, ledger_hint: Optional[int]) -> list:
        today = datetime.now()
        today_str = today.strftime("%Y-%m-%d")
        month_start = today.replace(day=1).strftime("%Y-%m-%d")
        next_month_start = (today.replace(day=28) + timedelta(days=4)).replace(day=1)
        last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        days_ago_30 = (today - timedelta(days=30)).strftime("%Y-%m-%d")

        date_hint = (
            f"\n【当前日期】今天是 {today_str}。"
            f"\"这个月/本月\"指 {today.strftime('%Y年%m月')}（{month_start} ~ {today_str}）；"
            f"\"上个月\"指 {last_month_start.strftime('%Y-%m-%d')} ~ {month_start}；"
            f"\"最近30天\"指 {days_ago_30} ~ {today_str}；"
            f"\"下个月\"指 {next_month_start.strftime('%Y-%m-%d')} 开始。"
            f"涉及\"今年/去年/近N天/近N个月\"时请据此推算起始日期。"
        )
        system_content = SYSTEM_PROMPT + date_hint
        if ledger_hint:
            system_content += (
                f"\n【当前账本】用户当前选择的分析账本ID为 {ledger_hint}。"
                f"所有查询工具默认使用该账本ID；仅当用户明确要求查看其他账本时，才调用 list_ledgers 查找。"
            )
        msgs = [{"role": "system", "content": system_content}]
        for m in messages:
            item = {"role": m.get("role", "user"), "content": m.get("content", "")}
            if m.get("name"):
                item["name"] = m["name"]
            msgs.append(item)
        return msgs

    @staticmethod
    def _parse_args(arguments: str) -> dict:
        try:
            return json.loads(arguments) if arguments else {}
        except Exception:
            return {"raw": arguments}
