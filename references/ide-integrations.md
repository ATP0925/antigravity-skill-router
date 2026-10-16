# 🌐 Universal IDE & Editor Integration Guide

**Skill Router** is built from the ground up to be **100% universal and platform-agnostic**. It works seamlessly across any modern AI code editor, agentic CLI, IDE, or terminal environment.

---

## 🧭 Multi-IDE Compatibility Matrix

| IDE / Code Editor / Agent Tool | Support Status | Integration Mechanism | Configuration File |
| :--- | :---: | :--- | :--- |
| **Google Antigravity IDE** | 🟢 Native | Automatic skill discovery & chat badges | `SKILL.md` in `~/.gemini/config/skills` or `.agents/skills` |
| **Anthropic Claude Code CLI** | 🟢 Native | Skill tool / Bash CLI hook | `~/.claude/skills` or `.claude/CLAUDE.md` |
| **Cursor AI Editor** | 🟢 Full | Agent rules & CLI routing | `.cursorrules` or `.cursor/rules` |
| **Windsurf (Codeium Cascade)** | 🟢 Full | Cascade agent rules & CLI | `.windsurfrules` |
| **VS Code (Copilot / Cline / Roo)** | 🟢 Full | Copilot instructions / Cline custom tools | `.github/copilot-instructions.md` / `.vscode/` |
| **JetBrains IDEs (IntelliJ, PyCharm)** | 🟢 Full | Terminal tool & Junie / AI Assistant prompt | Terminal tool `skill-hub` |
| **Neovim (Avante.nvim, CopilotChat)** | 🟢 Full | CLI integration & system commands | Lua `vim.fn.system('py skill_hub.py ...')` |
| **Terminal / CLI (Bash, Zsh, PowerShell)**| 🟢 Native | Direct shell executable | `./scripts/skill-hub.sh` or `.\scripts\skill-hub.ps1` |
| **CI / CD (GitHub Actions, GitLab CI)** | 🟢 Native | Automated PR intent verification | `python scripts/skill_hub.py lint` & `test` |

---

## 🚀 One-Command Adapter Generator

Generate ready-to-use configuration files for your editor in 1 second:

```bash
# For Cursor AI
python scripts/skill_hub.py export cursor

# For Windsurf Cascade
python scripts/skill_hub.py export windsurf

# For Anthropic Claude Code
python scripts/skill_hub.py export claude

# For Universal Multi-Agent standard (AGENTS.md)
python scripts/skill_hub.py export agents

# For GitHub Copilot Workspace
python scripts/skill_hub.py export copilot
```

---

## 🛠️ Detailed Setup by Environment

### 1. Google Antigravity IDE
- **Discovery**: Automatically picks up `SKILL.md` from:
  - Global: `~/.gemini/config/skills/skill-router`
  - Workspace: `.agents/skills/skill-router`
- **Behavior**: Auto-activates on user prompt, displays visual badge `> 🧭 [Skill Router] ➔ Activated Skill: ...`, and reads instructions.

### 2. Anthropic Claude Code (`claude`)
- **Global Install**:
  ```bash
  # Symlink or clone into Claude skills
  git clone https://github.com/ATP0925/antigravity-skill-router.git ~/.claude/skills/skill-router
  ```
- **CLI Invocations**:
  Use `./scripts/skill-hub.sh route "<prompt>"` from terminal or inside Claude Code bash commands.
- **Project Rule**: Run `python scripts/skill_hub.py export claude` to create `.claude/CLAUDE.md`.

### 3. Cursor AI (`.cursorrules`)
- Run `python scripts/skill_hub.py export cursor` to create `.cursorrules` in your project root.
- In Cursor Agent Mode (Ctrl+L / Cmd+L), Cursor will automatically inspect `scripts/skill_hub.py` before executing tasks.
- If you keep custom skills in `.cursor/skills/`, `build-index.py` automatically indexes them!

### 4. Windsurf Cascade (`.windsurfrules`)
- Run `python scripts/skill_hub.py export windsurf` to create `.windsurfrules`.
- Cascade will leverage `skill_hub.py` to route queries and detect multi-skill pipelines.
- Supports `.windsurf/skills/` workspace directory out-of-the-box.

### 5. VS Code with GitHub Copilot / Cline / Roo Code
- **For GitHub Copilot**:
  Run `python scripts/skill_hub.py export copilot`. Creates `.github/copilot-instructions.md`.
- **For Cline / Roo Code**:
  Cline detects skills inside `.agents/skills/` or `.vscode/skills/`.
  Add a custom tool or task prompt pointing to `py scripts/skill_hub.py route`.

### 6. JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm, GoLand)
- Open **Settings ➔ Tools ➔ External Tools**.
- Add tool:
  - **Name**: `Skill Router`
  - **Program**: `python` (or `py`)
  - **Arguments**: `scripts/skill_hub.py route "$Prompt$"`
  - **Working Directory**: `$ProjectFileDir$`
- You can now assign a hotkey (e.g. `Alt+Shift+S`) to route any selected text or prompt.

### 7. Neovim (Avante.nvim / CodeCompanion / Tmux)
- In your Neovim Lua config:
  ```lua
  vim.keymap.set("n", "<leader>sr", function()
    local query = vim.fn.input("Skill Route Query: ")
    if query ~= "" then
      local handle = io.popen("python scripts/skill_hub.py route '" .. query .. "'")
      local result = handle:read("*a")
      handle:close()
      print(result)
    end
  end, { desc = "Run Universal Skill Router" })
  ```

---

## 🌐 Custom Skills Path Environment Variable (`SKILLS_PATH`)

If your team or organization stores skills in a custom central location:

```bash
# Linux / macOS / Bash / Zsh
export SKILLS_PATH="/opt/shared-skills:/home/user/company-skills"

# Windows PowerShell
$env:SKILLS_PATH = "D:\CustomSkills;C:\TeamSkills"
```

When you run `python scripts/skill_hub.py index` or `status`, `skill-router` automatically discovers and indexes every skill in those folders!

---

## 🔍 Verification: Check Your Environment Now

To verify that your current editor and skill roots are recognized:

```bash
python scripts/skill_hub.py env
```

You will see a live dashboard showing all detected editors and active skill roots.
