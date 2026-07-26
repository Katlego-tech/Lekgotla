#!/usr/bin/env bash
# setup-project.sh — bootstrap a new project from the Cultivation kit.
#
# Usage: copy this file into a new (empty, or freshly `git init`'d) repo directory and run:
#   bash setup-project.sh
#
# It asks who's on the project and which AI each person uses, then dynamically copies only the
# files that project actually needs (CLAUDE.md only if someone uses Claude, GEMINI.md only if
# someone uses Gemini, a generated <TOOL>.md for anything else), fills in the placeholders it can,
# wires up the pre-push hook, and prints the manual steps it can't safely do for you.

set -euo pipefail

CULTIVATION_DIR="${CULTIVATION_DIR:-$HOME/Documents/projects/personal/Cultivation}"

if [ ! -d "$CULTIVATION_DIR" ]; then
  echo "Can't find the Cultivation kit at $CULTIVATION_DIR"
  echo "Set CULTIVATION_DIR=/path/to/Cultivation and re-run."
  exit 1
fi

ask() {
  local prompt="$1" default="${2:-}" ans
  read -rp "$prompt${default:+ [$default]}: " ans
  echo "${ans:-$default}"
}
ask_yn() {
  local prompt="$1" default="${2:-N}" ans
  read -rp "$prompt [y/N]: " ans
  ans="${ans:-$default}"
  [[ "$ans" =~ ^[Yy]$ ]]
}
sed_escape() { printf '%s' "$1" | sed -e 's/[\&#]/\\&/g'; }

echo "============================================================"
echo " Cultivation kit -- new project setup"
echo "============================================================"
echo

# ---------------------------------------------------------------- Step A ----
echo "-- Step A: the shape of this project --"
PROJECT_NAME=$(ask "Project name" "$(basename "$PWD")")
DEADLINE=$(ask "Deadline (leave blank if none)" "TBD")

echo
echo "Team & AI copilots -- who's on this project, and what does each person use?"
NAMES=(); ROLES=(); AIS=()
i=1
while true; do
  echo "Contributor $i:"
  def_name=""; def_role="Co-builder"; def_ai="Gemini"
  if [ "$i" -eq 1 ]; then def_name="$(whoami)"; def_role="Project leader"; def_ai="Claude"; fi
  name=$(ask "  Name" "$def_name")
  role=$(ask "  Role" "$def_role")
  ai=$(ask "  AI copilot (Claude/Gemini/anything else)" "$def_ai")
  NAMES+=("$name"); ROLES+=("$role"); AIS+=("$ai")
  i=$((i + 1))
  ask_yn "Add another contributor?" || break
done

echo
GROUNDING=$(ask "The one thing this project must NEVER fabricate or get wrong")
ONE_LINER=$(ask "One-paragraph description of what this project does")
PLANNING_MODE=$(ask "Planning docs: plain (SPEC/PLAN/TASKS) or speckit (formal lifecycle)" "plain")

echo
echo "Architecture defaults (see docs/architecture-defaults.md) -- override per project if you have a real reason."
ARCHITECTURE_STYLE=$(ask "Architecture style" "Microservices -- one service per bounded context")
MESSAGING_QUEUE=$(ask "Messaging queue for this project (Kafka / RabbitMQ / none)" "RabbitMQ")
FRONTEND_STACK=$(ask "Frontend stack (or 'none' if this project has no frontend)" "React + shadcn/ui (Radix + Tailwind + CVA)")
CONTAINERIZATION=$(ask "Containerization" "Docker per service + one docker-compose.yml for local dev")

# ---------------------------------------------------------------- Step B ----
echo
echo "-- Step B: copying the core files --"
mkdir -p docs .githooks

