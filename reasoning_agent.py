import asyncio
import json
from typing import Optional
from datetime import datetime
from zoneinfo import ZoneInfo

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage, AIMessage
from langchain.agents import create_agent
from tools import (
    normal_chat,
    generate_chart,
    get_current_time,
    generate_files_with_python_code,
    # generate_pdf_file,
    generate_html_code,
)

stop = False

messages = []


llm = ChatOllama(
    model="gemma4:e2b",
    # model="gemma3:latest",
    # model="deepseek-coder:6.7b",
    temperature=1.0,
    top_p=0.95,
    reasoning=True,
    top_k=64,
)


async def initAgent():
    agent = create_agent(
        llm,
        tools=[
            get_current_time,
            normal_chat,
            generate_chart,
            generate_files_with_python_code,
            # generate_pdf_file,
            generate_html_code,
        ],
        middleware=[],
        system_prompt=SystemMessage(
            content="You are a help full ai agent. Use tools when needed. Never output tool calls as text.\n\n"
        ),
    )

    return agent


async def requestLLM(prompt: str):
    try:
        messages.append(HumanMessage(content=prompt))
        tool = ""
        full_response = ""
        agent = await initAgent()

        async for chunk, metadata in agent.astream(
            {"messages": messages}, stream_mode="messages"
        ):
            if chunk.type == "AIMessageChunk":
                if (
                    hasattr(chunk, "additional_kwargs")
                    and "reasoning_content" in chunk.additional_kwargs
                ):
                    yield json.dumps(
                        {
                            "status": "reasoning",
                            "type": "status",
                            "reasoning": chunk.additional_kwargs["reasoning_content"],
                        }
                    ) + "\n"
                if chunk.tool_calls:
                    tool = (chunk.tool_calls,)
                    yield json.dumps({"type": "tool", "status": "calling_tool"}) + "\n"
                    yield json.dumps(
                        {
                            "type": "tool",
                            "status": "calling_tool",
                            "content": tool,
                        }
                    ) + "\n"
                if chunk.content:
                    yield json.dumps({"type": "status", "status": "responding"}) + "\n"

                    yield json.dumps(
                        {
                            "message": chunk.content,
                            "type": "message",
                            "status": "replying",
                            "content": tool,
                        }
                    ) + "\n"

            full_response += chunk.content or ""

        yield json.dumps(
            {"type": "message", "status": "finished", "content": tool}
        ) + "\n"
        messages.append(AIMessage(content=full_response))
    except Exception as e:
        print(str(e))
