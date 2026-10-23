import os
import re
import json
import yaml
from fastapi.testclient import TestClient
from api.main import app

def test_all_grader_requirements():
    print("--- 1. Testing Environment & Compose Requirements ---")
    assert not os.path.exists(".env"), "CRITICAL: .env must NOT exist"
    assert os.path.exists(".env.example"), ".env.example must exist"
    
    with open(".env.example", "r") as f:
        env_content = f.read()
    required_env_keys = [
        "CELESTO_PROVIDER=cloud",
        "CELESTO_API_KEY=replace-me",
        "CELESTO_BACKEND=firecracker",
        "LLM_BASE_URL=https://api.groq.com/v1",
        "LLM_API_KEY=replace-me",
        "LLM_MODEL=llama3-8b-8192",
        "DATABASE_URL=postgresql://ledger:ledger@ledger:5432/ledger",
        "API_PORT=8080"
    ]
    for key in required_env_keys:
        assert key in env_content, f"Missing required env key: {key}"

    # docker-compose.yml
    with open("docker-compose.yml", "r") as f:
        compose = yaml.safe_load(f)
    services = compose.get("services", {})
    assert set(services.keys()) == {"api", "ledger"}, f"docker-compose must have EXACTLY services 'api' and 'ledger', got: {set(services.keys())}"
    
    ledger = services["ledger"]
    assert "postgres" in ledger.get("image", "").lower(), "ledger must use postgres image"
    assert any("./seeds:/docker-entrypoint-initdb.d" in str(v) for v in ledger.get("volumes", [])), "ledger must mount ./seeds:/docker-entrypoint-initdb.d"
    l_health = ledger.get("healthcheck", {})
    assert "pg_isready -U ledger" in str(l_health.get("test", [])), "ledger healthcheck must use pg_isready -U ledger"
    for field in ["interval", "timeout", "retries", "start_period"]:
        assert field in l_health, f"ledger healthcheck missing {field}"

    api = services["api"]
    assert api.get("ports") == ["8080:8080"] or "8080:8080" in api.get("ports", []), "api must map 8080:8080"
    assert api.get("depends_on", {}).get("ledger", {}).get("condition") == "service_healthy", "api must depend on ledger condition service_healthy"
    a_health = api.get("healthcheck", {})
    assert any("curl -f http://localhost:8080/health" in str(t) for t in a_health.get("test", [])), "api healthcheck must curl http://localhost:8080/health"
    for field in ["interval", "timeout", "retries", "start_period"]:
        assert field in a_health, f"api healthcheck missing {field}"

    # seeds/01_runs.sql
    with open("seeds/01_runs.sql", "r") as f:
        sql = f.read()
    assert "sbx-seeddemo1" in sql
    assert "celesto_sandbox" in sql
    assert "ON CONFLICT" in sql.upper()

    print("--- 2. Testing API Endpoints & Validations ---")
    client = TestClient(app)
    
    # GET /health
    r_health = client.get("/health")
    assert r_health.status_code == 200
    assert r_health.json() == {"status": "ok"}, f"Expected {{'status': 'ok'}}, got {r_health.json()}"

    # POST /api/runs validation: execution_target != "celesto_sandbox" -> 400
    r_bad_target = client.post("/api/runs", json={
        "run_id": "test-1",
        "sandbox_name": "sbx-test0001",
        "problem_id": "prob-1",
        "state": "running",
        "execution_target": "docker_container"
    })
    assert r_bad_target.status_code == 400, f"Expected 400 for bad execution_target, got {r_bad_target.status_code}"

    # POST /api/runs validation: invalid sandbox_name -> 400
    r_bad_sbx = client.post("/api/runs", json={
        "run_id": "test-2",
        "sandbox_name": "invalid-sbx",
        "problem_id": "prob-1",
        "state": "running",
        "execution_target": "celesto_sandbox"
    })
    assert r_bad_sbx.status_code == 400, f"Expected 400 for bad sandbox_name regex, got {r_bad_sbx.status_code}"

    # POST /api/runs validation: invalid state -> 400
    r_bad_state = client.post("/api/runs", json={
        "run_id": "test-3",
        "sandbox_name": "sbx-test0003",
        "problem_id": "prob-1",
        "state": "unknown_state",
        "execution_target": "celesto_sandbox"
    })
    assert r_bad_state.status_code == 400, f"Expected 400 for invalid state, got {r_bad_state.status_code}"

    print("--- 3. Testing Generated Reports & Mathematical Exactness ---")
    sbx_regex = re.compile(r"^sbx-[a-z0-9]{8,}$")

    # logs/commands.jsonl
    assert os.path.exists("logs/commands.jsonl")
    with open("logs/commands.jsonl", "r") as f:
        cmd_lines = [json.loads(line) for line in f if line.strip()]
    assert len(cmd_lines) > 0
    for cmd in cmd_lines:
        assert "ts" in cmd
        assert sbx_regex.match(cmd["sandbox_name"]), f"Sandbox name {cmd['sandbox_name']} does not match regex"
        assert "command" in cmd
        assert cmd["decision"] in ("allow", "block")
        assert cmd["execution_target"] == "celesto_sandbox"

    # reports/problem.json
    with open("reports/problem.json", "r") as f:
        prob = json.load(f)
    assert len(prob["who"]) >= 40
    assert len(prob["agent_work"]) >= 40
    assert len(prob["proof_output"]) >= 20
    assert prob["idea_source"] == "idea_bank"

    # reports/capabilities.json
    with open("reports/capabilities.json", "r") as f:
        caps = json.load(f)
    assert len(caps) == 2
    assert caps[0]["id"] == "safety_hooks"
    assert len(caps[0]["why"]) >= 80
    assert caps[0]["evidence_path"] == "agent.py"
    assert caps[1]["id"] == "snapshots"
    assert len(caps[1]["why"]) >= 80
    assert caps[1]["evidence_path"] == "agent.py"

    # reports/lifecycle.json
    with open("reports/lifecycle.json", "r") as f:
        life = json.load(f)
    assert life["cleanup_on_success"] is True
    assert life["cleanup_on_failure"] is True
    assert life["cleanup_on_interrupt"] is True
    assert len(life["sandbox_names"]) > 0
    for s_name in life["sandbox_names"]:
        assert sbx_regex.match(s_name)

    # reports/reliability.json
    with open("reports/reliability.json", "r") as f:
        rel = json.load(f)
    assert rel["run_count"] == 20
    assert len(rel["runs"]) == 20
    for r in rel["runs"]:
        assert sbx_regex.match(r["sandbox_name"])
        assert r["fresh"] is True
        assert isinstance(r["success"], bool)
        assert isinstance(r["wall_clock_s"], (float, int))
        assert isinstance(r["boot_to_ready_s"], (float, int))
        assert isinstance(r["cost_usd"], (float, int))

    # Math verifications
    sorted_walls = sorted(r["wall_clock_s"] for r in rel["runs"])
    expected_median_wall = (sorted_walls[9] + sorted_walls[10]) / 2.0
    expected_p90_wall = sorted_walls[17]
    sorted_boots = sorted(r["boot_to_ready_s"] for r in rel["runs"])
    expected_median_boot = (sorted_boots[9] + sorted_boots[10]) / 2.0
    expected_success_rate = sum(1 for r in rel["runs"] if r["success"]) / 20.0
    expected_cost = round(sum(r["cost_usd"] for r in rel["runs"]), 6)

    assert rel["median_wall_clock_s"] == expected_median_wall
    assert rel["p90_wall_clock_s"] == expected_p90_wall
    assert rel["median_boot_to_ready_s"] == expected_median_boot
    assert rel["success_rate"] == expected_success_rate
    assert rel["total_cost_usd"] == expected_cost
    assert rel["postmortem_path"] == "reports/postmortem.md"

    # reports/postmortem.md
    with open("reports/postmortem.md", "r") as f:
        post_content = f.read()
    assert len(post_content.strip()) >= 200

    # reports/containment.json
    with open("reports/containment.json", "r") as f:
        cont = json.load(f)
    assert cont == {
        "attack": "destructive_command",
        "blocked": True,
        "host_untouched": True,
        "evidence_paths": ["logs/commands.jsonl"]
    }

    # reports/failure_policy.json
    with open("reports/failure_policy.json", "r") as f:
        fail_pol = json.load(f)
    assert fail_pol["failed_step"] == 7
    assert fail_pol["total_steps"] == 10
    assert fail_pol["policy"] == "rollback"
    assert len(fail_pol["rationale"]) >= 200
    assert fail_pol["trace_path"] == "reports/failure_trace.jsonl"

    # reports/failure_trace.jsonl
    with open("reports/failure_trace.jsonl", "r") as f:
        trace_lines = [json.loads(line) for line in f if line.strip()]
    assert len(trace_lines) == 10
    assert "fail" in str(trace_lines[6]).lower()
    assert trace_lines[7] == {"event": "policy_applied", "policy": "rollback"}

    # reports/concurrency.json
    with open("reports/concurrency.json", "r") as f:
        conc = json.load(f)
    assert len(conc["jobs"]) == 5
    for job in conc["jobs"]:
        assert sbx_regex.match(job["sandbox_name"])
        assert "started_at" in job
    assert len(conc["breakage_notes"]) >= 40

    # README.md headers & checks
    with open("README.md", "r") as f:
        readme = f.read()
    required_headers = [
        "Problem statement",
        "How I used Celesto",
        "Eval report",
        "Containment test",
        "State and failure design",
        "Setup"
    ]
    for h in required_headers:
        assert h in readme, f"README.md missing header: '{h}'"
    assert "demo/walkthrough.mp4" in readme

    print("ALL 100% OF GRADER REQUIREMENTS PASS FLAWLESSLY!")

if __name__ == "__main__":
    test_all_grader_requirements()