cp "$CULTIVATION_DIR/AGENTS.md" ./AGENTS.md
cp "$CULTIVATION_DIR/STATUS.template.md" ./STATUS.md
cp "$CULTIVATION_DIR/SPEC.template.md" ./SPEC.md
cp "$CULTIVATION_DIR/PLAN.template.md" ./PLAN.md
cp "$CULTIVATION_DIR/TASKS.template.md" ./TASKS.md
cp "$CULTIVATION_DIR"/docs/*.md ./docs/
# The handoff template ships unfilled. It gets copied to docs/HANDOFF.md and filled in only
# when work is actually being handed off -- see docs/cross-ai-protocol.md "Handoffs".
cp "$CULTIVATION_DIR/HANDOFF.template.md" ./docs/HANDOFF.template.md
echo "Copied: AGENTS.md STATUS.md SPEC.md PLAN.md TASKS.md docs/*.md docs/HANDOFF.template.md"

if [ -d "$CULTIVATION_DIR/.claude" ]; then
  mkdir -p .claude
  cp -r "$CULTIVATION_DIR/.claude/." ./.claude/
  echo "Copied: .claude/ (agents, feature-dev command, frontend-design skill)"
fi

# ---- dynamically create one entry-point file per unique AI in play --------
echo
echo "-- Step B2: entry-point files (one per AI tool actually in use) --"
declare -A OWNER_OF_FILE=()
CREATED_ENTRYPOINTS=()

for idx in "${!AIS[@]}"; do
  ai="${AIS[$idx]}"
  person="${NAMES[$idx]}"
  lower=$(printf '%s' "$ai" | tr '[:upper:]' '[:lower:]')

  case "$lower" in
    *claude*)
      fname="CLAUDE.md"; src="$CULTIVATION_DIR/CLAUDE.md"; kind=claude ;;
    *gemini*|*antigravity*)
      fname="GEMINI.md"; src="$CULTIVATION_DIR/GEMINI.md"; kind=gemini ;;
    *)
      slug=$(printf '%s' "$ai" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '_' | sed -e 's/^_*//' -e 's/_*$//')
      fname="$(printf '%s' "$slug" | tr '[:lower:]' '[:upper:]').md"
      src="$CULTIVATION_DIR/AI_ENTRYPOINT.template.md"; kind=generic ;;
  esac

  if [ -n "${OWNER_OF_FILE[$fname]:-}" ]; then
    echo "  skip: $fname already created for ${OWNER_OF_FILE[$fname]} -- $person also uses $ai;"
    echo "        edit $fname by hand to mention both of you."
    continue
  fi

  cp "$src" "./$fname"
  case "$kind" in
    claude) sed -i "s#<PERSON_A[^>]*>#$(sed_escape "$person")#g" "./$fname" ;;
    gemini) sed -i "s#<PERSON_B[^>]*>#$(sed_escape "$person")#g" "./$fname" ;;
    generic)
      sed -i "s#<TOOL_NAME>#$(sed_escape "$ai")#g; s#<PERSON>#$(sed_escape "$person")#g" "./$fname"
      ;;
  esac
  OWNER_OF_FILE[$fname]="$person"
  CREATED_ENTRYPOINTS+=("$fname")
  echo "  created $fname for $person ($ai)"
done

if ask_yn "Keep AI_ENTRYPOINT.template.md as a spare, for contributors who join later?" "Y"; then
  cp "$CULTIVATION_DIR/AI_ENTRYPOINT.template.md" ./AI_ENTRYPOINT.template.md
fi

# ---------------------------------------------------------------- Step C ----
echo
echo "-- Step C: rebuilding the AGENTS.md team table for $((i - 1)) contributor(s) --"

TEAM_ROWS=""
for idx in "${!NAMES[@]}"; do
  TEAM_ROWS+="| ${NAMES[$idx]} | ${ROLES[$idx]} | ${AIS[$idx]} |"$'\n'
done
sed -i '/<PERSON_A>/d;/<PERSON_B>/d' AGENTS.md
awk -v rows="$TEAM_ROWS" '{print} /^\|--------\|------\|----------------\|$/{printf "%s", rows}' \
  AGENTS.md > AGENTS.md.tmp && mv AGENTS.md.tmp AGENTS.md

