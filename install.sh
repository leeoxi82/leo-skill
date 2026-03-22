#!/usr/bin/env bash
# install.sh — Install a skill from leo-skill into your OpenClaw workspace
#
# Usage:
#   ./install.sh <category/skill-name>
#
# Examples:
#   ./install.sh ethan/academy/homework-checker
#   ./install.sh family/activity-finder
#
# What it does:
#   Creates a symlink: ~/.openclaw/workspace/skills/<skill-name> -> <repo>/skills/<path>
#   The skill name (last component of the path) is used as the symlink name.

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}/skills"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <path/to/skill>"
  echo ""
  echo "Available skills:"
  find "$REPO_DIR/skills" -name "SKILL.md" | sed "s|$REPO_DIR/skills/||" | sed "s|/SKILL.md||" | sort
  exit 1
fi

SKILL_PATH="$1"
SKILL_NAME="$(basename "$SKILL_PATH")"
SRC="$REPO_DIR/skills/$SKILL_PATH"
DST="$SKILLS_DIR/$SKILL_NAME"

if [[ ! -d "$SRC" ]]; then
  echo "❌ Skill not found: $SRC"
  echo ""
  echo "Available skills:"
  find "$REPO_DIR/skills" -name "SKILL.md" | sed "s|$REPO_DIR/skills/||" | sed "s|/SKILL.md||" | sort
  exit 1
fi

if [[ ! -f "$SRC/SKILL.md" ]]; then
  echo "❌ $SRC exists but has no SKILL.md — is this a skill directory?"
  exit 1
fi

mkdir -p "$SKILLS_DIR"

if [[ -L "$DST" ]]; then
  echo "♻️  Updating existing symlink: $DST"
  rm "$DST"
elif [[ -e "$DST" ]]; then
  echo "⚠️  $DST already exists and is not a symlink. Remove it manually first."
  exit 1
fi

ln -s "$SRC" "$DST"
echo "✅ Installed: $SKILL_NAME"
echo "   $SRC"
echo "   → $DST"
