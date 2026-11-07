import os
import re
import json
import math
import pytest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_path(rel_path: str) -> str:
    return os.path.join(ROOT_DIR, rel_path)

def test_docker_compose_and_dockerfile():
    compose_path = get_path("docker-compose.yml")
    dockerfile_path = get_path("Dockerfile")
    assert os.path.exists(compose_path), "docker-compose.yml must exist"
    assert os.path.exists(dockerfile_path), "Dockerfile must exist"
    
    with open(compose_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "api:" in content, "api service must exist in docker-compose.yml"
    assert "ledger:" in content, "ledger service must exist in docker-compose.yml"
    assert "healthcheck:" in content, "healthchecks must be configured"
    assert "pg_isready" in content, "ledger must use pg_isready"
    assert "/health" in content, "api must check /health"

def test_env_example():
    env_example = get_path(".env.example")
    assert os.path.exists(env_example), ".env.example must exist"
    with open(env_example, "r", encoding="utf-8") as f:
        content = f.read()
    required_keys = [
        "CELESTO_PROVIDER", "CELESTO_API_KEY", "LLM_API_KEY",
        "LLM_MODEL", "DATABASE_URL", "API_PORT"
    ]
    for key in required_keys:
        assert key in content, f"Key {key} must be in .env.example"

def test_problem_report():
    path = get_path("reports/problem.json")
    assert os.path.exists(path), "reports/problem.json must exist"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert len(data.get("who", "")) >= 40
    assert len(data.get("agent_work", "")) >= 40
    assert len(data.get("proof_output", "")) >= 20
    assert data.get("idea_source") in ("idea_bank", "original")

def test_commands_audit_log():
    path = get_path("logs/commands.jsonl")
    assert os.path.exists(path), "logs/commands.jsonl must exist"
    sandbox_re = re.compile(r"^sbx-[a-z0-9]{8,}$")
    
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
        
    assert len(lines) > 0, "logs/commands.jsonl must have at least one line"
    for line in lines:
        entry = json.loads(line)
        assert "ts" in entry
        assert sandbox_re.match(entry["sandbox_name"])
        assert len(entry["command"]) > 0
        assert entry["decision"] in ("allow", "block")
        assert entry["execution_target"] == "celesto_sandbox"

def test_capabilities_report():
    path = get_path("reports/capabilities.json")
    assert os.path.exists(path), "reports/capabilities.json must exist"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    caps = data.get("capabilities", [])
    assert len(caps) >= 2, "Must declare at least two capabilities"
    allowed_ids = {
        "persistence", "snapshots", "celestofs", "browser", "published_ports",
        "network_policy", "safety_hooks", "host_mounts", "coding_agent_preset", "agentor_durable"
    }
    seen_ids = set()
    for cap in caps:
        cap_id = cap["id"]
        assert cap_id in allowed_ids, f"Invalid capability {cap_id}"
        assert cap_id not in seen_ids, f"Duplicate capability {cap_id}"
        seen_ids.add(cap_id)
        assert len(cap["why"]) >= 80
        assert os.path.exists(get_path(cap["evidence_path"]))

def test_lifecycle_report():
    path = get_path("reports/lifecycle.json")
    assert os.path.exists(path), "reports/lifecycle.json must exist"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    assert data.get("cleanup_on_success") is True
    assert data.get("cleanup_on_failure") is True
    assert data.get("cleanup_on_interrupt") is True
    names = data.get("sandbox_names", [])
    assert len(names) > 0
    sandbox_re = re.compile(r"^sbx-[a-z0-9]{8,}$")
    for name in names:
        assert sandbox_re.match(name)

def test_reliability_report_and_arithmetic():
    path = get_path("reports/reliability.json")
    assert os.path.exists(path), "reports/reliability.json must exist"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    runs = data.get("runs", [])
    run_count = data.get("run_count", 0)
    assert run_count == len(runs)
    assert run_count >= 20
    
    sandbox_re = re.compile(r"^sbx-[a-z0-9]{8,}$")
    seen_names = set()
    success_count = 0
    for r in runs:
        assert r["fresh"] is True
        assert sandbox_re.match(r["sandbox_name"])
        assert r["sandbox_name"] not in seen_names
        seen_names.add(r["sandbox_name"])
        assert r["wall_clock_s"] >= 0
        assert r["boot_to_ready_s"] >= 0
        assert r["cost_usd"] >= 0
        if r["success"]:
            success_count += 1
            
    expected_success_rate = success_count / float(run_count)
    assert abs(data["success_rate"] - expected_success_rate) <= 0.001
    
    sorted_wall = sorted(r["wall_clock_s"] for r in runs)
    mid1, mid2 = sorted_wall[9], sorted_wall[10]
    expected_median_wall = (mid1 + mid2) / 2.0
    assert abs(data["median_wall_clock_s"] - expected_median_wall) <= 0.001
    
    p90_idx = math.ceil(0.90 * run_count) - 1 # 18th value, 0-indexed: 17
    assert abs(data["p90_wall_clock_s"] - sorted_wall[p90_idx]) <= 0.001
    
    sorted_boot = sorted(r["boot_to_ready_s"] for r in runs)
    expected_median_boot = (sorted_boot[9] + sorted_boot[10]) / 2.0
    assert abs(data["median_boot_to_ready_s"] - expected_median_boot) <= 0.001
    
    expected_total_cost = sum(r["cost_usd"] for r in runs)
    assert abs(data["total_cost_usd"] - expected_total_cost) <= 0.01
    
    postmortem_path = get_path(data["postmortem_path"])
    assert os.path.exists(postmortem_path)
    with open(postmortem_path, "r", encoding="utf-8") as pf:
        assert len(pf.read()) >= 200

def test_containment_report():
    path = get_path("reports/containment.json")
    assert os.path.exists(path), "reports/containment.json must exist"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("attack") in ("prompt_injection_exfil", "destructive_command", "suspicious_package")
    assert data.get("blocked") is True
    assert data.get("host_untouched") is True
    for ep in data.get("evidence_paths", []):
        assert os.path.exists(get_path(ep))

def test_failure_policy_report():
    path = get_path("reports/failure_policy.json")
    assert os.path.exists(path), "reports/failure_policy.json must exist"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data.get("failed_step") == 7
    assert data.get("total_steps") == 10
    policy = data.get("policy")
    assert policy in ("resume", "rollback", "fresh")
    assert len(data.get("rationale", "")) >= 200
    
    trace_path = get_path(data.get("trace_path"))
    assert os.path.exists(trace_path)
    found_event = False
    with open(trace_path, "r", encoding="utf-8") as tf:
        for line in tf:
            if line.strip():
                item = json.loads(line)
                if item.get("event") == "policy_applied" and item.get("policy") == policy:
                    found_event = True
                    break
    assert found_event, "Matching policy_applied line must exist in trace"

def test_concurrency_report():
    path = get_path("reports/concurrency.json")
    assert os.path.exists(path), "reports/concurrency.json must exist"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    jobs = data.get("jobs", [])
    assert len(jobs) >= 5
    sandbox_re = re.compile(r"^sbx-[a-z0-9]{8,}$")
    seen_names = set()
    for job in jobs:
        name = job["sandbox_name"]
        assert sandbox_re.match(name)
        assert name not in seen_names
        seen_names.add(name)
        assert len(job["started_at"]) > 0
    assert len(data.get("breakage_notes", "")) >= 40

def test_readme_phrases():
    path = get_path("README.md")
    assert os.path.exists(path), "README.md must exist"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    required_phrases = [
        "Problem statement",
        "How I used Celesto",
        "Eval report",
        "Containment test",
        "State and failure design",
        "Setup"
    ]
    for phrase in required_phrases:
        assert phrase in content, f"README must contain phrase '{phrase}'"
