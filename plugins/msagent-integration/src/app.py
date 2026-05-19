#!/usr/bin/env python3
"""Hermes 性能分析平台 — Gradio 前端 (直接调用 LangGraph)"""

import json
import os
import shutil
import uuid

import gradio as gr
import requests
from langchain_core.messages import AIMessage, HumanMessage

from deepseek_setup import setup as _deepseek_setup

_deepseek_setup()  # register deepseek provider + patch ChatDeepSeek

# ── Configuration ────────────────────────────────────────────────────────────
OPENAI_API_URL = os.environ.get("OPENAI_API_BASE", "https://api.deepseek.com/v1")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
UPLOAD_DIR = os.environ.get("UPLOAD_FOLDER", "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

http = requests.Session()
http.headers.update({"User-Agent": "Hermes-Gradio/4.0"})
_graph = None
_graph_cleanup = None


# ── Graph management ─────────────────────────────────────────────────────────
async def _get_graph():
    """Lazily initialize the msagent LangGraph graph in the running event loop."""
    global _graph, _graph_cleanup
    if _graph is not None:
        return _graph
    from msagent.web.runtime import create_web_graph, resolve_web_graph_options

    options = resolve_web_graph_options()
    _graph, _graph_cleanup = await create_web_graph(options)
    return _graph


# ── Graph streaming ──────────────────────────────────────────────────────────
async def _stream_graph(prompt: str, thread_id: str):
    """Yield (reasoning_parts, tool_parts, answer_parts) from the agent graph."""

    from langgraph.types import Command

    g = await _get_graph()
    config = {"configurable": {"thread_id": thread_id}}

    reasoning_parts: list[str] = []
    tool_parts: list[str] = []
    answer_parts: list[str] = []
    current_tool = ""
    last_tool_name = ""

    # Start with the initial input; on interrupt we resume with Command.
    payload: dict | Command = {"messages": [HumanMessage(content=prompt)]}

    while True:
        try:
            async for chunk in g.astream(payload, config, stream_mode="updates"):
                if not isinstance(chunk, dict):
                    continue

                # Auto-resume graph interrupts (execute approval etc.).
                # The web UI has no interactive approval mechanism, so we
                # accept every interrupt with an automatic "approve" decision.
                if "__interrupt__" in chunk:
                    interrupt_info = chunk["__interrupt__"]
                    # LangGraph interrupts arrive as a tuple of Interrupt objects.
                    items = (
                        list(interrupt_info)
                        if hasattr(interrupt_info, "__iter__")
                        and not isinstance(interrupt_info, (str, dict))
                        else [interrupt_info]
                    )
                    auto_decisions = []
                    for slot in items:
                        d = vars(slot) if hasattr(slot, "__dict__") else {}
                        allowed = d.get("allowed_decisions", ["approve"])
                        decision = {"type": (allowed[0] if allowed else "approve")}
                        auto_decisions.append(decision)
                    payload = Command(resume={"decisions": auto_decisions})
                    break  # exit the async-for, loop around with Command

                for _node, val in chunk.items():
                    msgs = val.get("messages") if isinstance(val, dict) else None
                    if msgs is None:
                        continue

                    items = list(msgs) if hasattr(msgs, "__iter__") else [msgs]
                    for msg in items:
                        msg_is_ai = isinstance(msg, AIMessage)
                        tool_calls = getattr(msg, "tool_calls", []) or []

                        # ── Reasoning content (DeepSeek thinking) ────────
                        if msg_is_ai:
                            rc = msg.additional_kwargs.get("reasoning_content")
                            if rc and rc not in reasoning_parts:
                                reasoning_parts.append(rc)

                        # ── Tool calls ───────────────────────────────────
                        for tc in tool_calls:
                            tc_name = tc.get("name", "")
                            if tc_name and tc_name != last_tool_name:
                                last_tool_name = tc_name
                                current_tool = tc_name
                                tool_parts.append(f"🔧 **{tc_name}**")

                        # ── Text content ─────────────────────────────────
                        content = str(getattr(msg, "content", ""))
                        if content:
                            # AIMessage without tool_calls = final answer or
                            # intermediate reasoning; always show as answer.
                            if msg_is_ai and not tool_calls:
                                current_tool = ""
                                answer_parts.append(content)
                            elif current_tool and current_tool != "execute":
                                tool_parts.append(f"```\n{content[:800]}\n```")
                            else:
                                answer_parts.append(content)

                        yield reasoning_parts, tool_parts, answer_parts
            else:
                break  # stream completed without interrupt
        except GeneratorExit:
            break


# ── OpenAI fallback streaming ────────────────────────────────────────────────
async def _stream_openai_wrapped(prompt: str):
    """Async wrapper around the sync OpenAI stream generator."""
    for parts in _stream_openai(prompt):
        yield parts


def _stream_openai(prompt: str):
    """Yield (reasoning_parts, tool_parts, answer_parts) from OpenAI-compatible streaming API."""
    accumulated: list[str] = []

    try:
        with http.post(
            f"{OPENAI_API_URL}/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {OPENAI_API_KEY}",
            },
            json={
                "model": "deepseek-v4-pro",
                "messages": [{"role": "user", "content": prompt}],
                "stream": True,
            },
            stream=True,
            timeout=300,
        ) as resp:
            if resp.status_code != 200:
                yield [], [], [f"❌ API 错误: {resp.status_code}"]
                return

            for line in resp.iter_lines(decode_unicode=True, chunk_size=1024):
                if not line or not line.startswith("data: "):
                    continue
                data = line[6:]
                if data == "[DONE]":
                    break
                try:
                    parsed = json.loads(data)
                    delta = parsed.get("choices", [{}])[0].get("delta", {})
                    content = delta.get("content", "")
                    if content:
                        accumulated.append(content)
                        yield [], [], ["".join(accumulated)]
                except json.JSONDecodeError:
                    continue

    except requests.RequestException as e:
        yield [], [], [f"❌ 连接错误: {e}"]


