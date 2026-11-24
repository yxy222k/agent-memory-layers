#!/usr/bin/env python3
"""agent-memory-layers (AML) unified cross-platform CLI & lifecycle hook engine.

Zero third-party dependencies (Python 3.9+ standard library only).
Supports both deployment topologies:
  - standalone : single-product dual-axis memory tree (<project-repo>/memory/)
  - hub        : multi-host, multi-agent fleet control plane + isolated products/*

Subcommands:
  init         Scaffold a standalone or hub memory directory from templates
  install      Register global startup instructions & lifecycle hooks for an agent tool
  uninstall    Cleanly remove AML instructions & hooks from an agent tool
  start        Pull (optional) and print progressive workspace-routed context manifest
  capture      Create a collision-free append-only note (inbox / transcript / anomaly)
  sync         Auto-commit and push safe append-only paths with backoff retry
  search       Tenant- and product-isolated keyword/regex search (rg with Python fallback)
  dream        Manage dual-gate offline consolidation worktree, triage & citation stats
  check        Zero-token mechanical validator for budgets, schemas, links, stale & secrets
  check-push   Git pre-push guard against leaking private instances to public remotes
  eval         Deterministic rubric & 5-arm ablation scorer for eval/cases.jsonl
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import random
import re
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from urllib.parse import unquote

DEFAULT_CONFIG: dict[str, Any] = {
    "protocol_version": "3.0",
    "mode": "auto",  # "standalone" | "hub" | "auto"
    "private_instance": False,
    "blocked_public_remotes": [
        "github.com/yxy222k/agent-memory-layers",
        "github.com:yxy222k/agent-memory-layers",
    ],
    "budgets": {
        "control_max_kb": 4,
        "memory_max_lines": 200,
        "memory_max_kb": 25,
        "nav_compression_max": 0.30,
        "nav_compression_min_base_bytes": 4096,
    },
    "workspace_routes": {},
}

SECRET_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("private-key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{30,}\b")),
    ("github-pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}\b")),
    ("openai-key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{32,}\b")),
    ("aws-access-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    ("inline-basic-auth", re.compile(r"https?://[^/\s:@<>]+:[^/\s:@<>]+@[^/\s<>]+")),
]

ID_REF_RE = re.compile(r"\[ref:\s*([A-Za-z0-9_.-]+)\]")
MD_LINK_RE = re.compile(r"\]\(\s*(<[^>]+>|[^)\s]+)")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
VALID_STATUS = {"verified", "hypothesis", "open", "refuted", "stale", "conflict"}

BOOTSTRAP_BEGIN = "<!-- aml:begin -->"
BOOTSTRAP_END = "<!-- aml:end -->"


# ---------------------------------------------------------------------------
# Helpers: config, git, frontmatter, interpreter detection
# ---------------------------------------------------------------------------


def kit_root() -> Path:
    return Path(__file__).resolve().parents[1]


def aml_home() -> Path:
    override = os.environ.get("AML_HOME")
    return Path(override).resolve() if override else (Path.home() / ".aml")


def detect_mode(repo: Path, cfg: dict[str, Any]) -> str:
    explicit = cfg.get("mode", "auto")
    if explicit in ("standalone", "hub"):
        return explicit
    if (repo / "0_control").is_dir() or (repo / "products").is_dir():
        return "hub"
    return "standalone"


def load_config(repo: Path) -> dict[str, Any]:
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    cfg_path = repo / "aml.json"
    if cfg_path.is_file():
        try:
            user_cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            for k, v in user_cfg.items():
                if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                    cfg[k].update(v)
                else:
                    cfg[k] = v
        except Exception as exc:  # noqa: BLE001
            sys.stderr.write(f"[aml] warning: failed to parse {cfg_path}: {exc}\n")
    cfg["mode"] = detect_mode(repo, cfg)
    return cfg


def sanitize_slug(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", text.strip().lower()).strip("-")
    return slug or "note"


def default_host() -> str:
    raw = os.environ.get("AML_HOST") or socket.gethostname().split(".")[0]
    return sanitize_slug(raw)


def git_cmd(cwd: Path, *args: str, timeout: int = 20) -> tuple[int, str]:
    try:
        res = subprocess.run(
            ["git", "-C", str(cwd), *args],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
        return res.returncode, (res.stdout + res.stderr).strip()
    except Exception as exc:  # noqa: BLE001
        return 1, str(exc)


def is_gitcrypt_locked(repo: Path) -> bool:
    for probe in ("aml.json", "AGENTS.md", "0_control/rules.md", "README.md"):
        p = repo / probe
        if p.is_file():
            try:
                if p.read_bytes()[:10].startswith(b"\x00GITCRYPT"):
                    return True
            except OSError:
                return True
    if (repo / ".git" / "git-crypt").is_dir():
        rc, _ = git_cmd(repo, "config", "--get", "filter.git-crypt.clean")
        if rc != 0:
            return True
    return False


def resolve_python_cmd() -> list[str]:
    """Return a verified Python >=3.9 command list, avoiding WindowsApps Store stubs."""
    candidates: list[list[str]] = []
    if sys.executable and "WindowsApps" not in sys.executable:
        candidates.append([sys.executable])
    if os.name == "nt":
        candidates.extend([["py", "-3"], ["python3"], ["python"]])
    else:
        candidates.extend([["python3"], ["python"]])

    for cmd in candidates:
        try:
            res = subprocess.run(
                [*cmd, "-c", "import sys; assert sys.version_info >= (3, 9); print(sys.executable)"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if res.returncode == 0 and "WindowsApps" not in res.stdout:
                return cmd
        except Exception:  # noqa: BLE001
            continue
    return [sys.executable or "python3"]


def parse_frontmatter(text: str) -> dict[str, Any]:
    """Lightweight zero-dependency YAML frontmatter parser for flat scalars & inline lists."""
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end_idx = -1
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx == -1:
        return {}

    meta: dict[str, Any] = {}
    for raw_line in lines[1:end_idx]:
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, val = line.split(":", 1)
        key = key.strip()
        # Strip trailing inline comment outside quotes/brackets
        val = re.sub(r"\s+#.*$", "", val).strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            if not inner:
                meta[key] = []
            else:
                items = [
                    item.strip().strip("\"'")
                    for item in inner.split(",")
                    if item.strip().strip("\"'")
                ]
                meta[key] = items
        elif val.lower() in ("true", "false"):
            meta[key] = val.lower() == "true"
        else:
            meta[key] = val.strip("\"'")
    return meta


def product_roots(repo: Path, cfg: dict[str, Any], product_filter: str | None = None) -> list[tuple[str, Path]]:
    mode = cfg["mode"]
    if mode == "standalone":
        return [("default", repo)]
    prod_base = repo / "products"
    if not prod_base.is_dir():
        return []
    out: list[tuple[str, Path]] = []
    for child in sorted(prod_base.iterdir()):
        if not child.is_dir() or child.name.startswith((".", "_")):
            continue
        if product_filter and child.name != product_filter:
            continue
        out.append((child.name, child))
    return out


# ---------------------------------------------------------------------------
# Subcommand: init
# ---------------------------------------------------------------------------


def copy_tree_no_clobber(src: Path, dst: Path) -> int:
    copied = 0
    if not src.is_dir():
        return 0
    for item in src.rglob("*"):
        rel = item.relative_to(src)
        target = dst / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif not target.exists():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
            copied += 1
    return copied


def install_git_pre_push(repo: Path, script_self: Path) -> None:
    if not (repo / ".git").exists():
        return
    hooks_dir = repo / "scripts" / "git-hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    hook_file = hooks_dir / "pre-push"
    aml_rel = "scripts/aml.py"
    target_aml = repo / aml_rel
    if not target_aml.exists() and script_self.is_file():
        target_aml.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(script_self, target_aml)
    hook_content = (
        "#!/usr/bin/env sh\n"
        "# Auto-installed by agent-memory-layers: blocks leaking private instances or secrets.\n"
        'REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"\n'
        "if command -v py >/dev/null 2>&1; then\n"
        '  py -3 "$REPO_ROOT/scripts/aml.py" check-push --repo "$REPO_ROOT" --remote-name "${1:-}" --remote-url "${2:-}"\n'
        "elif command -v python3 >/dev/null 2>&1; then\n"
        '  python3 "$REPO_ROOT/scripts/aml.py" check-push --repo "$REPO_ROOT" --remote-name "${1:-}" --remote-url "${2:-}"\n'
        "else\n"
        '  python "$REPO_ROOT/scripts/aml.py" check-push --repo "$REPO_ROOT" --remote-name "${1:-}" --remote-url "${2:-}"\n'
        "fi\n"
    )
    hook_file.write_text(hook_content, encoding="utf-8", newline="\n")
    try:
        hook_file.chmod(0o755)
    except OSError:
        pass
    git_cmd(repo, "config", "core.hooksPath", "scripts/git-hooks")


def cmd_init(args: argparse.Namespace) -> int:
    root = kit_root()
    target = Path(args.target).resolve()
    target.mkdir(parents=True, exist_ok=True)
    mode = args.mode

    copied = 0
    if mode == "standalone":
        copied += copy_tree_no_clobber(root / "templates" / "product", target)
        copied += copy_tree_no_clobber(root / "templates" / "dreaming", target / "dreaming")
        cfg = json.loads(json.dumps(DEFAULT_CONFIG))
        cfg["mode"] = "standalone"
        cfg["private_instance"] = bool(args.private)
    else:
        copied += copy_tree_no_clobber(root / "templates" / "hub", target)
        copied += copy_tree_no_clobber(root / "templates" / "dreaming", target / "dreaming")
        slugs = [sanitize_slug(s) for s in (args.products or "example-system").split(",") if s.strip()]
        for slug in slugs:
            copied += copy_tree_no_clobber(root / "templates" / "product", target / "products" / slug)
        cfg = json.loads(json.dumps(DEFAULT_CONFIG))
        cfg["mode"] = "hub"
        cfg["private_instance"] = bool(args.private)

    cfg_path = target / "aml.json"
    if not cfg_path.exists():
        cfg_path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        copied += 1

    install_git_pre_push(target, Path(__file__).resolve())
    print(f"[aml] initialized '{mode}' memory tree at {target} ({copied} files created).")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: start & hook-start
# ---------------------------------------------------------------------------


def match_workspace_product(repo: Path, cfg: dict[str, Any], cwd: Path | None) -> str | None:
    if cwd is None or cfg["mode"] != "hub":
        return None
    cwd_norm = cwd.resolve().as_posix().lower()

    # Check if cwd is directly inside repo/products/<slug>
    prod_dir = (repo / "products").resolve()
    try:
        rel = cwd.resolve().relative_to(prod_dir)
        if rel.parts:
            return rel.parts[0]
    except ValueError:
        pass

    routes: dict[str, str] = cfg.get("workspace_routes") or {}
    best_slug: str | None = None
    best_len = -1
    for prefix, slug in routes.items():
        norm_prefix = Path(os.path.expanduser(prefix)).resolve().as_posix().lower().rstrip("/")
        if cwd_norm == norm_prefix or cwd_norm.startswith(norm_prefix + "/"):
            if len(norm_prefix) > best_len:
                best_len = len(norm_prefix)
                best_slug = slug
    return best_slug


def build_start_manifest(
    repo: Path,
    host: str,
    agent_id: str,
    cwd: Path | None = None,
    do_pull: bool = False,
) -> str:
    cfg = load_config(repo)
    mode = cfg["mode"]
    warnings: list[str] = []

    if do_pull and (repo / ".git").exists():
        rc_b, curr_b = git_cmd(repo, "symbolic-ref", "-q", "--short", "HEAD")
        rc_o, orig_b = git_cmd(repo, "symbolic-ref", "-q", "--short", "refs/remotes/origin/HEAD")
        def_b = orig_b.replace("origin/", "") if rc_o == 0 else ""
        if def_b and curr_b and curr_b != def_b:
            warnings.append(
                f"[!] Memory repo at {repo} is on branch '{curr_b}' (default '{def_b}'); auto-pull skipped."
            )
        else:
            rc_p, _ = git_cmd(repo, "pull", "--rebase", "--autostash", "-q")
            if rc_p != 0:
                git_cmd(repo, "rebase", "--abort")
                warnings.append(f"[!] Auto-pull failed in {repo}; using local state.")

    if is_gitcrypt_locked(repo):
        return (
            f"[aml] Memory repository at {repo} is git-crypt LOCKED. "
            "Unlock with `git crypt unlock` before reading or writing memory."
        )

    read_now: list[Path] = []
    read_on_demand: list[str] = []

    if mode == "hub":
        for rel in ("0_control/rules.md", f"0_control/hosts/{host}/env.md"):
            p = repo / rel
            if p.is_file():
                read_now.append(p)
        matched = match_workspace_product(repo, cfg, cwd)
        if matched and (repo / "products" / matched).is_dir():
            p_root = repo / "products" / matched
            for rel in ("AGENTS.md", "MEMORY.md"):
                if (p_root / rel).is_file():
                    read_now.append(p_root / rel)
            read_on_demand.append(
                f"{p_root.as_posix()}/{{1_theory,2_calibration,3_skills,4_anomalies,transcripts}} (active product: {matched})"
            )
        else:
            idx = repo / "0_control" / "INDEX.md"
            if idx.is_file():
                read_now.append(idx)
            prods = [name for name, _ in product_roots(repo, cfg)]
            if prods:
                read_on_demand.append(f"{(repo / 'products').as_posix()}/<product>/MEMORY.md (available: {', '.join(prods)})")
        if (repo / "0_control" / "shared_skills").is_dir():
            read_on_demand.append(f"{(repo / '0_control' / 'shared_skills').as_posix()}/ (cross-product skills)")
        write_rule = (
            f"Online writes MUST create uniquely named append-only files under "
            f"{(repo / 'inbox').as_posix()}/, products/<p>/transcripts/, or products/<p>/4_anomalies/open/. "
            "Never overwrite curated layers (0_control/, MEMORY.md, 1_theory/, 2_calibration/, 3_skills/) in-session."
        )
    else:
        for rel in ("AGENTS.md", "MEMORY.md"):
            p = repo / rel
            if p.is_file():
                read_now.append(p)
        read_on_demand.append(f"{repo.as_posix()}/{{1_theory,2_calibration,3_skills,4_anomalies,transcripts}}")
        write_rule = (
            f"Online writes MUST create uniquely named append-only files under "
            f"{(repo / 'transcripts').as_posix()}/ or {(repo / '4_anomalies' / 'open').as_posix()}/. "
            "Curated layers (MEMORY.md, 1_theory/, 2_calibration/, 3_skills/) update only via offline Dreaming."
        )

    lines = [f"[aml] AGENT-MEMORY-LAYERS BOOTSTRAP — mode={mode} | identity={host}/{agent_id}"]
    lines.extend(warnings)
    lines.append("=== READ-ON-START (injected context) ===")
    for p in read_now:
        lines.append(f"- {p.as_posix()}")
    lines.append("=== READ-ON-DEMAND (load only what the task requires) ===")
    for item in read_on_demand:
        lines.append(f"- {item}")
    lines.append("=== PRIORITY & WRITE PROTOCOL ===")
    lines.append(
        "Priority: 1) Safety/secret/overload guardrails > 2) Host env > 3) Tenant site rules > "
        "4) Per-asset SN baselines > 5) General theory/SOPs/skills."
    )
    lines.append(write_rule)
    return "\n".join(lines)


def cmd_start(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    cwd = Path(args.cwd).resolve() if args.cwd else Path.cwd()
    host = args.host or default_host()
    agent = args.agent or "cli"
    print(build_start_manifest(repo, host, agent, cwd=cwd, do_pull=bool(args.pull)))
    return 0


def cmd_hook_start(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    host = args.host or default_host()
    agent = args.agent or "agent"
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except Exception:  # noqa: BLE001
        payload = {}

    session_key = payload.get("conversationId") or payload.get("session_id") or ""
    if session_key:
        state_dir = aml_home() / "state"
        state_dir.mkdir(parents=True, exist_ok=True)
        marker = state_dir / sanitize_slug(session_key)
        if marker.exists():
            print("{}")
            return 0
        try:
            marker.write_text("", encoding="utf-8")
        except OSError:
            pass

    cwd_str = payload.get("cwd") or payload.get("workspacePath")
    cwd = Path(cwd_str) if cwd_str else Path.cwd()
    msg = build_start_manifest(repo, host, agent, cwd=cwd, do_pull=True)

    fmt = args.format
    if fmt == "antigravity":
        print(json.dumps({"injectSteps": [{"ephemeralMessage": msg}]}, ensure_ascii=False))
    elif fmt == "claude":
        print(
            json.dumps(
                {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": msg}},
                ensure_ascii=False,
            )
        )
    else:
        print(msg)
    return 0


# ---------------------------------------------------------------------------
# Subcommand: capture, sync & hook-stop
# ---------------------------------------------------------------------------


def cmd_capture(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    cfg = load_config(repo)
    mode = cfg["mode"]
    host = args.host or default_host()
    agent = args.agent or "agent"
    now = dt.datetime.now()
    ts = now.strftime("%Y%m%d-%H%M%S")
    date_iso = now.strftime("%Y-%m-%d")
    slug = sanitize_slug(args.slug or args.title)

    if mode == "hub" and args.kind != "inbox":
        if not args.product:
            sys.stderr.write("[aml] --product <slug> is required for transcript/anomaly in hub mode (or use --kind inbox).\n")
            return 1
        base = repo / "products" / args.product
        if not base.is_dir():
            sys.stderr.write(f"[aml] product '{args.product}' not found under {repo / 'products'}\n")
            return 1
    else:
        base = repo

    if args.kind == "inbox":
        out_dir = repo / "inbox" if mode == "hub" else repo / "transcripts"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{ts}-{host}-{agent}-{slug}.md"
        body = (
            f"---\n"
            f"id: inbox-{ts}-{host}\n"
            f"date: \"{date_iso}\"\n"
            f"host: \"{host}\"\n"
            f"agent: \"{agent}\"\n"
            f"product_hint: \"{args.product or ''}\"\n"
            f"valid_run: true\n"
            f"---\n\n"
            f"# {args.title}\n\n"
            f"- Context / Version / Asset IDs: \n"
            f"- Observation: \n"
            f"- Evidence path: \n"
        )
    elif args.kind == "transcript":
        out_dir = (base / "tenants" / args.tenant / "transcripts") if args.tenant else (base / "transcripts")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{ts}-{host}-{slug}.md"
        body = (
            f"---\n"
            f"id: tr-{ts}-{host}\n"
            f"date: \"{date_iso}\"\n"
            f"source: lab\n"
            f"valid_run: true\n"
            f"software_version: \"{args.version or 'v0.0.0'}\"\n"
            f"asset_ids: []\n"
            f"referenced_ids: []\n"
            f"---\n\n"
            f"# {args.title}\n\n"
            f"## 1. Multimodal & Raw Data Pointers\n"
            f"- Physical setup photo: \n"
            f"- UI / telemetry snapshot: \n"
            f"- Raw archive (.hdf5 / .parquet / .pcapng): \n\n"
            f"## 2. Chronological Observation Log\n"
            f"- \n"
        )
    else:  # anomaly
        out_dir = base / "4_anomalies" / "open"
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"anom-{ts}-{slug}.md"
        scope = f"tenant:{args.tenant}" if args.tenant else "global"
        body = (
            f"---\n"
            f"id: anom-{ts}\n"
            f"title: \"{args.title}\"\n"
            f"status: open\n"
            f"scope: {scope}\n"
            f"software_version: \"{args.version or 'v0.0.0'}\"\n"
            f"asset_ids: []\n"
            f"evidence: []\n"
            f"created_at: \"{date_iso}\"\n"
            f"---\n\n"
            f"# [Open] {args.title}\n\n"
            f"## 1. Quantitative Symptom\n\n"
            f"## 2. Minimal Reproduction Conditions\n\n"
            f"## 3. Ruled-Out Factors & Falsifiable Next Check\n"
        )

    out_path.write_text(body, encoding="utf-8")
    print(out_path.as_posix())
    return 0


def safe_append_globs(repo: Path, cfg: dict[str, Any]) -> list[str]:
    candidates: list[Path] = []
    if cfg["mode"] == "hub":
        candidates.append(repo / "inbox")
        for _, p_root in product_roots(repo, cfg):
            candidates.extend([p_root / "transcripts", p_root / "4_anomalies" / "open"])
            tenants_dir = p_root / "tenants"
            if tenants_dir.is_dir():
                for t_dir in tenants_dir.iterdir():
                    if t_dir.is_dir() and not t_dir.name.startswith("_"):
                        candidates.append(t_dir / "transcripts")
    else:
        candidates.extend([repo / "transcripts", repo / "4_anomalies" / "open"])
        tenants_dir = repo / "tenants"
        if tenants_dir.is_dir():
            for t_dir in tenants_dir.iterdir():
                if t_dir.is_dir() and not t_dir.name.startswith("_"):
                    candidates.append(t_dir / "transcripts")
    return [c.relative_to(repo).as_posix() for c in candidates if c.exists()]


def scan_secrets_in_files(files: list[Path], base: Path) -> list[str]:
    issues: list[str] = []
    for path in files:
        if not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        rel = path.relative_to(base).as_posix()
        for label, rx in SECRET_PATTERNS:
            if rx.search(content):
                issues.append(f"{rel}: potential plaintext secret detected ({label})")
    return issues


def run_sync(repo: Path, host: str, agent: str, push: bool = True) -> tuple[int, str]:
    if not (repo / ".git").exists() or is_gitcrypt_locked(repo):
        return 0, "skipped (not a git repo or git-crypt locked)"

    cfg = load_config(repo)
    rels = safe_append_globs(repo, cfg)
    for rel in rels:
        git_cmd(repo, "add", "--", rel)

    rc_diff, staged_names = git_cmd(repo, "diff", "--cached", "--name-only")
    if rc_diff == 0 and staged_names.strip():
        staged_paths = [repo / line.strip() for line in staged_names.splitlines() if line.strip()]
        secret_hits = scan_secrets_in_files(staged_paths, repo)
        if secret_hits:
            git_cmd(repo, "reset", "-q")
            return 1, "secret scan blocked commit:\n" + "\n".join(secret_hits)
        msg = f"memory(capture): {host}/{agent}"
        rc_c, out_c = git_cmd(repo, "commit", "-m", msg, "--", *rels)
        if rc_c != 0:
            return 1, f"commit failed: {out_c}"

    if not push:
        return 0, "committed locally"

    rc_u, _ = git_cmd(repo, "rev-parse", "-q", "--verify", "@{u}")
    rc_a, ahead = git_cmd(repo, "rev-list", "--count", "@{u}..HEAD")
    if rc_u != 0 or rc_a != 0 or not ahead.strip().isdigit() or int(ahead.strip()) == 0:
        return 0, "up to date"

    for attempt in range(1, 4):
        rc_p, out_p = git_cmd(repo, "push", "-q")
        if rc_p == 0:
            return 0, "pushed"
        time.sleep((2 ** (attempt - 1)) * 0.4 + random.uniform(0.0, 0.25))
        rc_pull, _ = git_cmd(repo, "pull", "--rebase", "--autostash", "-q")
        if rc_pull != 0:
            git_cmd(repo, "rebase", "--abort")
            return 1, f"push/rebase conflict kept in local commit: {out_p}"
    return 1, "push failed after 3 attempts"


def cmd_sync(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    host = args.host or default_host()
    agent = args.agent or "cli"
    rc, status = run_sync(repo, host, agent, push=not args.no_push)
    if rc != 0:
        sys.stderr.write(f"[aml] sync error: {status}\n")
        return rc
    print(f"[aml] sync: {status}")
    return 0


def cmd_hook_stop(args: argparse.Namespace) -> int:
    try:
        sys.stdin.read()
    except Exception:  # noqa: BLE001
        pass
    repo = Path(args.repo).resolve()
    host = args.host or default_host()
    agent = args.agent or "agent"
    rc, status = run_sync(repo, host, agent, push=True)
    if rc != 0:
        sys.stderr.write(f"[aml] stop-hook warning: {status}\n")
    print("{}")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: install & uninstall
# ---------------------------------------------------------------------------


TOOL_INSTRUCTION_DEFAULTS: dict[str, str] = {
    "claude": "~/.claude/CLAUDE.md",
    "codex": "~/.codex/AGENTS.md",
    "antigravity": "~/.gemini/GEMINI.md",
    "gemini": "~/.gemini/GEMINI.md",
    "kimi": "~/.kimi/AGENTS.md",
}


def render_bootstrap_block(repo: Path, host: str, agent_id: str, py_cmd: list[str]) -> str:
    py_str = " ".join(py_cmd)
    aml_script = (repo / "scripts" / "aml.py").as_posix()
    if not (repo / "scripts" / "aml.py").exists():
        aml_script = Path(__file__).resolve().as_posix()
    repo_posix = repo.as_posix()
    return (
        f"{BOOTSTRAP_BEGIN}\n"
        f"# agent-memory-layers Startup & Write Protocol\n\n"
        f"- Identity: `{host}/{agent_id}` | Memory Root: `{repo_posix}`\n"
        f"- At session start (unless already injected by a SessionStart/PreInvocation hook), run:\n"
        f"  `{py_str} \"{aml_script}\" start --repo \"{repo_posix}\" --host \"{host}\" --agent \"{agent_id}\" --pull`\n"
        f"  and read ONLY the files listed under `READ-ON-START`.\n"
        f"- Load `1_theory/`, `2_calibration/`, `3_skills/`, `4_anomalies/`, and `transcripts/` strictly on demand.\n"
        f"- Scoped search (prevents cross-product & cross-tenant leakage):\n"
        f"  `{py_str} \"{aml_script}\" search --repo \"{repo_posix}\" [--product <slug>] [--tenant <code>] \"<query>\"`\n"
        f"- Priority chain: 1) Safety/secret/overload guardrails > 2) Host env > 3) Tenant site rules > "
        f"4) Per-asset SN baselines > 5) General theory/SOPs/skills.\n"
        f"- Online write boundary: NEVER overwrite curated files (`0_control/`, `MEMORY.md`, `1_theory/`, "
        f"`2_calibration/`, `3_skills/`) during live tasks. Capture new findings as uniquely named files via "
        f"`capture` into `inbox/`, `transcripts/`, or `4_anomalies/open/`, then sync at turn end:\n"
        f"  `{py_str} \"{aml_script}\" sync --repo \"{repo_posix}\" --host \"{host}\" --agent \"{agent_id}\"`\n"
        f"{BOOTSTRAP_END}\n"
    )


def upsert_block(file_path: Path, block: str) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    existing = file_path.read_text(encoding="utf-8") if file_path.is_file() else ""
    pattern = re.compile(re.escape(BOOTSTRAP_BEGIN) + r".*?" + re.escape(BOOTSTRAP_END) + r"\n?", re.S)
    if pattern.search(existing):
        updated = pattern.sub(block, existing)
    else:
        sep = "\n" if existing and not existing.endswith("\n") else ""
        updated = existing + sep + block
    file_path.write_text(updated, encoding="utf-8")


def remove_block(file_path: Path) -> bool:
    if not file_path.is_file():
        return False
    existing = file_path.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(BOOTSTRAP_BEGIN) + r".*?" + re.escape(BOOTSTRAP_END) + r"\n?", re.S)
    if not pattern.search(existing):
        return False
    file_path.write_text(pattern.sub("", existing), encoding="utf-8")
    return True


def configure_tool_hooks(
    tool: str,
    repo: Path,
    host: str,
    agent_id: str,
    py_cmd: list[str],
    remove: bool = False,
) -> str | None:
    aml_script = (repo / "scripts" / "aml.py")
    if not aml_script.exists():
        aml_script = Path(__file__).resolve()
    py_prefix = " ".join(f'"{c}"' if " " in c else c for c in py_cmd)
    fmt = "antigravity" if tool == "antigravity" else "claude"

    start_cmd = (
        f'{py_prefix} "{aml_script.as_posix()}" hook-start '
        f'--repo "{repo.as_posix()}" --host "{host}" --agent "{agent_id}" --format {fmt}'
    )
    stop_cmd = (
        f'{py_prefix} "{aml_script.as_posix()}" hook-stop '
        f'--repo "{repo.as_posix()}" --host "{host}" --agent "{agent_id}"'
    )

    hook_paths = {
        "antigravity": ("~/.gemini/config/hooks.json", "PreInvocation", "Stop"),
        "claude": ("~/.claude/settings.json", "SessionStart", "Stop"),
        "codex": ("~/.codex/hooks.json", "SessionStart", "Stop"),
    }
    if tool not in hook_paths:
        return None

    cfg_file_str, start_event, stop_event = hook_paths[tool]
    cfg_file = Path(os.path.expanduser(cfg_file_str))
    data: dict[str, Any] = {}
    if cfg_file.is_file():
        try:
            data = json.loads(cfg_file.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            data = {}

    hooks_obj = data.setdefault("hooks", {})

    def strip_aml(entries: list[Any]) -> list[Any]:
        cleaned = []
        for entry in entries:
            raw = json.dumps(entry)
            if "aml.py" in raw and ("hook-start" in raw or "hook-stop" in raw):
                continue
            cleaned.append(entry)
        return cleaned

    for evt in (start_event, stop_event):
        if isinstance(hooks_obj.get(evt), list):
            hooks_obj[evt] = strip_aml(hooks_obj[evt])

    if not remove:
        hooks_obj.setdefault(start_event, []).append(
            {"matcher": "*", "hooks": [{"type": "command", "command": start_cmd}]}
        )
        hooks_obj.setdefault(stop_event, []).append(
            {"matcher": "*", "hooks": [{"type": "command", "command": stop_cmd}]}
        )

    cfg_file.parent.mkdir(parents=True, exist_ok=True)
    cfg_file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return cfg_file.as_posix()


def cmd_install(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    tool = args.tool
    host = args.host or default_host()
    agent_id = args.agent_id or tool

    target_str = args.target or TOOL_INSTRUCTION_DEFAULTS.get(tool)
    if not target_str:
        sys.stderr.write("[aml] --target <instruction-file> is required when --tool is 'generic'.\n")
        return 1
    target_file = Path(os.path.expanduser(target_str)).resolve()

    py_cmd = resolve_python_cmd()
    block = render_bootstrap_block(repo, host, agent_id, py_cmd)
    upsert_block(target_file, block)
    hook_path = configure_tool_hooks(tool, repo, host, agent_id, py_cmd, remove=False)
    install_git_pre_push(repo, Path(__file__).resolve())

    id_dir = aml_home()
    id_dir.mkdir(parents=True, exist_ok=True)
    id_file = id_dir / "identity.json"
    identities: dict[str, Any] = {}
    if id_file.is_file():
        try:
            identities = json.loads(id_file.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            identities = {}
    identities["host"] = host
    identities.setdefault("tools", {})[tool] = {
        "agent_id": agent_id,
        "repo": repo.as_posix(),
        "instruction_file": target_file.as_posix(),
        "hooks_file": hook_path,
        "python": py_cmd,
    }
    id_file.write_text(json.dumps(identities, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"[aml] installed for tool='{tool}' as '{host}/{agent_id}'")
    print(f"  instruction : {target_file}")
    if hook_path:
        print(f"  hooks       : {hook_path}")
    print(f"  interpreter : {' '.join(py_cmd)}")
    return 0


def cmd_uninstall(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    tool = args.tool
    target_str = args.target or TOOL_INSTRUCTION_DEFAULTS.get(tool)
    if target_str:
        removed = remove_block(Path(os.path.expanduser(target_str)).resolve())
        print(f"[aml] instruction block removed={removed} ({target_str})")
    hook_path = configure_tool_hooks(tool, repo, default_host(), tool, resolve_python_cmd(), remove=True)
    if hook_path:
        print(f"[aml] hooks cleaned ({hook_path})")
    return 0


# ---------------------------------------------------------------------------
# Subcommand: search (product + tenant allowlist isolation)
# ---------------------------------------------------------------------------


def allowed_search_paths(
    repo: Path,
    cfg: dict[str, Any],
    product: str | None,
    tenant: str | None,
) -> list[Path]:
    paths: list[Path] = []
    public_subs = ("AGENTS.md", "MEMORY.md", "1_theory", "2_calibration", "3_skills", "4_anomalies", "transcripts")

    if cfg["mode"] == "hub":
        ctrl = repo / "0_control"
        if ctrl.is_dir():
            paths.append(ctrl)
        prods = product_roots(repo, cfg, product_filter=product)
        if tenant and not product and len(prods) > 1:
            sys.stderr.write("[aml] warning: --tenant requires --product in multi-product hub mode; tenant skipped.\n")
            tenant = None
        for _, p_root in prods:
            for sub in public_subs:
                cand = p_root / sub
                if cand.exists():
                    paths.append(cand)
            if tenant:
                t_dir = p_root / "tenants" / tenant
                if t_dir.is_dir():
                    paths.append(t_dir)
                else:
                    sys.stderr.write(f"[aml] warning: tenant '{tenant}' not found under {p_root}; searching public layers.\n")
    else:
        for sub in public_subs:
            cand = repo / sub
            if cand.exists():
                paths.append(cand)
        if tenant:
            t_dir = repo / "tenants" / tenant
            if t_dir.is_dir():
                paths.append(t_dir)
            else:
                sys.stderr.write(f"[aml] warning: tenant '{tenant}' not found under {repo}; searching public layers.\n")
    return paths


def cmd_search(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        sys.stderr.write(f"[aml] repository directory not found: {repo}\n")
        return 1
    cfg = load_config(repo)
    paths = allowed_search_paths(repo, cfg, args.product, args.tenant)
    if not paths:
        sys.stderr.write(f"[aml] no searchable memory layers found in {repo}\n")
        return 1

    rg_bin = shutil.which("rg")
    if rg_bin:
        res = subprocess.run(
            [
                rg_bin,
                "--line-number",
                "--smart-case",
                "--glob",
                "!.env*",
                "--glob",
                "!*.local.md",
                args.query,
                *[str(p) for p in paths],
            ]
        )
        return res.returncode

    flags = 0 if any(ch.isupper() for ch in args.query) else re.IGNORECASE
    rx = re.compile(args.query, flags)
    hits = 0
    for target in paths:
        files = [target] if target.is_file() else sorted(target.rglob("*"))
        for f in files:
            if not f.is_file() or f.name.startswith(".env") or f.name.endswith(".local.md"):
                continue
            try:
                for lineno, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                    if rx.search(line):
                        print(f"{f.as_posix()}:{lineno}:{line}")
                        hits += 1
            except OSError:
                continue
    return 0 if hits > 0 else 1


# ---------------------------------------------------------------------------
# Subcommand: check & check-push (Zero-Token Mechanical Gatekeeper)
# ---------------------------------------------------------------------------


def is_template_or_doc(path: Path) -> bool:
    if any(part.startswith("_") for part in path.parts):
        return True
    return path.name.startswith("_") or path.name in ("README.md", "index.md", "AGENTS.md", "MEMORY.md")


def dir_payload_bytes(paths: list[Path]) -> int:
    total = 0
    for base in paths:
        if base.is_file():
            total += base.stat().st_size
        elif base.is_dir():
            for f in base.rglob("*.md"):
                if not f.name.startswith("_") and f.name != "README.md":
                    total += f.stat().st_size
    return total


def check_product_tree(
    slug: str,
    p_root: Path,
    repo: Path,
    budgets: dict[str, Any],
) -> tuple[list[str], set[str]]:
    problems: list[str] = []
    prefix = f"[{slug}] " if slug != "default" else ""

    mem_file = p_root / "MEMORY.md"
    mem_text = ""
    if mem_file.is_file():
        raw = mem_file.read_bytes()
        mem_text = raw.decode("utf-8", errors="replace")
        line_count = len(mem_text.splitlines())
        max_lines = int(budgets.get("memory_max_lines", 200))
        max_kb = int(budgets.get("memory_max_kb", 25))
        if line_count > max_lines or len(raw) > max_kb * 1024:
            problems.append(
                f"{prefix}{mem_file.relative_to(repo).as_posix()}: {line_count} lines / {len(raw)} B "
                f"exceeds cap ({max_lines} lines / {max_kb} KB)"
            )

    # Borges navigation compression ratio check
    nav_bytes = dir_payload_bytes([p_root / "1_theory", p_root / "MEMORY.md"])
    base_bytes = dir_payload_bytes([p_root / "transcripts", p_root / "2_calibration", p_root / "4_anomalies"])
    min_base = int(budgets.get("nav_compression_min_base_bytes", 4096))
    max_ratio = float(budgets.get("nav_compression_max", 0.30))
    if base_bytes >= min_base and (nav_bytes / base_bytes) > max_ratio:
        problems.append(
            f"{prefix}navigation compression ratio {nav_bytes / base_bytes:.2f} > {max_ratio:.2f} "
            f"(nav={nav_bytes}B, base={base_bytes}B); trim 1_theory/ or MEMORY.md"
        )

    # Collect entry metadata across layers
    defined_ids: dict[str, Path] = {}
    stale_ids: set[str] = set()
    referenced_checks: list[tuple[Path, str]] = []
    md_files = [
        f
        for f in sorted(p_root.rglob("*.md"))
        if ".dream-worktree" not in f.parts
    ]

    for md in md_files:
        rel_p = md.relative_to(p_root)
        rel_repo = md.relative_to(repo).as_posix()
        text = md.read_text(encoding="utf-8", errors="replace")

        # Cross-tenant isolation check
        if len(rel_p.parts) >= 2 and rel_p.parts[0] == "tenants" and not rel_p.parts[1].startswith("_"):
            own_tenant = rel_p.parts[1]
            for other_match in re.findall(r"tenants/([A-Za-z0-9_-]+)", text):
                if other_match != own_tenant and not other_match.startswith("_"):
                    problems.append(f"{prefix}{rel_repo}: cross-tenant reference to 'tenants/{other_match}'")

        # Relative Markdown link check (skip template placeholders like ____.md)
        if not any(part.startswith("_") for part in rel_p.parts) and not md.name.startswith("_"):
            for raw_target in MD_LINK_RE.findall(text):
                target = raw_target[1:-1] if raw_target.startswith("<") else raw_target
                target = unquote(target.split("#", 1)[0]).strip()
                if (
                    not target
                    or "____" in target
                    or "<" in target
                    or SCHEME_RE.match(target)
                    or target.startswith("/")
                    or not target.endswith(".md")
                ):
                    continue
                resolved_local = (md.parent / target).resolve()
                resolved_prod = (p_root / target).resolve()
                if not resolved_local.exists() and not resolved_prod.exists():
                    problems.append(f"{prefix}{rel_repo}: broken markdown link '{target}'")

        if is_template_or_doc(rel_p):
            continue

        meta = parse_frontmatter(text)
        entry_id = str(meta.get("id") or "").strip()
        status = str(meta.get("status") or "").strip()
        top_dir = rel_p.parts[0] if rel_p.parts else ""

        if top_dir in ("1_theory", "2_calibration", "4_anomalies", "transcripts") or (
            len(rel_p.parts) >= 3 and rel_p.parts[0] == "tenants" and rel_p.parts[2] == "transcripts"
        ):
            if not entry_id:
                problems.append(f"{prefix}{rel_repo}: missing required frontmatter 'id'")
            else:
                defined_ids[entry_id] = md

        if status:
            if status not in VALID_STATUS:
                problems.append(f"{prefix}{rel_repo}: invalid status '{status}' (allowed: {sorted(VALID_STATUS)})")
            if status == "stale" and entry_id:
                stale_ids.add(entry_id)

        if top_dir == "2_calibration":
            sub_dir = rel_p.parts[1] if len(rel_p.parts) > 1 else ""
            if not status:
                problems.append(f"{prefix}{rel_repo}: missing 'status' in frontmatter")
            if sub_dir == "assets":
                if not (meta.get("asset_id") or meta.get("asset_sn")):
                    problems.append(f"{prefix}{rel_repo}: asset profile requires 'asset_id' (or 'asset_sn')")
                if status == "verified":
                    if not (meta.get("applies_to") or meta.get("applies_to_version")):
                        problems.append(f"{prefix}{rel_repo}: verified asset requires 'applies_to' or 'applies_to_version'")
                    if not meta.get("evidence"):
                        problems.append(f"{prefix}{rel_repo}: verified asset requires non-empty 'evidence'")
            elif sub_dir == "sops":
                if status == "verified" and not meta.get("applies_to"):
                    problems.append(f"{prefix}{rel_repo}: verified SOP requires 'applies_to'")

        elif top_dir == "4_anomalies":
            sub_dir = rel_p.parts[1] if len(rel_p.parts) > 1 else ""
            if sub_dir == "open":
                if status != "open":
                    problems.append(f"{prefix}{rel_repo}: open anomaly must have 'status: open'")
                if not meta.get("software_version"):
                    problems.append(f"{prefix}{rel_repo}: open anomaly requires 'software_version'")
                if not meta.get("evidence"):
                    problems.append(f"{prefix}{rel_repo}: open anomaly requires 'evidence'")
            elif sub_dir == "resolved":
                if status not in ("verified", "refuted", "stale", "conflict"):
                    problems.append(f"{prefix}{rel_repo}: resolved anomaly has invalid status '{status}'")
                if status == "verified" and not meta.get("applies_to"):
                    problems.append(f"{prefix}{rel_repo}: verified resolved anomaly requires 'applies_to'")
                if not meta.get("evidence"):
                    problems.append(f"{prefix}{rel_repo}: resolved anomaly requires 'evidence'")

        # Collect explicit [ref: <id>] & evidence IDs for existence verification
        for ref_id in ID_REF_RE.findall(text):
            if "____" not in ref_id and ref_id != "ID":
                referenced_checks.append((md, ref_id))
        ev_list = meta.get("evidence")
        if isinstance(ev_list, list):
            for ev in ev_list:
                if isinstance(ev, str) and not ev.endswith(".md") and "____" not in ev:
                    referenced_checks.append((md, ev))

    # Verify stale IDs never remain in MEMORY.md
    for sid in sorted(stale_ids):
        if sid in mem_text:
            problems.append(
                f"{prefix}{mem_file.relative_to(repo).as_posix()}: references stale entry '{sid}' (must be demoted)"
            )

    # Verify [ref: <id>] and evidence IDs exist
    for src_md, ref_id in referenced_checks:
        if ref_id not in defined_ids:
            problems.append(f"{prefix}{src_md.relative_to(repo).as_posix()}: unresolved ID reference '{ref_id}'")

    return problems, stale_ids


def run_check(repo: Path, product_filter: str | None = None) -> list[str]:
    cfg = load_config(repo)
    budgets = cfg.get("budgets") or {}
    problems: list[str] = []

    all_md = [
        f
        for f in sorted(repo.rglob("*.md"))
        if ".dream-worktree" not in f.parts and ".git" not in f.parts
    ]
    problems.extend(scan_secrets_in_files(all_md, repo))

    all_stale: set[str] = set()
    if cfg["mode"] == "hub":
        ctrl_cap = int(budgets.get("control_max_kb", 4)) * 1024
        ctrl_files: list[Path] = [repo / "0_control" / "rules.md", repo / "0_control" / "INDEX.md"]
        hosts_dir = repo / "0_control" / "hosts"
        if hosts_dir.is_dir():
            for h_dir in sorted(hosts_dir.iterdir()):
                if h_dir.is_dir() and not h_dir.name.startswith("_"):
                    ctrl_files.append(h_dir / "env.md")
        for cf in ctrl_files:
            if cf.is_file() and cf.stat().st_size > ctrl_cap:
                problems.append(
                    f"{cf.relative_to(repo).as_posix()}: {cf.stat().st_size} B exceeds control-plane cap ({ctrl_cap} B)"
                )

    for slug, p_root in product_roots(repo, cfg, product_filter=product_filter):
        prod_problems, prod_stale = check_product_tree(slug, p_root, repo, budgets)
        problems.extend(prod_problems)
        all_stale.update(prod_stale)

    if cfg["mode"] == "hub" and (repo / "0_control" / "INDEX.md").is_file():
        idx_text = (repo / "0_control" / "INDEX.md").read_text(encoding="utf-8", errors="replace")
        for sid in sorted(all_stale):
            if sid in idx_text:
                problems.append(f"0_control/INDEX.md: references stale entry '{sid}'")

    return problems


def cmd_check(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    problems = run_check(repo, product_filter=args.product)
    if problems:
        for p in problems:
            print(f"[FAIL] {p}")
        print(f"\n[aml] check failed with {len(problems)} issue(s).")
        return 1
    print(f"[aml] OK: '{repo.name}' (mode={load_config(repo)['mode']}) passed all mechanical checks.")
    return 0


def cmd_check_push(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    cfg = load_config(repo)
    remote_url = args.remote_url or ""
    if not remote_url and args.remote_name:
        rc, out = git_cmd(repo, "remote", "get-url", args.remote_name)
        if rc == 0:
            remote_url = out.strip()

    if cfg.get("private_instance"):
        blocked = cfg.get("blocked_public_remotes") or []
        for pattern in blocked:
            if pattern and pattern.lower() in remote_url.lower():
                sys.stderr.write(
                    f"[aml] BLOCKED: refusing to push private memory instance ({repo}) "
                    f"to public remote '{remote_url}'.\n"
                )
                return 1

    all_md = [f for f in repo.rglob("*.md") if ".git" not in f.parts and ".dream-worktree" not in f.parts]
    secret_hits = scan_secrets_in_files(all_md, repo)
    if secret_hits:
        sys.stderr.write("[aml] BLOCKED: pre-push secret scan detected potential credentials:\n")
        for hit in secret_hits:
            sys.stderr.write(f"  - {hit}\n")
        return 1
    return 0


# ---------------------------------------------------------------------------
# Subcommand: dream (Triage + Isolated Git Worktree + Citation Stats)
# ---------------------------------------------------------------------------


def compute_citation_stats(repo: Path, cfg: dict[str, Any], product_filter: str | None = None) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}
    roots = [p for _, p in product_roots(repo, cfg, product_filter=product_filter)]
    for p_root in roots:
        for md in p_root.rglob("*.md"):
            if ".dream-worktree" in md.parts or is_template_or_doc(md.relative_to(p_root)):
                continue
            text = md.read_text(encoding="utf-8", errors="replace")
            meta = parse_frontmatter(text)
            own_id = str(meta.get("id") or "")
            for ref in ID_REF_RE.findall(text):
                if ref != own_id and "____" not in ref:
                    counts[ref] = counts.get(ref, 0) + 1
            ref_list = meta.get("referenced_ids")
            if isinstance(ref_list, list):
                for ref in ref_list:
                    if isinstance(ref, str) and ref != own_id and "____" not in ref:
                        counts[ref] = counts.get(ref, 0) + 1
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))


def generate_triage_markdown(repo: Path, cfg: dict[str, Any], product_filter: str | None = None) -> str:
    lines = [f"# Pre-Dream Triage Summary ({dt.datetime.now().strftime('%Y-%m-%d %H:%M')})\n"]

    if cfg["mode"] == "hub" and (repo / "inbox").is_dir():
        inbox_items = sorted(f for f in (repo / "inbox").glob("*.md") if f.name != "README.md")
        lines.append("## 1. Pending Global Inbox Captures")
        if inbox_items:
            for item in inbox_items:
                meta = parse_frontmatter(item.read_text(encoding="utf-8", errors="replace"))
                hint = meta.get("product_hint") or "unassigned"
                lines.append(f"- [ ] `inbox/{item.name}` (product_hint: `{hint}`) -> route or discard")
        else:
            lines.append("- None")
        lines.append("")

    lines.append("## 2. Product Transcripts, Open Anomalies & Unchecked Cascades")
    for slug, p_root in product_roots(repo, cfg, product_filter=product_filter):
        trs = sorted(
            f for f in (p_root / "transcripts").glob("*.md")
            if not f.name.startswith("_") and f.name != "README.md"
        ) if (p_root / "transcripts").is_dir() else []
        opens = sorted(
            f for f in (p_root / "4_anomalies" / "open").glob("*.md")
            if not f.name.startswith("_")
        ) if (p_root / "4_anomalies" / "open").is_dir() else []
        pending_cascades: list[Path] = []
        res_dir = p_root / "4_anomalies" / "resolved"
        if res_dir.is_dir():
            for rf in sorted(res_dir.glob("*.md")):
                if rf.name.startswith("_"):
                    continue
                meta = parse_frontmatter(rf.read_text(encoding="utf-8", errors="replace"))
                if meta.get("cascade_checked") is False:
                    pending_cascades.append(rf)

        lines.append(f"### Product: `{slug}`")
        lines.append(f"- Transcripts on file: `{len(trs)}` | Open anomalies: `{len(opens)}` | Pending 4-way cascades: `{len(pending_cascades)}`")
        for op in opens:
            lines.append(f"  - [ ] Open anomaly `{op.name}` -> keep `open` or promote to `resolved`?")
        for pc in pending_cascades:
            lines.append(f"  - [ ] Resolved `{pc.name}` (`cascade_checked: false`) -> run L4->L1/L2/L3 audit")
    return "\n".join(lines) + "\n"


def cmd_dream(args: argparse.Namespace) -> int:
    repo = Path(args.repo).resolve()
    cfg = load_config(repo)
    wt_dir = repo / ".dream-worktree"
    stamp = dt.datetime.now().strftime("%Y%m%d")
    branch = f"dream/{stamp}"

    if args.action == "stats":
        for ref_id, cnt in compute_citation_stats(repo, cfg, args.product):
            print(f"{cnt:4d}  {ref_id}")
        return 0

    if args.action == "triage":
        report = generate_triage_markdown(repo, cfg, args.product)
        (repo / "triage-list.md").write_text(report, encoding="utf-8")
        print(report)
        return 0

    if args.action == "start":
        if wt_dir.exists():
            sys.stderr.write(f"[aml] worktree {wt_dir} already exists; run `aml dream clean` first.\n")
            return 1
        rc, out = git_cmd(repo, "worktree", "add", "-B", branch, str(wt_dir), "HEAD")
        if rc != 0:
            sys.stderr.write(f"[aml] failed to create git worktree: {out}\n")
            return 1
        wt_cfg = load_config(wt_dir)
        stats = compute_citation_stats(wt_dir, wt_cfg, args.product)
        stats_lines = [f"# Citation Frequency Report ({dt.datetime.now().isoformat(timespec='seconds')})"]
        stats_lines.extend(f"{cnt:4d}  {ref_id}" for ref_id, cnt in stats)
        (wt_dir / "reference-stats.txt").write_text("\n".join(stats_lines) + "\n", encoding="utf-8")
        (wt_dir / "triage-list.md").write_text(generate_triage_markdown(wt_dir, wt_cfg, args.product), encoding="utf-8")
        print(f"[aml] created isolated dreaming worktree: {wt_dir} (branch: {branch})")
        print(f"[aml] wrote {wt_dir / 'reference-stats.txt'} and {wt_dir / 'triage-list.md'}")
        print("[aml] next: let the consolidation agent edit files inside .dream-worktree, then run `aml dream diff`.")
        return 0

    if args.action == "diff":
        if not wt_dir.exists():
            sys.stderr.write(f"[aml] no active dreaming worktree at {wt_dir}\n")
            return 1
        changelog = wt_dir / "change-log.md"
        if changelog.is_file():
            print("==================== change-log.md ====================")
            print(changelog.read_text(encoding="utf-8", errors="replace"))
            print("=======================================================")
        problems = run_check(wt_dir, product_filter=args.product)
        if problems:
            print("[aml] WARNING: mechanical check reported issues in .dream-worktree:")
            for p in problems:
                print(f"  - {p}")
        else:
            print("[aml] mechanical check on .dream-worktree: OK (0 issues)")
        _, st = git_cmd(wt_dir, "status", "-s")
        if st:
            print(st)
        _, diff_out = git_cmd(wt_dir, "diff")
        if diff_out:
            print(diff_out)
        return 1 if problems else 0

    if args.action == "clean":
        if wt_dir.exists():
            rc, out = git_cmd(repo, "worktree", "remove", "--force", str(wt_dir))
            if rc != 0:
                sys.stderr.write(f"[aml] failed to remove worktree: {out}\n")
                return 1
            print(f"[aml] cleaned {wt_dir} (branch '{branch}' kept for git merge or git branch -D).")
        else:
            print("[aml] nothing to clean.")
        return 0

    return 1


# ---------------------------------------------------------------------------
# Subcommand: eval (Deterministic Rubric & Ablation Scorer)
# ---------------------------------------------------------------------------


_CLAUSE_NORM_TABLE = str.maketrans(
    {
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u00a0": " ",
        "\u202f": " ",
        "\u2009": " ",
        "\u3000": " ",
        "\u00b5": "μ",
    }
)


def _normalize_for_regex(text: str) -> str:
    return re.sub(r"\s+", " ", text.translate(_CLAUSE_NORM_TABLE))


def _normalize_literal(text: str) -> str:
    norm = _normalize_for_regex(text)
    return re.sub(r"\s*-\s*", "-", norm).lower()


def _clause_matches(clause: str, text: str) -> bool:
    """Match a rubric anchor clause against response text.

    Supports:
      - `re:<pattern>` for explicit case-insensitive regular expressions
      - `<alt1>|<alt2>` pipe-separated lexical alternatives to avoid false negatives
        from surface wording or Unicode dash/space/micro differences while keeping
        grading deterministic.
    """
    spec = clause.strip()
    if not spec:
        return True
    if spec.startswith("re:"):
        return bool(re.search(spec[3:], _normalize_for_regex(text), flags=re.IGNORECASE))
    norm_text = _normalize_literal(text)
    for alt in spec.split("|"):
        token = _normalize_literal(alt.strip())
        if token and token in norm_text:
            return True
    return False


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{lineno}: invalid JSON ({exc})") from exc
        if not isinstance(obj, dict):
            raise ValueError(f"{path}:{lineno}: expected JSON object")
        rows.append(obj)
    return rows


def grade_response(case: dict[str, Any], response_text: str) -> dict[str, Any]:
    """Grade one model response against a case definition with hard-gate priority."""
    must_hit: list[str] = list(case.get("must_hit_anchors") or case.get("must_hit") or [])
    must_not_hit: list[str] = list(case.get("must_not_hit") or [])

    matched: list[str] = []
    missed: list[str] = []
    for clause in must_hit:
        if _clause_matches(clause, response_text):
            matched.append(clause)
        else:
            missed.append(clause)

    forbidden_hits: list[str] = [
        clause for clause in must_not_hit if _clause_matches(clause, response_text)
    ]

    raw_coverage = (len(matched) / len(must_hit)) if must_hit else 1.0
    if forbidden_hits:
        # Hard gate before weighted scoring: safety / refuted violations score 0.0
        passed = False
        score = 0.0
        outcome = "HARD_GATE_VIOLATION"
    elif not missed:
        passed = True
        score = 1.0
        outcome = "PASS"
    else:
        passed = False
        score = round(raw_coverage, 4)
        outcome = "PARTIAL" if matched else "MISS"

    return {
        "id": case.get("id", ""),
        "category": case.get("category", "general"),
        "passed": passed,
        "score": score,
        "raw_coverage": round(raw_coverage, 4),
        "outcome": outcome,
        "matched": matched,
        "missed": missed,
        "forbidden_hits": forbidden_hits,
    }


def evaluate_ablation(
    cases: list[dict[str, Any]],
    responses: list[dict[str, Any]],
) -> dict[str, Any]:
    case_map = {str(c["id"]): c for c in cases if "id" in c}
    arms: dict[str, list[dict[str, Any]]] = {}

    for row in responses:
        cid = str(row.get("id") or "")
        if cid not in case_map:
            continue
        arm = str(row.get("arm") or "default")
        graded = grade_response(case_map[cid], str(row.get("response") or ""))
        if "tokens" in row and row["tokens"] is not None:
            graded["tokens"] = int(row["tokens"])
        if "turns" in row and row["turns"] is not None:
            graded["turns"] = int(row["turns"])
        arms.setdefault(arm, []).append(graded)

    summary: dict[str, Any] = {}
    for arm, items in sorted(arms.items()):
        n = len(items)
        passes = sum(1 for it in items if it["passed"])
        violations = sum(1 for it in items if it["outcome"] == "HARD_GATE_VIOLATION")
        mean_score = sum(it["score"] for it in items) / n if n else 0.0
        tok_vals = [it["tokens"] for it in items if "tokens" in it]
        turn_vals = [it["turns"] for it in items if "turns" in it]
        summary[arm] = {
            "cases_evaluated": n,
            "cases_total": len(case_map),
            "pass_count": passes,
            "pass_rate": round(passes / n, 4) if n else 0.0,
            "mean_score": round(mean_score, 4),
            "hard_gate_violations": violations,
            "mean_tokens": round(sum(tok_vals) / len(tok_vals), 1) if tok_vals else None,
            "mean_turns": round(sum(turn_vals) / len(turn_vals), 2) if turn_vals else None,
            "results": items,
        }

    return {"total_cases": len(case_map), "arms": summary}


def cmd_eval(args: argparse.Namespace) -> int:
    cases_path = Path(args.cases).resolve()
    resp_path = Path(args.responses).resolve()
    if not cases_path.is_file():
        sys.stderr.write(f"[aml] cases file not found: {cases_path}\n")
        return 1
    if not resp_path.is_file():
        sys.stderr.write(f"[aml] responses file not found: {resp_path}\n")
        return 1

    try:
        cases = load_jsonl(cases_path)
        responses = load_jsonl(resp_path)
    except ValueError as exc:
        sys.stderr.write(f"[aml] {exc}\n")
        return 1

    report = evaluate_ablation(cases, responses)
    if args.json_out:
        out_path = Path(args.json_out).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"[aml] Ablation Evaluation ({report['total_cases']} benchmark cases)")
    print(f"{'Arm':<10} {'Pass':<10} {'PassRate':<10} {'MeanScore':<11} {'GateViol':<10} {'AvgTurns':<10} {'AvgTokens':<10}")
    print("-" * 74)
    for arm, stats in report["arms"].items():
        pass_str = f"{stats['pass_count']}/{stats['cases_evaluated']}"
        rate_str = f"{stats['pass_rate'] * 100:.1f}%"
        score_str = f"{stats['mean_score']:.3f}"
        turns_str = f"{stats['mean_turns']:.1f}" if stats["mean_turns"] is not None else "-"
        toks_str = f"{stats['mean_tokens']:.0f}" if stats["mean_tokens"] is not None else "-"
        print(
            f"{arm:<10} {pass_str:<10} {rate_str:<10} {score_str:<11} "
            f"{stats['hard_gate_violations']:<10} {turns_str:<10} {toks_str:<10}"
        )
        if args.verbose:
            for item in stats["results"]:
                tag = item["outcome"]
                detail = ""
                if item["forbidden_hits"]:
                    detail = f" forbidden={item['forbidden_hits']}"
                elif item["missed"]:
                    detail = f" missed={item['missed']}"
                print(f"  - [{tag}] {item['id']} ({item['category']}): score={item['score']:.2f}{detail}")

    if args.min_pass_rate is not None:
        target_arm = args.require_arm
        if target_arm:
            arms_to_check = {target_arm: report["arms"].get(target_arm)}
        else:
            arms_to_check = report["arms"]
        for arm_name, st in arms_to_check.items():
            if st is None or st["pass_rate"] < args.min_pass_rate or st["hard_gate_violations"] > 0:
                return 1
    return 0


# ---------------------------------------------------------------------------
# Argument Parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="aml", description="agent-memory-layers CLI & lifecycle engine")
    sub = p.add_subparsers(dest="subcmd", required=True)

    p_init = sub.add_parser("init", help="Scaffold a standalone or hub memory repository")
    p_init.add_argument("target", help="Target directory path")
    p_init.add_argument("--mode", choices=["standalone", "hub"], default="standalone")
    p_init.add_argument("--products", help="Comma-separated initial product slugs (hub mode)")
    p_init.add_argument("--private", action="store_true", help="Mark instance private to block public remote pushes")
    p_init.set_defaults(func=cmd_init)

    p_inst = sub.add_parser("install", help="Install startup instructions and hooks for an AI agent tool")
    p_inst.add_argument("--repo", default=".", help="Path to the memory repository")
    p_inst.add_argument("--tool", choices=["claude", "codex", "antigravity", "gemini", "kimi", "generic"], required=True)
    p_inst.add_argument("--target", help="Custom instruction file path (required for --tool generic)")
    p_inst.add_argument("--host", help="Override short host identifier")
    p_inst.add_argument("--agent-id", help="Override agent instance identifier")
    p_inst.set_defaults(func=cmd_install)

    p_uninst = sub.add_parser("uninstall", help="Remove AML instructions and hooks for an AI agent tool")
    p_uninst.add_argument("--repo", default=".", help="Path to the memory repository")
    p_uninst.add_argument("--tool", choices=["claude", "codex", "antigravity", "gemini", "kimi", "generic"], required=True)
    p_uninst.add_argument("--target", help="Custom instruction file path")
    p_uninst.set_defaults(func=cmd_uninstall)

    p_start = sub.add_parser("start", help="Print progressive context manifest for a session")
    p_start.add_argument("--repo", default=".", help="Path to the memory repository")
    p_start.add_argument("--cwd", help="Active workspace directory for automatic product routing")
    p_start.add_argument("--host", help="Host identifier")
    p_start.add_argument("--agent", help="Agent identifier")
    p_start.add_argument("--pull", action="store_true", help="Pull latest commits with rebase before building manifest")
    p_start.set_defaults(func=cmd_start)

    p_hstart = sub.add_parser("hook-start", help="Lifecycle SessionStart / PreInvocation JSON hook")
    p_hstart.add_argument("--repo", required=True)
    p_hstart.add_argument("--host")
    p_hstart.add_argument("--agent")
    p_hstart.add_argument("--format", choices=["antigravity", "claude", "plain"], default="plain")
    p_hstart.set_defaults(func=cmd_hook_start)

    p_cap = sub.add_parser("capture", help="Create a collision-free append-only capture file")
    p_cap.add_argument("--repo", default=".")
    p_cap.add_argument("--kind", choices=["inbox", "transcript", "anomaly"], required=True)
    p_cap.add_argument("--product", help="Target product slug (hub mode)")
    p_cap.add_argument("--tenant", help="Optional tenant code")
    p_cap.add_argument("--version", help="Software/firmware version")
    p_cap.add_argument("--title", required=True, help="Short factual title")
    p_cap.add_argument("--slug", help="Optional ASCII filename slug")
    p_cap.add_argument("--host")
    p_cap.add_argument("--agent")
    p_cap.set_defaults(func=cmd_capture)

    p_sync = sub.add_parser("sync", help="Commit and push safe append-only capture directories")
    p_sync.add_argument("--repo", default=".")
    p_sync.add_argument("--host")
    p_sync.add_argument("--agent")
    p_sync.add_argument("--no-push", action="store_true")
    p_sync.set_defaults(func=cmd_sync)

    p_hstop = sub.add_parser("hook-stop", help="Lifecycle Stop JSON hook")
    p_hstop.add_argument("--repo", required=True)
    p_hstop.add_argument("--host")
    p_hstop.add_argument("--agent")
    p_hstop.set_defaults(func=cmd_hook_stop)

    p_search = sub.add_parser("search", help="Product- and tenant-isolated regex search")
    p_search.add_argument("--repo", default=".")
    p_search.add_argument("--product", help="Scope search to a single product (hub mode)")
    p_search.add_argument("--tenant", help="Mount a specific tenant partition")
    p_search.add_argument("query", help="Keyword or regular expression")
    p_search.set_defaults(func=cmd_search)

    p_dream = sub.add_parser("dream", help="Dual-gate offline consolidation worktree manager")
    p_dream.add_argument("action", choices=["triage", "start", "diff", "clean", "stats"])
    p_dream.add_argument("--repo", default=".")
    p_dream.add_argument("--product", help="Filter stats/triage/check to a single product")
    p_dream.set_defaults(func=cmd_dream)

    p_check = sub.add_parser("check", help="Zero-token mechanical layout, schema, link, stale & secret check")
    p_check.add_argument("--repo", default=".")
    p_check.add_argument("--product", help="Check a single product")
    p_check.set_defaults(func=cmd_check)

    p_cpush = sub.add_parser("check-push", help="Git pre-push safety guard")
    p_cpush.add_argument("--repo", default=".")
    p_cpush.add_argument("--remote-name", default="")
    p_cpush.add_argument("--remote-url", default="")
    p_cpush.set_defaults(func=cmd_check_push)

    p_eval = sub.add_parser("eval", help="Deterministic rubric & ablation scorer for eval/cases.jsonl")
    p_eval.add_argument("--cases", required=True, help="Path to benchmark cases.jsonl")
    p_eval.add_argument("--responses", required=True, help="Path to model responses.jsonl")
    p_eval.add_argument("--json-out", help="Optional path to write full JSON evaluation report")
    p_eval.add_argument("--verbose", "-v", action="store_true", help="Print per-case pass/miss/violation details")
    p_eval.add_argument("--require-arm", help="Arm name to enforce --min-pass-rate against (e.g. C)")
    p_eval.add_argument("--min-pass-rate", type=float, help="Fail with exit code 1 if pass rate is below threshold")
    p_eval.set_defaults(func=cmd_eval)

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
