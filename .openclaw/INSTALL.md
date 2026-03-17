# Install Deep Think For OpenClaw

Install from GitHub with one shared local checkout and a symlink into the
OpenClaw workspace skills directory.

## Install

```bash
git clone https://github.com/canzheng/deep-think.git ~/.deep-think
mkdir -p ~/.openclaw/workspace/skills
ln -s ~/.deep-think/skills/deep-think/openclaw ~/.openclaw/workspace/skills/deep-think
```

If `~/.deep-think` already exists:

```bash
cd ~/.deep-think && git pull
```

If `~/.openclaw/workspace/skills/deep-think` already exists and should be
replaced:

```bash
rm ~/.openclaw/workspace/skills/deep-think
ln -s ~/.deep-think/skills/deep-think/openclaw ~/.openclaw/workspace/skills/deep-think
```

## Update

```bash
cd ~/.deep-think && git pull
```

Because the skill path is a symlink into the repo checkout, pulling updates is
enough.

## Notes

- OpenClaw discovers the installed skill from
  `~/.openclaw/workspace/skills/deep-think`.
- The installed OpenClaw skill is the self-contained bundle rooted at
  `skills/deep-think/openclaw`.
- Start a new OpenClaw session after install or update if the skill does not
  appear immediately.
