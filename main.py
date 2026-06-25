"""
Classroom Exam Agent — Main Entry Point
Starts the MCP server and the UI.
Each team can also run their part independently.
"""
import threading
from config.settings import MCP_HOST, MCP_PORT, UI_PORT
from mcp_server.server import start_mcp_server


def run_mcp():
    start_mcp_server(host=MCP_HOST, port=MCP_PORT)


def run_ui():
    import subprocess
    import sys
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", "ui/app.py",
        "--server.port", str(UI_PORT)
    ])


if __name__ == "__main__":
    # start MCP server in background thread
    mcp_thread = threading.Thread(target=run_mcp, daemon=True)
    mcp_thread.start()
    print(f"MCP server started on {MCP_HOST}:{MCP_PORT}")

    # start UI in main thread
    run_ui()