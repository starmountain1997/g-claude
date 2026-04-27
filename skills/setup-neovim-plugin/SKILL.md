---
name: setup-neovim-plugin
description: Configure a Neovim plugin from GitHub. Use whenever the user mentions adding, installing, or setting up a Vim/Neovim plugin, even if they don't say "skill" or "setup". Fetches docs via context7, writes minimal config to init.lua/init.vim, and updates the project README.md in Chinese.
---

## Plugin Setup Workflow

### Step 1: Identify the plugin

The user provides a plugin name or GitHub URL.

- If it's a full URL (e.g. `https://github.com/preservim/nerdtree`), extract the repo path (`preservim/nerdtree`).
- If it's just a name (e.g. `nerdtree`), assume `https://github.com/preservim/{name}` unless told otherwise.
- If it's an org/repo format (e.g. `vim-airline/vim-airline`), use it directly.

### Step 2: Fetch documentation via context7

Resolve the library ID for the plugin's GitHub repo. Use the repo path as `libraryName` (e.g. `preservim/nerdtree`) and query for installation and configuration instructions.

If context7 returns no useful results, fall back to a basic config template using the plugin name in lowercase with hyphens.

### Step 3: Detect Neovim config file

Check in the current working directory for:
- `init.lua` (preferred — Neovim's modern config format)
- `init.vim`
- `vim.cfg`

If none exist, create `init.lua`. If multiple exist, prefer `init.lua`.

### Step 4: Parse existing config

Read the existing config file. Track:
- Which plugins are already configured (via plugin managers like `use`, `plug`, `dein`, `packer`, or `lazy`).
- Any existing config blocks for the target plugin — if found, replace the entire block with the new minimal config (no保留 redundant setup).
- General settings to avoid duplicating.

Goal: keep config minimal and non-redundant. Rewrite sections for the same plugin rather than appending duplicate blocks.

### Step 5: Generate and write config

Use the context7 docs (or fallback) to write the minimal required config:
- Plugin declaration (using the detected/preferred plugin manager, or `lazy.nvim` as default for new setups)
- Any essential `require('plugin-name').setup({})` if the plugin uses Lua module
- NO keybindings unless the user explicitly asks for them

If the project already has a plugin manager set up (e.g. `vim-plug`), reuse it. If not, prefer `lazy.nvim` for new setups — it's the modern standard for Neovim.

### Step 6: Update README.md

Read the existing `README.md` in the current working directory.

Add or update a `## 插件配置` (Plugin Config) section with:
- Plugin name and GitHub link
- 安装方式 (Installation method) — paste the relevant config snippet
- 基本用法 (Basic usage) — key commands or API if applicable, in Chinese

Keep it concise. If the section already exists for this plugin, replace it entirely.

Format example:
```markdown
## 插件配置

### [plugin-name](https://github.com/org/repo)

**安装方式**

```lua
-- init.lua
return {
  "org/repo"
}
```

**基本用法**

- `:` command description
```

### Step 7: Verify

- Config file is valid Lua (no syntax errors)
- README.md has the new/updated section
- Report to the user: what was added/modified and where