# ── File handling ────────────────────────────────────────────────────────────
def _save_uploaded(files: list[str] | None) -> list[str]:
    """Copy uploaded temp files to UPLOAD_DIR, return persistent paths."""
    if not files:
        return []
    saved = []
    for src in files:
        if not src:
            continue
        dst = os.path.join(
            UPLOAD_DIR, f"{uuid.uuid4().hex[:8]}_{os.path.basename(src)}"
        )
        shutil.copyfile(src, dst)
        saved.append(os.path.abspath(dst))
    return saved


# ── Gradio event handlers ────────────────────────────────────────────────────
def handle_upload(files):
    """Called when files are dropped/selected in the sidebar."""
    paths = _save_uploaded(files)
    if not paths:
        return paths, "📎 暂无文件"
    return paths, f"📎 已上传 {len(paths)} 个文件"


def user_fn(message: str, history: list, thread_state, file_paths):
    """Instant: append user message, clear input, prepare prompt."""
    if not message.strip() and not file_paths:
        return "", history, thread_state, file_paths, ""

    prompt = message
    if file_paths:
        file_list = "\n".join([f"- {p}" for p in file_paths])
        prompt = f"{message}\n\n--- 附件文件 ---\n{file_list}\n请分析上述文件。"

    display = message.strip() if message.strip() else f"请分析 {len(file_paths)} 个附件"
    history.append({"role": "user", "content": display})
    return "", history, thread_state, file_paths, prompt


