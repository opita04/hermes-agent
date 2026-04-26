
## 2026-04-23 Hermes Gateway / Codex Streaming Fix

Context:
- Gateway was repeatedly crashing or failing to answer after update/restart work.
- `hermes update` exists and was run. It initially failed because Windows-reserved/untracked `NUL` plus locked `.claude` / `.nanostack` paths blocked autostash/ZIP fallback.
- `NUL` was deleted. `.claude` and `.nanostack` were temporarily moved out of the repo during update, then restored.
- Update completed successfully and reported `Already up to date!`.

Local fixes applied:
- `gateway/status.py`: Windows stale PID handling now treats `os.kill(pid, 0)` `OSError` variants with `winerror` 11 or 87 as stale PID records and removes the pid file instead of crashing startup.
- `gateway/status.py`: scoped lock handling had already been adjusted similarly for stale/invalid Windows PIDs.
- `gateway/platforms/discord.py`: Discord message handling was changed to schedule `_handle_message(message)` as a background task instead of awaiting inline, preventing long agent turns from starving Discord heartbeat.
- `run_agent.py`: Codex Responses streaming path now collects `response.output_item.done` items from stream events and restores them onto the final response if `stream.get_final_response()` returns an empty `output` list.

Root cause of `Empty/malformed response`:
- Codex was not actually failing to generate text.
- A direct stream probe showed `response.output_text.delta` contained `OK` and `response.output_text.done` contained `OK`.
- However, the OpenAI SDK final object from `stream.get_final_response()` had `output_len: 0` and `output_text: ""`.
- Hermes validated the final empty object, discarded the streamed text/items, and emitted `Empty/malformed response`.
- Fixing `run_agent.py` to preserve completed streamed output items resolved the bot replies while keeping provider `openai-codex`.

Current runtime/config notes:
- Provider should remain `openai-codex`, not Anthropic.
- Model was temporarily changed from `gpt-5.5` to `gpt-5.4` during debugging, then changed back to `gpt-5.5` after the streaming fix.
- Gateway launch command used successfully:
  `venv\Scripts\pythonw.exe -m hermes_cli.main gateway run --replace`
- If gateway appears running but does not answer, check real processes instead of trusting stale `gateway_state.json`:
  `Get-CimInstance Win32_Process | Where-Object { $_.Name -in @('pythonw.exe','python.exe') -and $_.CommandLine -like '*hermes*gateway*' }`

Important backups/stashes created during this work:
- Config backup before temporary Anthropic switch: `C:\Users\Jaime Bohl\.hermes\config.yaml.bak-20260423-192618`
- Config backup before switching to gpt-5.4: `C:\Users\Jaime Bohl\.hermes\config.yaml.bak-before-gpt54-20260423-193026`
- Config backup before switching back to gpt-5.5: `C:\Users\Jaime Bohl\.hermes\config.yaml.bak-before-gpt55-20260423-193453`
- Updater stash examples from this session: `hermes-update-autostash-20260424-015430`, `hermes-update-autostash-20260424-020825`
