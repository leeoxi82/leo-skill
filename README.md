# leo-skill

Leo's personal [OpenClaw](https://github.com/openclaw/openclaw) skill collection, organized by life domain.

## Structure

```
skills/
├── ethan/
│   ├── academy/          ← Ethan's school & homework
│   │   └── homework-checker/
│   └── college-prep/     ← College apps (future)
├── family/               ← Family life (future)
├── work/                 ← Leo's work (future)
└── ops/                  ← Server ops (future)
```

See [CATALOG.md](./CATALOG.md) for the full skill index.

## Install a skill

```bash
# Clone the repo once
git clone https://github.com/leeoxi82/leo-skill.git ~/leo-skill
cd ~/leo-skill

# Install a skill (creates a symlink into your workspace)
./install.sh ethan/academy/homework-checker
```

This creates:
```
~/.openclaw/workspace/skills/homework-checker -> ~/leo-skill/skills/ethan/academy/homework-checker
```

OpenClaw picks it up automatically — no restart needed.

## Update all installed skills

Since skills are symlinks, just pull the repo:

```bash
cd ~/leo-skill && git pull
```

## Add a new skill

1. Create your skill under the right category folder:
   ```
   skills/<category>/<skill-name>/SKILL.md
   ```
2. Add it to [CATALOG.md](./CATALOG.md)
3. Commit and push
