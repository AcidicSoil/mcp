# Project Structure and Setup

**Created:** 6/13/2025 12:56  
**Updated:** 6/13/2025 13:05  
**Exported:** 6/13/2025 13:06

## Response:

```text
# Project layout — minimal but extensible
my-local-agent/
├─ README.md
├─ requirements.txt
├─ .env.template
├─ agent/
│   ├─ __init__.py
│   ├─ config.py          # Pydantic settings loader
│   ├─ main.py            # the ReAct + tool-calling loop
│   ├─ tools/
│   │   ├─ __init__.py
│   │   ├─ python_exec.py # sandboxed code runner
│   │   ├─ git_status.py  # readonly Git helper
│   │   └─ web_search.py  # DuckDuckGo search wrapper
│   └─ sandbox/
│       └─ Dockerfile     # non-root, no network
└─ tests/
    └─ test_tools.py
```

```text
# requirements.txt
openai>=1.30          # works with LM Studio endpoint
litellm>=1.36         # faster streaming wrapper (optional)
pydantic>=2.7
python-dotenv>=1.0
duckduckgo-search>=4  # simple web search
pytest>=8
```

```dotenv
# .env.template  — copy to .env and tweak values
OPENAI_API_BASE=http://localhost:1234/v1
OPENAI_API_KEY=local-key-or-dummy
MODEL_NAME=lmstudio-community/qwen3-7b-instruct
MAX_ITERATIONS=6
DEBUG=1
PY_EXEC_TIMEOUT=15      # seconds
ALLOWED_SHELL_CMDS=git\ status,ls,cat
```

```python
# agent/config.py
from pydantic import BaseSettings, Field
from pathlib import Path

class Settings(BaseSettings):
    api_base: str = Field(..., env="OPENAI_API_BASE")
    api_key: str = Field(..., env="OPENAI_API_KEY")
    model: str    = Field(..., env="MODEL_NAME")
    max_iter: int = Field(6, env="MAX_ITERATIONS")
    debug: bool   = Field(False, env="DEBUG")
    py_timeout: int = Field(15, env="PY_EXEC_TIMEOUT")
    allowed_cmds: str = Field("git status,ls,cat", env="ALLOWED_SHELL_CMDS")

    @property
    def allowed_list(self) -> set[str]:
        return {c.strip() for c in self.allowed_cmds.split(",")}

settings = Settings(_env_file=Path(__file__).resolve().parent.parent / ".env")
```

```python
# agent/tools/python_exec.py
import subprocess, json, shlex, tempfile, os, textwrap, contextlib, signal
from agent.config import settings

SCHEMA = {
    "name": "python_exec",
    "description": "Run short Python snippets in a sandboxed Docker container",
    "parameters": {
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Python code"},
        },
        "required": ["code"]
    },
}

def run(args: dict) -> str:
    code = textwrap.dedent(args["code"])
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as tf:
        tf.write(code)
        tf.flush()
        cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "256m",
            "-v", f"{tf.name}:/tmp/code.py:ro",
            "python:3.12-alpine",
            "python", "/tmp/code.py"
        ]
        try:
            out = subprocess.check_output(
                cmd, text=True, timeout=settings.py_timeout
            )
            return out[:4_000]   # trim to save tokens
        except subprocess.CalledProcessError as e:
            return f"ERROR: {e.stdout}{e.stderr}"
        except subprocess.TimeoutExpired:
            return "ERROR: execution timed-out"
```

