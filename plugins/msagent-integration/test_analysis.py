#!/usr/bin/env python3
"""End-to-end test: verify performance analysis with interrupt resume."""

import asyncio, json, os, sys, time

os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, "src")

from deepseek_setup import setup as _deepseek_setup

_deepseek_setup()

from langgraph.types import Command
from langchain_core.messages import HumanMessage, AIMessage
from msagent.web.runtime import resolve_web_graph_options, create_web_graph

FILE = "uploads/1a46c757_operator_details.csv"


async def run(prompt: str):
    opts = resolve_web_graph_options()
    g, cleanup = await create_web_graph(opts)

    config = {"configurable": {"thread_id": f"test-{int(time.time())}"}}

    reasoning_parts = []
    tool_parts = []
    answer_parts = []
    current_tool = ""
    last_tool_name = ""
    interrupts = 0

    payload: dict | Command = {"messages": [HumanMessage(content=prompt)]}

    try:
        while True:
            try:
                async for chunk in g.astream(payload, config, stream_mode="updates"):
                    if not isinstance(chunk, dict):
                        continue

                    if "__interrupt__" in chunk:
                        interrupts += 1
                        interrupt_info = chunk["__interrupt__"]
                        print(f"\n⏸  interrupt #{interrupts}")
                        print(f"   interrupt_info type={type(interrupt_info).__name__}")

                        auto_decisions = []
                        items = list(interrupt_info) if hasattr(interrupt_info, "__iter__") else [interrupt_info]
                        for i, slot in enumerate(items):
                            if hasattr(slot, "__dict__"):
                                d = vars(slot).copy()
                            elif isinstance(slot, dict):
                                d = dict(slot)
                            else:
                                d = {}
                            print(f"   slot[{i}]: {json.dumps({k: str(v)[:200] for k, v in d.items()}, ensure_ascii=False)}")
                            # Build a valid decision
                            decision = {"type": "approve"}
                            if isinstance(d.get("allowed_decisions"), list) and d["allowed_decisions"]:
                                decision["type"] = d["allowed_decisions"][0]
                            auto_decisions.append(decision)

                        print(f"   → resume with: {auto_decisions}")
                        payload = Command(resume={"decisions": auto_decisions})
                        break

                    for _node, val in chunk.items():
                        msgs = val.get("messages") if isinstance(val, dict) else None
                        if msgs is None:
                            continue

                        items = list(msgs) if hasattr(msgs, "__iter__") else [msgs]
                        for msg in items:
                            msg_is_ai = isinstance(msg, AIMessage)
                            tool_calls = getattr(msg, "tool_calls", []) or []

                            if msg_is_ai:
                                rc = msg.additional_kwargs.get("reasoning_content")
                                if rc and rc not in reasoning_parts:
                                    reasoning_parts.append(rc)

                            for tc in tool_calls:
                                tc_name = tc.get("name", "")
                                if tc_name and tc_name != last_tool_name:
                                    last_tool_name = tc_name
                                    current_tool = tc_name
                                    tool_parts.append(f"🔧 {tc_name}")
                                    print(f"  🔧 {tc_name}")

                            content = str(getattr(msg, "content", ""))
                            if content:
                                if msg_is_ai and not tool_calls:
                                    current_tool = ""
                                    answer_parts.append(content)
                                    print(f"  🤖 [{len(''.join(answer_parts))} chars]")
                                elif current_tool and current_tool != "execute":
                                    tool_parts.append(content[:200])
                                    print(f"  📦 tool output ({len(content)} chars)")
                                elif current_tool == "execute":
                                    answer_parts.append(content)
                                    print(f"  🐍 execute output ({len(content)} chars)")
                else:
                    break  # no interrupt, stream completed
            except GeneratorExit:
                break
    finally:
        await cleanup()

    return reasoning_parts, tool_parts, answer_parts, interrupts


async def main():
    t0 = time.time()
    print("=" * 60)
    print(f"分析文件: {FILE}")
    print("=" * 60)

    prompt = f"请用 msprof-mcp 工具读取 {FILE}，找出 Device Total Duration 最高的 TOP 3 算子并给出简要建议。"

    reasoning, tools, answer, interrupts = await run(prompt)

    elapsed = time.time() - t0
    print("\n" + "=" * 60)
    print(f"耗时 {elapsed:.0f}s  |  中断 {interrupts}  |  最终回答 {len(''.join(answer))} chars")
    print("=" * 60)
    ans = "".join(answer)
    if ans:
        print(ans[:3000])
    else:
        print("(回答为空)")
        print("\n工具片段:", "".join(tools)[:500])


if __name__ == "__main__":
    asyncio.run(main())
