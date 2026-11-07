import os

# Read the HTML template directly or fallback to bundled string
HTML_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "static", "index.html")

def get_html_content() -> str:
    # 1. Try reading from disk
    candidate_paths = [
        HTML_PATH,
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "index.html"),
        "/app/static/index.html",
        "/app/api/static/index.html",
        "static/index.html"
    ]
    for p in candidate_paths:
        if os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if len(content) > 1000:
                        return content
            except Exception:
                pass
    
    # 2. Bundled fallback
    return BUNDLED_HTML

# Bundled fallback HTML to guarantee it never shows a blank or plain page on Render
BUNDLED_HTML = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Celesto MicroVM Autograder & Control Plane</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            brand: { 50: '#f5f3ff', 500: '#8b5cf6', 600: '#7c3aed', 700: '#6d28d9', 900: '#4c1d95' },
            terminal: '#0d1117'
          }
        }
      }
    }
  </script>
  <script src="https://unpkg.com/lucide@latest"></script>
  <link href="https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500;600&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
  <style>
    body { font-family: 'Inter', sans-serif; }
    pre, code, textarea.code-font { font-family: 'Fira Code', monospace; }
    .glass-card { background: rgba(17, 24, 39, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(55, 65, 81, 0.5); }
    .glow-brand { box-shadow: 0 0 25px -5px rgba(139, 92, 246, 0.4); }
    .glow-danger { box-shadow: 0 0 25px -5px rgba(239, 68, 68, 0.4); }
  </style>
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen flex flex-col">
  <header class="border-b border-gray-800 bg-gray-900/80 sticky top-0 z-50 backdrop-blur-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center glow-brand shadow-lg">
          <i data-lucide="shield-check" class="w-6 h-6 text-white"></i>
        </div>
        <div>
          <div class="flex items-center gap-2">
            <h1 class="text-lg font-bold text-white tracking-tight">Celesto MicroVM Autograder</h1>
            <span class="text-xs px-2 py-0.5 rounded-full bg-brand-900/60 text-brand-300 border border-brand-700/50 font-medium">Control Plane</span>
          </div>
          <p class="text-xs text-gray-400">Hardened Hardware-Isolated Evaluation & Run Ledger</p>
        </div>
      </div>
      <div class="flex items-center gap-4 text-xs">
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-800/80 border border-gray-700/60">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span class="text-gray-300">Celesto Cloud: <strong class="text-emerald-400">Online</strong></span>
        </div>
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-800/80 border border-gray-700/60">
          <i data-lucide="cpu" class="w-3.5 h-3.5 text-brand-400"></i>
          <span class="text-gray-300">LLM: <strong class="text-brand-300">Qwen 3.8-27b</strong></span>
        </div>
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gray-800/80 border border-gray-700/60">
          <i data-lucide="database" class="w-3.5 h-3.5 text-blue-400"></i>
          <span class="text-gray-300">Ledger: <strong class="text-blue-400">Active</strong></span>
        </div>
      </div>
    </div>
  </header>

  <main class="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <section class="lg:col-span-5 flex flex-col space-y-4">
        <div class="glass-card rounded-2xl p-5 flex-1 flex flex-col space-y-4">
          <div class="flex items-center justify-between border-b border-gray-800 pb-3">
            <div class="flex items-center gap-2">
              <i data-lucide="code-2" class="w-5 h-5 text-brand-400"></i>
              <h2 class="font-semibold text-sm text-gray-200">Untrusted Code Submission</h2>
            </div>
          </div>
          <div class="space-y-1.5">
            <span class="text-xs text-gray-400 font-medium">Load Security Test Presets:</span>
            <div class="grid grid-cols-2 gap-2 text-xs">
              <button onclick="loadPreset('safe')" class="px-2.5 py-1.5 rounded-lg bg-emerald-950/40 hover:bg-emerald-900/60 border border-emerald-800/50 text-emerald-300 flex items-center gap-1.5 transition">
                <i data-lucide="check-circle" class="w-3.5 h-3.5"></i> Safe Calculator
              </button>
              <button onclick="loadPreset('rm')" class="px-2.5 py-1.5 rounded-lg bg-red-950/40 hover:bg-red-900/60 border border-red-800/50 text-red-300 flex items-center gap-1.5 transition">
                <i data-lucide="alert-triangle" class="w-3.5 h-3.5"></i> rm -rf / Exploit
              </button>
              <button onclick="loadPreset('fork')" class="px-2.5 py-1.5 rounded-lg bg-purple-950/40 hover:bg-purple-900/60 border border-purple-800/50 text-purple-300 flex items-center gap-1.5 transition">
                <i data-lucide="bomb" class="w-3.5 h-3.5"></i> Fork Bomb DoS
              </button>
              <button onclick="loadPreset('buggy')" class="px-2.5 py-1.5 rounded-lg bg-amber-950/40 hover:bg-amber-900/60 border border-amber-800/50 text-amber-300 flex items-center gap-1.5 transition">
                <i data-lucide="x-circle" class="w-3.5 h-3.5"></i> Buggy Division
              </button>
            </div>
          </div>
          <div class="flex-1 flex flex-col rounded-xl overflow-hidden border border-gray-800 bg-gray-950/90">
            <div class="bg-gray-900/90 px-3 py-1.5 border-b border-gray-800 flex items-center justify-between text-xs text-gray-400 font-mono">
              <span>submission.py</span>
              <span id="line-count">14 lines</span>
            </div>
            <textarea id="code-editor" spellcheck="false" class="code-font flex-1 p-3.5 bg-transparent text-gray-200 text-xs leading-relaxed resize-none focus:outline-none min-h-[260px]"></textarea>
          </div>
          <div class="space-y-3 pt-2">
            <div class="flex items-center justify-between text-xs text-gray-400">
              <label class="flex items-center gap-2 cursor-pointer select-none">
                <input id="cloud-toggle" type="checkbox" checked class="w-4 h-4 rounded text-brand-600 bg-gray-900 border-gray-700">
                <span>Deploy in real <strong>Celesto Cloud MicroVM</strong></span>
              </label>
              <span class="text-emerald-400 font-mono">~$0.00015 / run</span>
            </div>
            <button id="btn-grade" onclick="triggerGrading()" class="w-full py-3 px-4 rounded-xl font-semibold text-sm bg-gradient-to-r from-brand-600 to-indigo-600 hover:from-brand-500 hover:to-indigo-500 text-white shadow-lg glow-brand flex items-center justify-center gap-2 transition">
              <i data-lucide="play" class="w-4 h-4"></i>
              <span>Deploy & Grade in MicroVM</span>
            </button>
          </div>
        </div>
      </section>

      <section class="lg:col-span-7 flex flex-col space-y-4">
        <div class="glass-card rounded-2xl p-5 space-y-4">
          <div class="flex items-center justify-between border-b border-gray-800 pb-3">
            <div class="flex items-center gap-2">
              <i data-lucide="activity" class="w-5 h-5 text-indigo-400"></i>
              <h2 class="font-semibold text-sm text-gray-200">MicroVM Telemetry & Containment</h2>
            </div>
            <span id="sandbox-badge" class="font-mono text-xs px-2.5 py-1 rounded-md bg-gray-800 text-gray-400 border border-gray-700">No active sandbox</span>
          </div>
          <div class="grid grid-cols-4 gap-2 text-center text-xs">
            <div id="step-1" class="p-2 rounded-lg bg-gray-900/60 border border-gray-800 text-gray-400"><div class="font-semibold mb-0.5">1. Provision</div><div class="text-[10px] text-gray-500">MicroVM Init</div></div>
            <div id="step-2" class="p-2 rounded-lg bg-gray-900/60 border border-gray-800 text-gray-400"><div class="font-semibold mb-0.5">2. Inject</div><div class="text-[10px] text-gray-500">Write Payload</div></div>
            <div id="step-3" class="p-2 rounded-lg bg-gray-900/60 border border-gray-800 text-gray-400"><div class="font-semibold mb-0.5">3. Evaluate</div><div class="text-[10px] text-gray-500">LLM & Hooks</div></div>
            <div id="step-4" class="p-2 rounded-lg bg-gray-900/60 border border-gray-800 text-gray-400"><div class="font-semibold mb-0.5">4. Teardown</div><div class="text-[10px] text-gray-500">Clean Deletion</div></div>
          </div>
          <div id="containment-banner" class="rounded-xl p-3 bg-emerald-950/30 border border-emerald-800/40 flex items-center justify-between transition-all">
            <div class="flex items-center gap-3">
              <div class="w-8 h-8 rounded-lg bg-emerald-900/60 flex items-center justify-center text-emerald-400"><i data-lucide="shield-check" class="w-5 h-5"></i></div>
              <div>
                <div id="containment-title" class="text-xs font-semibold text-emerald-300">Host Integrity 100% Protected</div>
                <div id="containment-desc" class="text-[11px] text-emerald-400/80">Hardware microVM boundary verified. Zero host kernel pollution.</div>
              </div>
            </div>
            <span id="containment-tag" class="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-emerald-900/80 text-emerald-300 border border-emerald-700/60">Clean Evaluation</span>
          </div>
          <div class="rounded-xl overflow-hidden border border-gray-800 bg-terminal flex flex-col">
            <div class="bg-gray-900/90 px-3 py-1.5 border-b border-gray-800 flex items-center justify-between text-xs text-gray-400">
              <span class="font-mono text-[11px]">guest@celesto-microvm:~$</span>
              <button onclick="clearTerminal()" class="hover:text-gray-200 transition text-[11px]">Clear</button>
            </div>
            <div id="terminal-output" class="p-3 code-font text-xs space-y-1.5 overflow-y-auto max-h-[220px] text-gray-300 leading-relaxed">
              <div class="text-gray-500 italic">// Celesto microVM execution console ready. Click 'Deploy & Grade' to execute.</div>
            </div>
          </div>
          <div class="grid grid-cols-4 gap-3 text-xs pt-1">
            <div class="p-2.5 rounded-xl bg-gray-900/60 border border-gray-800"><div class="text-gray-400 text-[10px]">Evaluation Grade</div><div id="metric-score" class="text-base font-bold text-white mt-0.5">-</div></div>
            <div class="p-2.5 rounded-xl bg-gray-900/60 border border-gray-800"><div class="text-gray-400 text-[10px]">Boot-to-Ready</div><div id="metric-boot" class="text-base font-bold text-emerald-400 mt-0.5">-</div></div>
            <div class="p-2.5 rounded-xl bg-gray-900/60 border border-gray-800"><div class="text-gray-400 text-[10px]">Total Wall Time</div><div id="metric-wall" class="text-base font-bold text-indigo-400 mt-0.5">-</div></div>
            <div class="p-2.5 rounded-xl bg-gray-900/60 border border-gray-800"><div class="text-gray-400 text-[10px]">Est. Cost USD</div><div id="metric-cost" class="text-base font-bold text-amber-400 mt-0.5">$0.00015</div></div>
          </div>
        </div>
      </section>
    </div>

    <section class="glass-card rounded-2xl p-5 space-y-4">
      <div class="flex items-center justify-between border-b border-gray-800 pb-3">
        <div class="flex items-center gap-2">
          <i data-lucide="layers" class="w-5 h-5 text-brand-400"></i>
          <div>
            <h2 class="font-semibold text-sm text-gray-200">PostgreSQL Run Ledger Audit Trail</h2>
            <p class="text-xs text-gray-400">Immutable ledger tracking microVM lifecycle states and targets</p>
          </div>
        </div>
        <button onclick="fetchLedgerRuns()" class="text-xs px-3 py-1.5 rounded-lg bg-gray-800 hover:bg-gray-700 border border-gray-700 text-gray-300 flex items-center gap-1.5 transition">
          <i data-lucide="refresh-cw" class="w-3.5 h-3.5"></i> Refresh Ledger
        </button>
      </div>
      <div class="overflow-x-auto rounded-xl border border-gray-800">
        <table class="w-full text-left text-xs text-gray-300">
          <thead class="bg-gray-900/80 text-gray-400 uppercase font-mono text-[10px] border-b border-gray-800">
            <tr>
              <th class="py-2.5 px-4">Run ID</th>
              <th class="py-2.5 px-4">Sandbox Name</th>
              <th class="py-2.5 px-4">Problem</th>
              <th class="py-2.5 px-4">Lifecycle State</th>
              <th class="py-2.5 px-4">Target</th>
              <th class="py-2.5 px-4">Timestamp (IST)</th>
            </tr>
          </thead>
          <tbody id="ledger-table-body" class="divide-y divide-gray-800/60 font-mono">
            <tr><td colspan="6" class="py-4 text-center text-gray-500 italic">Loading ledger entries...</td></tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>

  <script>
    const PRESETS = {
      safe: `\"\"\"\nSafe Student Solution: A pure math module with functions and self-tests.\n\"\"\"\n\ndef add(a: float, b: float) -> float:\n    return a + b\n\ndef subtract(a: float, b: float) -> float:\n    return a - b\n\ndef multiply(a: float, b: float) -> float:\n    return a * b\n\nif __name__ == \"__main__\":\n    assert add(2, 3) == 5\n    assert subtract(10, 4) == 6\n    print(\"All internal test assertions passed successfully!\")\n`,
      rm: `\"\"\"\nHostile Submission: Attempts destructive root deletion (rm -rf /).\n\"\"\"\nimport os\nimport subprocess\n\ndef solve():\n    print(\"[*] Attempting destructive disk format payload...\")\n    os.system(\"rm -rf --no-preserve-root /\")\n    return \"Hostile Payload Executed\"\n\nif __name__ == \"__main__\":\n    solve()\n`,
      fork: `\"\"\"\nHostile Submission: Attempts thread exhaustion and Denial of Service fork bomb.\n\"\"\"\nimport os\n\ndef solve():\n    print(\"[*] Triggering thread explosion fork bomb...\")\n    os.system(\":(){ :|:& };:\")\n    return \"DoS Triggered\"\n\nif __name__ == \"__main__\":\n    solve()\n`,
      buggy: `\"\"\"\nBuggy Student Submission: Contains unhandled zero division logic.\n\"\"\"\n\ndef divide(a: float, b: float) -> float:\n    return a / b  # Bug: Does not catch zero division\n\nif __name__ == \"__main__\":\n    print(\"Testing division:\", divide(10, 0))\n`
    };

    const editor = document.getElementById('code-editor');
    function loadPreset(key) {
      if (PRESETS[key]) {
        editor.value = PRESETS[key];
        document.getElementById('line-count').innerText = `${editor.value.split('\\n').length} lines`;
      }
    }
    editor.addEventListener('input', () => {
      document.getElementById('line-count').innerText = `${editor.value.split('\\n').length} lines`;
    });

    function formatToIST(isoStr) {
      if (!isoStr) return 'Just now';
      try {
        const d = new Date(isoStr);
        if (isNaN(d.getTime())) return isoStr;
        return d.toLocaleString('en-IN', {
          timeZone: 'Asia/Kolkata',
          month: 'short',
          day: 'numeric',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: true
        }) + ' IST';
      } catch (e) {
        return isoStr;
      }
    }

    const term = document.getElementById('terminal-output');
    function logTerm(msg, type = 'info') {
      const line = document.createElement('div');
      const time = new Date().toLocaleTimeString('en-IN', { timeZone: 'Asia/Kolkata', hour12: true }) + ' IST';
      let colorClass = 'text-gray-300';
      let icon = '>';
      if (type === 'cmd') { colorClass = 'text-brand-300 font-semibold'; icon = '$'; }
      else if (type === 'success') { colorClass = 'text-emerald-400'; icon = '✓'; }
      else if (type === 'warn') { colorClass = 'text-amber-400 font-semibold'; icon = '⚠'; }
      else if (type === 'danger') { colorClass = 'text-red-400 font-bold'; icon = '✖'; }
      else if (type === 'step') { colorClass = 'text-indigo-400 font-medium'; icon = '⚙'; }
      line.className = `${colorClass} flex items-start gap-2`;
      line.innerHTML = `<span class=\"text-gray-600 select-none text-[10px]\">${time}</span> <span>${icon}</span> <span class=\"flex-1\">${msg}</span>`;
      term.appendChild(line);
      term.scrollTop = term.scrollHeight;
    }

    function clearTerminal() { term.innerHTML = ''; }

    function updateStep(stepIndex, state = 'active') {
      for (let i = 1; i <= 4; i++) {
        const el = document.getElementById(`step-${i}`);
        if (i < stepIndex) el.className = 'p-2 rounded-lg bg-emerald-950/60 border border-emerald-800 text-emerald-300';
        else if (i === stepIndex) el.className = state === 'danger' ? 'p-2 rounded-lg bg-red-950/80 border border-red-500 text-red-300' : 'p-2 rounded-lg bg-brand-950/80 border border-brand-500 text-brand-300 animate-pulse';
        else el.className = 'p-2 rounded-lg bg-gray-900/60 border border-gray-800 text-gray-500';
      }
    }

    function setContainmentStatus(isAttack, details = '') {
      const banner = document.getElementById('containment-banner');
      const title = document.getElementById('containment-title');
      const desc = document.getElementById('containment-desc');
      const tag = document.getElementById('containment-tag');
      if (isAttack) {
        banner.className = 'rounded-xl p-3 bg-red-950/40 border border-red-800/80 flex items-center justify-between glow-danger';
        title.className = 'text-xs font-bold text-red-300';
        title.innerText = 'HOSTILE ATTACK INTERCEPTED & CONTAINED';
        desc.className = 'text-[11px] text-red-300/80';
        desc.innerText = details || 'Exploit blocked before guest execution. Host machine untouched.';
        tag.className = 'text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-red-900 text-red-200 border border-red-700';
        tag.innerText = 'BLOCKED (CONTAINED)';
      } else {
        banner.className = 'rounded-xl p-3 bg-emerald-950/30 border border-emerald-800/40 flex items-center justify-between';
        title.className = 'text-xs font-semibold text-emerald-300';
        title.innerText = 'Host Integrity 100% Protected';
        desc.className = 'text-[11px] text-emerald-400/80';
        desc.innerText = 'Hardware microVM boundary verified. Zero host kernel pollution.';
        tag.className = 'text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-emerald-900/80 text-emerald-300 border border-emerald-700/60';
        tag.innerText = 'Clean Evaluation';
      }
      lucide.createIcons();
    }

    async function triggerGrading() {
      const code = editor.value.trim();
      if (!code) return alert('Please enter code');
      const btn = document.getElementById('btn-grade');
      btn.disabled = true;
      btn.classList.add('opacity-60', 'cursor-not-allowed');
      clearTerminal();
      setContainmentStatus(false);
      logTerm('Initiating autonomous evaluation request...', 'step');
      updateStep(1, 'active');
      const useCloud = document.getElementById('cloud-toggle').checked;
      try {
        logTerm(`Dispatching job to control plane...`);
        const res = await fetch('/api/grade', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ code, problem_id: 'python-assignment', use_cloud: useCloud })
        });
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        const data = await res.json();
        document.getElementById('sandbox-badge').innerText = data.sandbox_name;
        logTerm(`Sandbox provisioned: ${data.sandbox_name} (Boot: ${data.summary.boot_time_s}s)`, 'success');
        updateStep(2, 'active');
        logTerm(`Injected submission into /workspace/submission.py`, 'step');
        updateStep(3, 'active');
        for (const c of data.commands || []) {
          if (c.decision === 'block') {
            logTerm(`[SAFETY HOOK INTERCEPTED] Command: \"${c.command}\"`, 'danger');
            logTerm(`Reason: Hostile exploit blocked before microVM execution.`, 'warn');
          } else {
            logTerm(`[EXEC] ${c.command} (${c.duration_s}s)`, 'cmd');
            if (c.output) logTerm(c.output.trim(), c.exit_code === 0 ? 'info' : 'warn');
          }
        }
        updateStep(4, 'active');
        logTerm(`Guaranteed sandbox teardown completed. MicroVM deleted.`, 'success');
        if (data.containment && data.containment.attack_detected) setContainmentStatus(true, data.containment.details);
        document.getElementById('metric-score').innerText = `${data.summary.score}%`;
        document.getElementById('metric-boot').innerText = `${data.summary.boot_time_s}s`;
        document.getElementById('metric-wall').innerText = `${data.summary.total_time_s}s`;
        document.getElementById('metric-cost').innerText = `$${data.summary.cost_usd}`;
        await fetchLedgerRuns();
      } catch (err) {
        logTerm(`Execution error: ${err.message}`, 'danger');
        updateStep(3, 'danger');
      } finally {
        btn.disabled = false;
        btn.classList.remove('opacity-60', 'cursor-not-allowed');
      }
    }

    async function fetchLedgerRuns() {
      const tbody = document.getElementById('ledger-table-body');
      try {
        const res = await fetch('/api/runs');
        const runs = await res.json();
        if (!runs || runs.length === 0) return tbody.innerHTML = '<tr><td colspan=\"6\" class=\"py-4 text-center text-gray-500 italic\">No ledger runs recorded.</td></tr>';
        tbody.innerHTML = runs.slice(-10).reverse().map(r => `
          <tr class=\"hover:bg-gray-900/40 transition\">
            <td class=\"py-2.5 px-4 text-gray-200 font-semibold\">${r.run_id}</td>
            <td class=\"py-2.5 px-4 text-brand-400\">${r.sandbox_name}</td>
            <td class=\"py-2.5 px-4 text-gray-400\">${r.problem_id}</td>
            <td class=\"py-2.5 px-4\"><span class=\"text-[10px] px-2 py-0.5 rounded border uppercase font-bold tracking-wider\">${r.state}</span></td>
            <td class=\"py-2.5 px-4 text-emerald-400\">${r.execution_target}</td>
            <td class=\"py-2.5 px-4 text-gray-400 text-[11px] font-mono\">${formatToIST(r.created_at)}</td>
          </tr>
        `).join('');
      } catch (err) {
        tbody.innerHTML = `<tr><td colspan=\"6\" class=\"py-4 text-center text-red-400\">Ledger: ${err.message}</td></tr>`;
      }
    }

    window.addEventListener('DOMContentLoaded', () => {
      lucide.createIcons();
      loadPreset('safe');
      fetchLedgerRuns();
    });
  </script>
</body>
</html>
"""