```python
# agent/main.py
#!/usr/bin/env python3
from openai import OpenAI
from agent.config import settings
from agent.tools import python_exec, git_status, web_search

TOOLS = [t.SCHEMA for t in (python_exec, git_status, web_search)]
TOOL_MAP = {s["name"]: mod for s, mod in [
    (python_exec.SCHEMA, python_exec),
    (git_status.SCHEMA,  git_status),
    (web_search.SCHEMA,  web_search),
]}

client = OpenAI(base_url=settings.api_base, api_key=settings.api_key)
history = [{"role": "system", "content": "You are an efficient DevOps assistant."}]

def call_llm(messages, tools=None, stream=False):
    return client.chat.completions.create(
        model=settings.model,
        messages=messages,
        tools=tools,
        stream=stream,
    )

def main():
    user_prompt = input("❯ ")
    history.append({"role": "user", "content": user_prompt})

    for _ in range(settings.max_iter):
        resp = call_llm(history, tools=TOOLS)
        msg = resp.choices[0].message

        # 1) Did the model ask to call a tool?
        if msg.tool_calls:
            for tc in msg.tool_calls:
                name = tc.function.name
                args = tc.function.arguments
                result = TOOL_MAP[name].run(args)  # execute securely

                history.extend([
                    {"role": "assistant", "tool_call_id": tc.id, **tc.to_dict()},
                    {"role": "tool", "tool_call_id": tc.id, "content": result},
                ])
            # loop again so model can incorporate tool output
            continue

        # 2) Final answer – stream it
        final = call_llm(history, tools=None, stream=True)
        for chunk in final:
            print(chunk.choices[0].delta.content or "", end="", flush=True)
        print()
        break
    else:
        print("⛔ Max iterations reached — aborting.")

if __name__ == "__main__":
    main()
```

## Response:

```text
# Project layout — minimal but extensible
my-local-agent/
├─ README.md
├─ requirements.txt
├─ .env.template
├─ agent/
│   ├─ __init__.py
│   ├─ config.py          # Pydantic settings loader
│   ├─ main.py            # the ReAct + tool-calling loop
│   ├─ tools/
│   │   ├─ __init__.py
│   │   ├─ python_exec.py # sandboxed code runner
│   │   ├─ git_status.py  # readonly Git helper
│   │   └─ web_search.py  # DuckDuckGo search wrapper
│   └─ sandbox/
│       └─ Dockerfile     # non-root, no network
└─ tests/
    └─ test_tools.py
```

```text
# requirements.txt
openai>=1.30          # works with LM Studio endpoint
litellm>=1.36         # faster streaming wrapper (optional)
pydantic>=2.7
python-dotenv>=1.0
duckduckgo-search>=4  # simple web search
pytest>=8
```

```dotenv
# .env.template  — copy to .env and tweak values
OPENAI_API_BASE=http://localhost:1234/v1
OPENAI_API_KEY=local-key-or-dummy
MODEL_NAME=lmstudio-community/qwen3-7b-instruct
MAX_ITERATIONS=6
DEBUG=1
PY_EXEC_TIMEOUT=15      # seconds
ALLOWED_SHELL_CMDS=git\ status,ls,cat
```

```python
# agent/config.py
from pydantic import BaseSettings, Field
from pathlib import Path

class Settings(BaseSettings):
    api_base: str = Field(..., env="OPENAI_API_BASE")
    api_key: str = Field(..., env="OPENAI_API_KEY")
    model: str    = Field(..., env="MODEL_NAME")
    max_iter: int = Field(6, env="MAX_ITERATIONS")
    debug: bool   = Field(False, env="DEBUG")
    py_timeout: int = Field(15, env="PY_EXEC_TIMEOUT")
    allowed_cmds: str = Field("git status,ls,cat", env="ALLOWED_SHELL_CMDS")

    @property
    def allowed_list(self) -> set[str]:
        return {c.strip() for c in self.allowed_cmds.split(",")}

settings = Settings(_env_file=Path(__file__).resolve().parent.parent / ".env")
```

```python
# agent/tools/python_exec.py
import subprocess, textwrap, tempfile
from agent.config import settings

SCHEMA = {
    "name": "python_exec",
    "description": "Run short Python snippets in a sandboxed Docker container",
    "parameters": {
        "type": "object",
        "properties": {
            "code": {"type": "string", "description": "Python code"},
        },
        "required": ["code"]
    },
}

def run(args: dict) -> str:
    code = textwrap.dedent(args["code"])
    with tempfile.NamedTemporaryFile("w", delete=False, suffix=".py") as tf:
        tf.write(code)
        tf.flush()
        cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "256m",
            "-v", f"{tf.name}:/tmp/code.py:ro",
            "python:3.12-alpine",
            "python", "/tmp/code.py"
        ]
        try:
            out = subprocess.check_output(
                cmd, text=True, timeout=settings.py_timeout
            )
            return out[:4_000]   # trim to save tokens
        except subprocess.CalledProcessError as e:
            return f"ERROR: {e.stdout}{e.stderr}"
        except subprocess.TimeoutExpired:
            return "ERROR: execution timed-out"
```

