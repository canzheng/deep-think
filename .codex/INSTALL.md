# Install Deep Think For Codex

Install from GitHub with one shared local checkout and a symlink into Codex
skills.

## Install

```bash
git clone https://github.com/canzheng/deep-think.git ~/.deep-think
mkdir -p ~/.codex/skills
ln -s ~/.deep-think/skills/deep-think/codex ~/.codex/skills/deep-think
```

If `~/.deep-think` already exists:

```bash
cd ~/.deep-think && git pull
```

If `~/.codex/skills/deep-think` already exists and should be replaced:

```bash
rm ~/.codex/skills/deep-think
ln -s ~/.deep-think/skills/deep-think/codex ~/.codex/skills/deep-think
```

## Update

```bash
cd ~/.deep-think && git pull
```

Because the skill path is a symlink into the repo checkout, pulling updates is
enough.

## Notes

- Codex discovers the installed skill from `~/.codex/skills/deep-think`.
- The Codex skill root is `skills/deep-think/codex`.
- Start a new Codex session after install or update if the skill does not
  appear immediately.
