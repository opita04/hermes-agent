@echo off
cd /d "C:\AI\Agents\hermes-agent-clean"
"C:\AI\Agents\hermes-agent-clean\.venv\Scripts\python.exe" -m acp_adapter.entry %*
