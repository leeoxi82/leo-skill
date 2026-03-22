# leo-skill

Leo's personal [OpenClaw](https://github.com/openclaw/openclaw) skill collection.

Skills here are shared across machines — install them by symlinking or copying into `~/.openclaw/workspace/skills/`.

## Skills

| Skill | Description |
|-------|-------------|
| [homework-checker](./skills/homework-checker/) | Check Ethan's homework from photos, generate error explainer + tutoring + practice PDFs, publish to Notion |

## Usage

```bash
# Clone to your workspace skills directory
git clone https://github.com/leeoxi82/leo-skill.git /tmp/leo-skill

# Copy a skill into your workspace
cp -r /tmp/leo-skill/skills/homework-checker ~/.openclaw/workspace/skills/
```

Or just keep the repo somewhere and symlink:

```bash
git clone https://github.com/leeoxi82/leo-skill.git ~/.openclaw/leo-skill
ln -s ~/.openclaw/leo-skill/skills/homework-checker ~/.openclaw/workspace/skills/homework-checker
```

## Structure

```
skills/
  homework-checker/
    SKILL.md          # skill definition (loaded by OpenClaw)
    scripts/          # helper scripts
      notion_homework_setup.py
      notion_homework_publish_review.py
```