```python
# agent/main.py
#!/usr/bin/env python3
from openai import OpenAI
from agent.config import settings
from agent.tools import python_exec, git_status, web_search

TOOLS = [t.SCHEMA for t in (python_exec, git_status, web_search)]
TOOL_MAP = {s["name"]: mod for s, mod in [
    (python_exec.SCHEMA, python_exec),
    (git_status.SCHEMA,  git_status),
    (web_search.SCHEMA,  web_search),
]}

client = OpenAI(base_url=settings.api_base, api_key=settings.api_key)
history = [{"role": "system", "content": "You are an efficient DevOps assistant."}]

def call_llm(messages, tools=None, stream=False):
    return client.chat.completions.create(
        model=settings.model,
        messages=messages,
        tools=tools,
        stream=stream,
    )

def main():
    user_prompt = input("❯ ")
    history.append({"role": "user", "content": user_prompt})

    for _ in range(settings.max_iter):
        resp = call_llm(history, tools=TOOLS)
        msg = resp.choices[0].message

        # 1) Did the model ask to call a tool?
        if msg.tool_calls:
            for tc in msg.tool_calls:
                name = tc.function.name
                args = tc.function.arguments
                result = TOOL_MAP[name].run(args)  # execute securely

                history.extend([
                    {"role": "assistant", "tool_call_id": tc.id, **tc.to_dict()},
                    {"role": "tool", "tool_call_id": tc.id, "content": result},
                ])
            continue  # loop again so model can incorporate tool output

        # 2) Final answer – stream it
        final = call_llm(history, tools=None, stream=True)
        for chunk in final:
            print(chunk.choices[0].delta.content or "", end="", flush=True)
        print()
        break
    else:
        print("⛔ Max iterations reached — aborting.")

if __name__ == "__main__":
    main()
```

```python
# Qwen-Agent: register a custom Git tool
from qwen_agent.tool import register_tool, BaseTool
import subprocess, json5

@register_tool('git_status')
class GitStatus(BaseTool):
    description = 'Return clean/dirty git tree summary'
    parameters = [{'name': 'path', 'type': 'string', 'required': False}]

    def call(self, params, **_):
        path = json5.loads(params).get('path', '.')
        status = subprocess.check_output(['git', 'status', '-s', path]).decode()
        return json5.dumps({'status': status})
```

```python
# llm_cfg example for LM Studio endpoint
llm_cfg = {
    'model': 'Qwen3-7B-Instruct',
    'model_server': 'http://localhost:1234/v1',  # LM Studio default port
    'api_key': 'EMPTY',
    'generate_cfg': {'top_p': 0.8}
}
```

```bash
# Running Qwen3 locally — choose one backend
# 1) LM Studio GUI
lmstudio serve -m Qwen3-7B-Instruct -p 1234

# 2) vLLM
python -m vllm.entrypoints.openai.api_server \
  --model Qwen3-7B-Instruct \
  --port 1234 \
  --enable-reasoning --reasoning-parser deepseek_r1

# 3) Ollama
OLLAMA_ORIGINS=http://127.0.0.1:1234 ollama serve &
ollama pull qwen3
```

```bash
# MCP TypeScript SDK quick start
npm i -g @modelcontextprotocol/sdk
mcp-server-sqlite --db-path my.db
```

```ts
// Example MCP tool (TypeScript)
server.tool("query", { sql: z.string() }, async ({ sql }) => {
  /* run the query and return JSON rows */
});
```

```python
# Connecting Qwen-Agent to an MCP SQLite server
bot = Assistant(
    llm=llm_cfg,
    mcp_servers={'sqlite': 'http://localhost:8080'},
    function_list=['code_interpreter']  # plus any local tools
)
```

```text
# Suggested repo layout for custom tools
repo-root/
├─ codex_local_shell_bridge.py
├─ tools/
│   ├─ __init__.py
│   ├─ python_exec.py
│   ├─ git_status.py
│   ├─ file_edit.py
│   └─ … additional tools …
└─ tests/
    └─ test_tools.py
```

```bash
# Install Qwen-Agent with all extras
pip install -U "qwen-agent[gui,rag,code_interpreter,mcp]"
```

```bash
# Validate end-to-end
echo "What’s the row count of users and how many lines did I change in Git?" | \
python codex_local_shell_bridge.py
```

---

Powered by [ChatGPT Exporter](https://www.chatgptexporter.com)