async def bot_fn(history: list, thread_state, file_paths, prompt: str):
    """Async generator: stream bot response from LangGraph (or OpenAI fallback)."""
    if not history or not prompt:
        yield history, thread_state
        return

    thread_id = thread_state or str(uuid.uuid4())
    history.append({"role": "assistant", "content": ""})
    yield history, thread_id

    try:
        await _get_graph()
        stream = _stream_graph(prompt, thread_id)
    except Exception:
        stream = _stream_openai_wrapped(prompt)

    try:
        async for reasoning_parts, tool_parts, answer_parts in stream:
            display = _build_display(reasoning_parts, tool_parts, answer_parts)
            history[-1]["content"] = display
            yield history, thread_id
    except GeneratorExit:
        if history[-1]["content"] == "":
            history[-1]["content"] = "⏸ *已停止*"
        yield history, thread_id


def _build_display(
    reasoning_parts: list[str],
    tool_parts: list[str],
    answer_parts: list[str],
) -> str:
    """Build a formatted message with reasoning, tool calls, and final answer."""
    sections: list[str] = []
    if reasoning_parts:
        sections.append("<details open>\n<summary>🧠 深度思考</summary>\n")
        sections.append("\n\n".join(reasoning_parts))
        sections.append("\n</details>")
    if tool_parts:
        sections.append("<details open>\n<summary>🔧 工具调用</summary>\n")
        sections.extend(tool_parts)
        sections.append("\n</details>")
    if answer_parts:
        if reasoning_parts or tool_parts:
            sections.append("\n---\n")
        sections.append("".join(answer_parts))
    return "\n".join(sections) if sections else "🤔 *思考中...*"


def start_new_chat():
    """Reset everything for a new conversation."""
    return [], None, [], "📎 暂无文件"


# ── UI ───────────────────────────────────────────────────────────────────────
_CSS = """
.thinking-details { border: 1px solid #e0e0e0; border-radius: 8px; padding: 8px 12px; margin: 8px 0; }
.thinking-details summary { font-weight: 500; color: #667eea; cursor: pointer; }
footer { display: none !important; }
"""


def build_ui():
    with gr.Blocks(title="Hermes 性能调优平台") as demo:
        thread_state = gr.State(None)
        file_paths_state = gr.State([])
        prompt_state = gr.State("")

        gr.Markdown("# 🤖 Hermes 性能调优平台")

        with gr.Row():
            with gr.Column(scale=1, elem_id="sidebar"):
                gr.Markdown("### 📎 附件文件")
                file_upload = gr.File(
                    label="拖拽或点击上传",
                    file_count="multiple",
                    file_types=[".csv", ".json", ".db", ".txt", ".log"],
                )
                upload_status = gr.Markdown("📎 暂无文件")
                new_chat_btn = gr.Button("🔄 新对话", variant="secondary", size="sm")

            with gr.Column(scale=4):
                chatbot = gr.Chatbot(
                    label="对话",
                    height=600,
                    placeholder="欢迎使用 Hermes 性能分析平台。上传数据文件，输入分析指令即可开始。",
                )
                with gr.Row():
                    msg = gr.Textbox(
                        label="",
                        placeholder="输入指令，例如：分析这个性能数据，找出瓶颈...",
                        scale=9,
                        container=False,
                    )
                    send_btn = gr.Button("发送", variant="primary", scale=1)

        # ── Event wiring ──

        file_upload.change(
            handle_upload, [file_upload], [file_paths_state, upload_status]
        )

        gr.on(
            [msg.submit, send_btn.click],
            user_fn,
            [msg, chatbot, thread_state, file_paths_state],
            [msg, chatbot, thread_state, file_paths_state, prompt_state],
            queue=False,
        ).then(
            bot_fn,
            [chatbot, thread_state, file_paths_state, prompt_state],
            [chatbot, thread_state],
        )

        new_chat_btn.click(
            start_new_chat,
            None,
            [chatbot, thread_state, file_paths_state, upload_status],
            queue=False,
        )

    return demo


# ── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    demo = build_ui()
    demo.launch(
        server_name="0.0.0.0",
        server_port=8082,
        theme=gr.themes.Soft(primary_hue="purple"),
        css=_CSS,
        show_error=True,
    )