echo
echo "-- Step C2: filling in the rest of the placeholders --"
replace_token() {
  local token="$1" value="$2" escaped
  escaped=$(sed_escape "$value")
  for f in *.md docs/*.md; do
    [ -f "$f" ] || continue
    sed -i "s#<${token}[^>]*>#${escaped}#g" "$f"
  done
}
replace_token "PROJECT_NAME" "$PROJECT_NAME"
replace_token "DEADLINE" "$DEADLINE"
replace_token "YOUR_GROUNDING_RULE" "$GROUNDING"
replace_token "ONE_PARAGRAPH_PROJECT_DESCRIPTION" "$ONE_LINER"
replace_token "ARCHITECTURE_STYLE" "$ARCHITECTURE_STYLE"
replace_token "MESSAGING_QUEUE" "$MESSAGING_QUEUE"
replace_token "FRONTEND_STACK" "$FRONTEND_STACK"
replace_token "CONTAINERIZATION" "$CONTAINERIZATION"

echo "Substituted the identity + team placeholders."
echo "Anything still showing <...> or a 📝 Customize callout needs a manual pass -- notably"
echo "PLAN.md's Non-negotiables + Technical Context, the locked-stack line, and TASKS.md's list."

# ---------------------------------------------------------------- Step D ----
echo
echo "-- Step D: git + the pre-push hook --"

if [ ! -d .git ]; then
  if ask_yn "Not a git repo yet -- run 'git init'?"; then
    git init
  fi
fi

if ask_yn "Write .githooks/pre-push now?"; then
  cat > .githooks/pre-push <<'HOOK'
#!/usr/bin/env bash
# Pre-push gate: blocks direct pushes to main, runs whatever test tooling it finds.
# Customize the loop below for your real project layout -- see docs/git-workflow.md.
set -u
protected="refs/heads/main"
while read -r local_ref local_sha remote_ref remote_sha; do
  if [ "$remote_ref" = "$protected" ]; then
    echo "Direct pushes to 'main' are not allowed. Push a branch and open a PR."
    exit 1
  fi
done

echo "Running the test gate before push..."
fail=0
root="$(git rev-parse --show-toplevel)"

for dir in "$root" "$root"/services/* "$root"/apps/*; do
  [ -d "$dir" ] || continue
  if { [ -f "$dir/pyproject.toml" ] || [ -f "$dir/requirements.txt" ]; } \
      && python -c "import pytest" >/dev/null 2>&1; then
    echo "-> pytest ($dir)"
    ( cd "$dir" && python -m pytest -q ) || fail=1
  fi
  if [ -f "$dir/package.json" ] && [ -d "$root/node_modules" ]; then
    echo "-> npm test ($dir)"
    ( cd "$dir" && npm test --silent --if-present ) || fail=1
  fi
done

if [ "$fail" -ne 0 ]; then
  echo "Test gate failed. Fix it before pushing (or --no-verify only for a green branch)."
  exit 1
fi
echo "Test gate passed."
exit 0
HOOK
  chmod +x .githooks/pre-push
  echo "Wrote .githooks/pre-push."
fi

if [ -d .git ]; then
  git config core.hooksPath .githooks
  echo "git config core.hooksPath .githooks -- done."
fi

# ---------------------------------------------------------------- Step E ----
echo
echo "-- Step E: what's left (manual -- this script won't do these for you) --"
cat <<EOF
Files created for this project: AGENTS.md STATUS.md SPEC.md PLAN.md TASKS.md docs/*.md ${CREATED_ENTRYPOINTS[*]} .claude/

Architecture defaults recorded in PLAN.md: $ARCHITECTURE_STYLE / $MESSAGING_QUEUE / $FRONTEND_STACK / $CONTAINERIZATION
(see docs/architecture-defaults.md -- edit PLAN.md's Technical Context table if this project should
deviate from any of these).

1. Open every file above and search for '<' and '📝' -- fill in anything left, especially:
     - PLAN.md: Non-negotiables + the rest of the Technical Context table. Pin EXACT versions in the
       Language(s)/Runtime rows -- default is the latest LTS, confirmed against the source, not assumed
       (docs/architecture-defaults.md §5).
     - ${CREATED_ENTRYPOINTS[*]}: the "Locked stack" line
     - TASKS.md: your real Phase 1 setup tasks
     - docs/project-structure.md: the real repo tree, once services/ and apps/ exist
2. Planning mode chosen: $PLANNING_MODE
$( [ "$PLANNING_MODE" = "speckit" ] && echo "   -> read docs/planning-workflow.md's \"heavier alternative\" section before running \`specify init\`." )
3. If this is a real microservices project, set up the broker now ($MESSAGING_QUEUE) -- a
   docker-compose entry or managed instance -- and note it in docs/project-structure.md.
4. Create the remote repo and add it:
     git remote add origin <url>
5. Commit + push the scaffold ONCE directly to main (the only allowed direct push):
     git add -A && git commit -m "chore: bootstrap project scaffold"
     git push -u origin main
6. Turn on branch protection on main (require PR, require the CI check, require review, disallow bypass).
7. Add a CI workflow that reruns the same checks as the pre-push hook.
8. Prove the loop once: branch -> trivial change -> push -> PR -> green CI -> merge.
   Also try pushing straight to main on purpose -- confirm the hook rejects it.
9. Claim your first lane in STATUS.md, write T001 in TASKS.md, and start.

Frontend lanes are assigned to Claude by default (AGENTS.md section 1) — the frontend-design
skill only loads for Claude, and a visual identity degrades when several hands re-decide palette
and spacing in turn. Other AIs use the existing components but don't restyle or hand-roll UI.
Delete that section if this project has no frontend.

Handoffs are part of the cycle here, not an exception. When an AI is about to run out of
budget or hand work to another tool, it copies docs/HANDOFF.template.md to docs/HANDOFF.md,
fills it in, and flips the "## HANDOFF" block at the top of STATUS.md to ACTIVE. Every
entry-point file makes reading that block step 0 of every session, so the next AI picks the
work up automatically instead of re-deriving context. Rules: docs/cross-ai-protocol.md.
EOF

echo
if ask_yn "Delete this setup script now that it's done?"; then
  rm -- "$0"
  echo "Removed setup-project.sh."
fi

echo
echo "Done. Full checklist with checkboxes: $CULTIVATION_DIR/SETUP-CHECKLIST.md"
