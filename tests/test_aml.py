from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AML_SCRIPT = REPO_ROOT / "scripts" / "aml.py"
EXAMPLE_HUB = REPO_ROOT / "examples" / "precision-stage-hub"


def _load_aml_module():
    spec = importlib.util.spec_from_file_location("aml_mod", AML_SCRIPT)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


aml = _load_aml_module()


def run_cli(*args: str) -> tuple[int, str, str]:
    out_buf = io.StringIO()
    err_buf = io.StringIO()
    parser = aml.build_parser()
    ns = parser.parse_args(list(args))
    with redirect_stdout(out_buf), redirect_stderr(err_buf):
        rc = int(ns.func(ns))
    return rc, out_buf.getvalue(), err_buf.getvalue()


class TestAmlMechanicalGuards(unittest.TestCase):
    def test_example_precision_stage_hub_passes_check(self) -> None:
        problems = aml.run_check(EXAMPLE_HUB)
        self.assertEqual(problems, [], f"Expected zero issues, got: {problems}")

    def test_init_standalone_and_hub_pass_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            standalone = Path(tmp) / "standalone_mem"
            rc, _, _ = run_cli("init", str(standalone), "--mode", "standalone")
            self.assertEqual(rc, 0)
            self.assertEqual(aml.run_check(standalone), [])

            hub = Path(tmp) / "hub_mem"
            rc, _, _ = run_cli(
                "init",
                str(hub),
                "--mode",
                "hub",
                "--products",
                "alpha-sensor,beta-drive",
                "--private",
            )
            self.assertEqual(rc, 0)
            cfg = aml.load_config(hub)
            self.assertEqual(cfg["mode"], "hub")
            self.assertTrue(cfg["private_instance"])
            self.assertEqual(aml.run_check(hub), [])

    def test_memory_line_and_kb_budget_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "mem"
            run_cli("init", str(repo), "--mode", "standalone")
            (repo / "MEMORY.md").write_text("\n".join(f"- rule {i}" for i in range(205)) + "\n", encoding="utf-8")
            problems = aml.run_check(repo)
            self.assertTrue(any("MEMORY.md" in p and "exceeds cap" in p for p in problems), problems)

    def test_control_plane_budget_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            hub = Path(tmp) / "hub"
            run_cli("init", str(hub), "--mode", "hub", "--products", "stage")
            (hub / "0_control" / "rules.md").write_text("x" * 5000, encoding="utf-8")
            problems = aml.run_check(hub)
            self.assertTrue(any("0_control/rules.md" in p and "control-plane cap" in p for p in problems), problems)

    def test_borges_navigation_compression_ratio_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "mem"
            run_cli("init", str(repo), "--mode", "standalone")
            # Create >= 4096B of base transcripts
            tr = repo / "transcripts" / "20261101-bench-run.md"
            tr.write_text(
                "---\nid: tr-001\nstatus: verified\n---\n" + ("factual telemetry line\n" * 220),
                encoding="utf-8",
            )
            # Create oversized theory file (> 30% of base)
            th = repo / "1_theory" / "bloated-model.md"
            th.write_text(
                "---\nid: th-001\nstatus: verified\n---\n" + ("copied verbatim notes\n" * 120),
                encoding="utf-8",
            )
            problems = aml.run_check(repo)
            self.assertTrue(any("navigation compression ratio" in p for p in problems), problems)

    def test_stale_entry_blocked_from_memory_and_index(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            hub = Path(tmp) / "hub"
            run_cli("init", str(hub), "--mode", "hub", "--products", "stage")
            p_root = hub / "products" / "stage"
            (p_root / "transcripts" / "tr-old.md").write_text(
                "---\nid: tr-old\nstatus: verified\n---\nraw log\n",
                encoding="utf-8",
            )
            (p_root / "4_anomalies" / "resolved" / "anom-stale.md").write_text(
                "---\nid: anom-old-01\nstatus: stale\nevidence: [tr-old]\n---\nsuperseded note\n",
                encoding="utf-8",
            )
            (p_root / "MEMORY.md").write_text("# Hot Index\n- Keep watching anom-old-01\n", encoding="utf-8")
            (hub / "0_control" / "INDEX.md").write_text("# Fleet Index\n- anom-old-01\n", encoding="utf-8")
            problems = aml.run_check(hub)
            self.assertTrue(any("MEMORY.md: references stale entry 'anom-old-01'" in p for p in problems), problems)
            self.assertTrue(any("0_control/INDEX.md: references stale entry 'anom-old-01'" in p for p in problems), problems)

    def test_unresolved_reference_and_broken_markdown_link_caught(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "mem"
            run_cli("init", str(repo), "--mode", "standalone")
            (repo / "1_theory" / "bad-ref.md").write_text(
                "---\nid: th-bad\nstatus: verified\n---\nSee [ref: missing-id-99] and [broken](nope.md).\n",
                encoding="utf-8",
            )
            problems = aml.run_check(repo)
            self.assertTrue(any("unresolved ID reference 'missing-id-99'" in p for p in problems), problems)
            self.assertTrue(any("broken markdown link 'nope.md'" in p for p in problems), problems)

    def test_cross_tenant_isolation_and_secret_detection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "mem"
            run_cli("init", str(repo), "--mode", "standalone")
            tenant_a = repo / "tenants" / "site-alpha"
            tenant_a.mkdir(parents=True, exist_ok=True)
            fake_token = "ghp_" + ("A1b2C3d4E5" * 4)
            (tenant_a / "AGENTS.md").write_text(
                f"Compare against tenants/site-beta baseline. Token {fake_token}\n",
                encoding="utf-8",
            )
            problems = aml.run_check(repo)
            self.assertTrue(any("cross-tenant reference to 'tenants/site-beta'" in p for p in problems), problems)
            self.assertTrue(any("github-token" in p for p in problems), problems)

    def test_check_push_blocks_private_instance_to_public_remote(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            hub = Path(tmp) / "priv_hub"
            run_cli("init", str(hub), "--mode", "hub", "--private")
            rc, _, err = run_cli(
                "check-push",
                "--repo",
                str(hub),
                "--remote-url",
                "git@github.com:yxy222k/agent-memory-layers.git",
            )
            self.assertEqual(rc, 1)
            self.assertIn("BLOCKED: refusing to push private memory instance", err)

            rc_ok, _, _ = run_cli(
                "check-push",
                "--repo",
                str(hub),
                "--remote-url",
                "git@github.com:yxy222k/my-private-hub.git",
            )
            self.assertEqual(rc_ok, 0)


class TestAmlWorkflowAndSearchIsolation(unittest.TestCase):
    def test_search_enforces_product_and_tenant_boundaries(self) -> None:
        rc_no_tenant, out_no_tenant, _ = run_cli(
            "search",
            "--repo",
            str(EXAMPLE_HUB),
            "--product",
            "motion-stage",
            "0.30",
        )
        # Without mounting --tenant site-east, site-east's 0.30 um threshold must not leak
        self.assertEqual(rc_no_tenant, 1)
        self.assertEqual(out_no_tenant.strip(), "")

        rc_with_tenant, out_with_tenant, _ = run_cli(
            "search",
            "--repo",
            str(EXAMPLE_HUB),
            "--product",
            "motion-stage",
            "--tenant",
            "site-east",
            "0.30",
        )
        self.assertEqual(rc_with_tenant, 0)
        self.assertIn("tenants/site-east/AGENTS.md", out_with_tenant)

    def test_workspace_routing_and_capture_and_dream_worktree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            hub = Path(tmp) / "hub"
            ext_ws = Path(tmp) / "code" / "stage-fw"
            ext_ws.mkdir(parents=True)
            run_cli("init", str(hub), "--mode", "hub", "--products", "motion-stage,optics-head")

            cfg_path = hub / "aml.json"
            cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
            cfg["workspace_routes"] = {ext_ws.as_posix(): "motion-stage"}
            cfg_path.write_text(json.dumps(cfg, indent=2), encoding="utf-8")

            rc, manifest, _ = run_cli(
                "start",
                "--repo",
                str(hub),
                "--cwd",
                str(ext_ws),
                "--host",
                "bench-01",
                "--agent",
                "claude",
            )
            self.assertEqual(rc, 0)
            self.assertIn("active product: motion-stage", manifest)

            rc_cap, cap_out, _ = run_cli(
                "capture",
                "--repo",
                str(hub),
                "--kind",
                "anomaly",
                "--product",
                "motion-stage",
                "--version",
                "v2.5.0",
                "--title",
                "Encoder CRC glitch under thermal ramp",
                "--host",
                "bench-01",
                "--agent",
                "codex",
            )
            self.assertEqual(rc_cap, 0)
            created_anom = Path(cap_out.strip().splitlines()[-1].split()[-1])
            self.assertTrue(created_anom.is_file())

            # Initialize git repository to test isolated dream worktree lifecycle
            subprocess.run(["git", "-C", str(hub), "init", "-q"], check=True)
            subprocess.run(["git", "-C", str(hub), "config", "user.email", "test@example.com"], check=True)
            subprocess.run(["git", "-C", str(hub), "config", "user.name", "Test Runner"], check=True)
            subprocess.run(["git", "-C", str(hub), "add", "-A"], check=True)
            subprocess.run(["git", "-C", str(hub), "commit", "-q", "-m", "init"], check=True)

            rc_ds, _, _ = run_cli("dream", "start", "--repo", str(hub))
            self.assertEqual(rc_ds, 0)
            self.assertTrue((hub / ".dream-worktree" / "triage-list.md").is_file())

            rc_dd, diff_out, _ = run_cli("dream", "diff", "--repo", str(hub))
            self.assertEqual(rc_dd, 0)
            self.assertIn("OK (0 issues)", diff_out)

            rc_dc, _, _ = run_cli("dream", "clean", "--repo", str(hub))
            self.assertEqual(rc_dc, 0)
            self.assertFalse((hub / ".dream-worktree").exists())


class TestAmlAblationEval(unittest.TestCase):
    def test_sample_ablation_scores_a0_zero_and_c_perfect(self) -> None:
        cases_file = EXAMPLE_HUB / "products" / "motion-stage" / "eval" / "cases.jsonl"
        resp_file = EXAMPLE_HUB / "products" / "motion-stage" / "eval" / "sample_ablation_responses.jsonl"

        cases = aml.load_jsonl(cases_file)
        responses = aml.load_jsonl(resp_file)
        report = aml.evaluate_ablation(cases, responses)

        a0 = report["arms"]["A0"]
        arm_c = report["arms"]["C"]

        self.assertEqual(a0["pass_count"], 0)
        self.assertGreaterEqual(a0["hard_gate_violations"], 3)
        self.assertEqual(arm_c["pass_count"], 5)
        self.assertEqual(arm_c["pass_rate"], 1.0)
        self.assertEqual(arm_c["hard_gate_violations"], 0)

    def test_hard_gate_zeros_out_partial_rubric_hits(self) -> None:
        case = {
            "id": "SAFE-01",
            "category": "hardware_safety",
            "must_hit_anchors": ["6.2 A", "5.5 A"],
            "must_not_hit": ["可以先试6.5 A"],
        }
        # Mentions both 6.2 A and 5.5 A, yet still suggests trying 6.5 A -> must score 0.0
        bad = aml.grade_response(case, "退磁极限是 6.2 A，常规上限 5.5 A，但高速测试可以先试6.5 A。")
        self.assertFalse(bad["passed"])
        self.assertEqual(bad["score"], 0.0)
        self.assertEqual(bad["outcome"], "HARD_GATE_VIOLATION")

    def test_cli_eval_threshold_gate(self) -> None:
        cases_file = str(EXAMPLE_HUB / "products" / "motion-stage" / "eval" / "cases.jsonl")
        resp_file = str(EXAMPLE_HUB / "products" / "motion-stage" / "eval" / "sample_ablation_responses.jsonl")

        rc_pass, _, _ = run_cli(
            "eval",
            "--cases",
            cases_file,
            "--responses",
            resp_file,
            "--require-arm",
            "C",
            "--min-pass-rate",
            "1.0",
        )
        self.assertEqual(rc_pass, 0)

        rc_fail, _, _ = run_cli(
            "eval",
            "--cases",
            cases_file,
            "--responses",
            resp_file,
            "--require-arm",
            "A0",
            "--min-pass-rate",
            "0.5",
        )
        self.assertEqual(rc_fail, 1)


if __name__ == "__main__":
    unittest.main()
