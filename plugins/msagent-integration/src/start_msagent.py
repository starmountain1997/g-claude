#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import os
import sys
from pathlib import Path

# OPENAI_API_KEY is loaded from .env by start.sh or should be set in the environment

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from msagent.web.launcher import launch_langgraph_dev_server


async def main():
    working_dir = Path.cwd()
    await launch_langgraph_dev_server(
        host="127.0.0.1",
        port=2026,
        ui_port=3000,
        start_ui=False,
        open_browser_on_start=False,
        working_dir=working_dir,
        agent=None,
        model=None,
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")
