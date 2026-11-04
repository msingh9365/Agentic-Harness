"use strict";
// ETL Doctor UI. Everything shown here comes from a broken system or from a model, so it is
// untrusted: the page only ever sets textContent (via h()), never innerHTML.

const STATUS = {
  running: "Running",
  awaiting_approval: "Waiting for approval",
  fixed: "Fixed",
  diagnosed_unfixed: "Diagnosed, not fixed",
  escalated: "Escalated",
  stopped: "Stopped",
};

const REPLAY = document.body.dataset.mode === "replay";
let config = null;
let cases = null;
let cleanup = [];

function h(tag, attrs, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === "class") el.className = v;
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v === true ? "" : String(v));
  }
  for (const kid of kids.flat(Infinity)) {
    if (kid == null || kid === false) continue;
    el.append(kid instanceof Node ? kid : document.createTextNode(String(kid)));
  }
  return el;
}

async function api(path, body) {
  const opts = body === undefined ? {} : {
    method: "POST",
    headers: { "content-type": "application/json", "x-etldoc": "1" },
    body: JSON.stringify(body),
  };
  const r = await fetch(path, opts);
  const data = r.headers.get("content-type")?.includes("json") ? await r.json() : await r.text();
  if (!r.ok) throw new Error(typeof data === "object" && data.detail ? data.detail : `HTTP ${r.status}`);
  return data;
}

const store = {
  get(k) { try { return localStorage.getItem(k) || ""; } catch { return ""; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* private mode: fine */ } },
};

const pill = (status) => h("span", { class: `pill ${status}` }, STATUS[status] || status);
const fmtTime = (iso) => iso ? new Date(iso).toLocaleString() : "";
const pct = (x) => `${Math.round(x * 100)}%`;
const ktok = (n) => n >= 1000 ? `${(n / 1000).toFixed(1)}k` : String(n);
const variantText = (v) => Object.entries(v || {}).map(([k, x]) => `${k}=${x}`).join(", ") || "default";

function nameField(id) {
  if (config.auth) return null;
  const input = h("input", { type: "text", id, value: store.get("etldoc.name"), placeholder: "e.g. Asha",
    maxlength: 60, autocomplete: "name", oninput: (e) => store.set("etldoc.name", e.target.value) });
  return h("div", { class: "field" }, h("label", { for: id }, "Your name (recorded in the audit trail)"), input);
}
const nameValue = (id) => document.getElementById(id)?.value.trim() || null;

// --- routing -----------------------------------------------------------------------------

function route() {
  cleanup.forEach((f) => f());
  cleanup = [];
  const m = location.hash.match(/^#\/run\/([\w-]+)$/);
  let page;
  if (REPLAY) page = m ? loadRecording(m[1]) : Promise.resolve(location.replace("./"));
  else page = m ? showRun(m[1], liveSource(m[1])) : showHome();
  page.catch((e) => {
    document.getElementById("main").replaceChildren(h("div", { class: "banner bad" }, e.message));
  });
}

// --- home: start a run, list runs ---------------------------------------------------------

async function showHome() {
  const main = document.getElementById("main");
  const select = h("select", { id: "case" });
  const groups = {};
  for (const c of cases) {
    groups[c.scenario] ??= h("optgroup", { label: `${c.failure_class} · ${c.scenario}` });
    groups[c.scenario].append(h("option", { value: c.case }, `${c.mode} · ${variantText(c.variant)}`));
  }
  select.append(...Object.values(groups));
  const desc = h("p", { class: "muted small" });
  const showDesc = () => {
    const c = cases.find((x) => x.case === select.value);
    desc.textContent = c ? `${c.description} Mode "${c.mode}": ${c.mode === "crash"
      ? "the pipeline fails loudly." : "the pipeline succeeds, but data-quality checks fail."}` : "";
  };
  select.addEventListener("change", showDesc);
  showDesc();

  const sandbox = h("select", { id: "sandbox" },
    h("option", { value: "e2b" }, "E2B microVM (isolated)"),
    config.allow_local_sandbox ? h("option", { value: "local" }, "local (not isolated, dev only)") : null);
  const err = h("div", { class: "err" });
  const btn = h("button", { class: "primary", onclick: async () => {
    btn.disabled = true; err.textContent = "";
    btn.textContent = "Preparing the broken bundle…";
    try {
      const r = await api("/api/runs", { case: select.value, sandbox: sandbox.value, approver: nameValue("starter") });
      location.hash = `#/run/${r.run_id}`;
    } catch (e) {
      err.textContent = e.message; btn.disabled = false; btn.textContent = "Start diagnosis";
    }
  } }, "Start diagnosis");

  const limits = h("p", { class: "muted small" });
  const runsBox = h("div", { class: "table-wrap" }, h("p", { class: "empty" }, "Loading runs…"));

  main.replaceChildren(
    h("section", { class: "panel" },
      h("h2", {}, "Start a run"),
      h("p", { class: "muted small" }, "Pick a failure to inject. The fault injector builds a broken copy of the demo " +
        "pipeline (code, data, logs); the agent investigates it in a sandbox, proposes a fix, and waits for your approval."),
      h("div", { class: "fields" },
        h("div", { class: "field" }, h("label", { for: "case" }, "Failure"), select),
        h("div", { class: "field" }, h("label", { for: "sandbox" }, "Sandbox"), sandbox),
        nameField("starter") || h("div")),
      desc, h("div", { class: "row" }, btn, limits), err),
    h("section", { class: "panel" }, h("h2", {}, "Runs"), runsBox));

  async function refresh() {
    const [runs, cfg] = await Promise.all([api("/api/runs"), api("/api/config")]);
    limits.textContent = `${cfg.active_runs}/${cfg.max_active_runs} active · ${cfg.runs_today}/${cfg.max_runs_per_day} runs today`;
    if (!runs.length) {
      runsBox.replaceChildren(h("p", { class: "empty" }, "No runs yet."));
      return;
    }
    runsBox.replaceChildren(h("table", {},
      h("thead", {}, h("tr", {}, ["Run", "Failure", "Mode", "Variant", "Status", "Started by", "Created"].map((x) => h("th", {}, x)))),
      h("tbody", {}, runs.map((r) => h("tr", {},
        h("td", {}, h("a", { href: `#/run/${r.run_id}`, class: "mono" }, r.run_id)),
        h("td", {}, `${r.failure_class} ${r.scenario}`),
        h("td", {}, r.mode),
        h("td", { class: "small" }, variantText(r.variant)),
        h("td", {}, pill(r.status)),
        h("td", {}, r.started_by || ""),
        h("td", { class: "small muted" }, fmtTime(r.created_at)))))));
  }
  await refresh();
  const timer = setInterval(() => refresh().catch(() => {}), 5000);
  cleanup.push(() => clearInterval(timer));
}

// --- one run ------------------------------------------------------------------------------
// The run view reads from a "source": the live server, or a recording played back in the
// browser (the static replay site). Rendering is the same code either way.

function liveSource(runId) {
  return {
    replay: false,
    controls: null,
    get: () => api(`/api/runs/${runId}`),
    history: () => api(`/api/runs/${runId}/history`),
    // Replayed from the start, then pushed as they happen. EventSource reconnects by itself
    // and sends Last-Event-ID, so nothing is missed or duplicated.
    start(onEvent) {
      const es = new EventSource(`/api/runs/${runId}/events`);
      es.onmessage = (msg) => onEvent(JSON.parse(msg.data));
      return () => es.close();
    },
  };
}

async function showRun(runId, src) {
  const main = document.getElementById("main");
  const head = h("div", { class: "panel" });
  const body = h("div");
  const timeline = h("ol", { class: "timeline" });
  main.replaceChildren(...[src.controls, head, h("div", { class: "grid" }, body,
    h("aside", { class: "panel" }, h("h2", {}, src.replay ? "Log" : "Live log"), timeline))].filter(Boolean));

  let lastSig = null;
  let lastError = null;
  let pending = null;
  let seen = new Set();

  async function refresh() {
    const run = await src.get();
    const s = run.state;
    const sig = JSON.stringify([run.status, run.next, s?.evidence?.length, s?.approvals?.length, s?.fix_attempts,
      s?.report?.status, s?.hypotheses, s?.verification, lastError]);
    renderHead(run);
    if (sig === lastSig) return;  // unchanged: don't wipe a half-typed rejection
    lastSig = sig;
    body.replaceChildren(...renderBody(run));
  }
  const soon = () => { clearTimeout(pending); pending = setTimeout(() => refresh().catch(() => {}), src.replay ? 0 : 250); };

  function renderHead(run) {
    const m = run.meta;
    const resume = run.status === "stopped" && !src.replay ? h("button", { class: "primary", onclick: async (e) => {
      e.target.disabled = true;
      try { await api(`/api/runs/${runId}/resume`, {}); soon(); } catch (x) { alert(x.message); e.target.disabled = false; }
    } }, "Resume from last checkpoint") : null;
    head.replaceChildren(...[
      h("div", { class: "row spread" },
        h("div", { class: "row" }, h("a", { href: src.replay ? "./" : "#/" }, src.replay ? "← Project" : "← Runs"),
          h("h1", { class: "mono" }, runId), pill(run.status)),
        resume),
      h("p", { class: "muted small" },
        `${m.failure_class} ${m.scenario} · ${m.mode} · ${variantText(m.variant)} · sandbox ${m.sandbox} · ` +
        `started by ${m.started_by} · ${fmtTime(m.created_at)}`),
      run.status === "stopped" && lastError ? h("div", { class: "banner bad" }, lastError) : null,
    ].filter(Boolean));  // replaceChildren would print a null as the text "null"
  }

  function renderBody(run) {
    const s = run.state;
    const out = [];
    if (run.status === "awaiting_approval" && run.approval) {
      out.push(approvalCard(runId, run.approval, soon, src.replay ? { decision: src.decisionAfter() } : null));
    }
    if (s?.report) out.push(reportPanel(runId, s, run.answer_key, src.replay));
    if (!s) {
      out.push(h("section", { class: "panel" }, h("p", { class: "empty" },
        run.status === "running" ? "Starting: reading the bundle and creating the sandbox…" : "No checkpoint yet.")));
      return out;
    }
    out.push(investigationPanel(s));
    out.push(evidencePanel(s));
    out.push(historyPanel(src.history));
    return out;
  }

  function onEvent(e) {
    if (seen.has(e.seq)) return;
    seen.add(e.seq);
    if (e.type === "error") lastError = e.message;
    if (e.type === "status" && e.status === "running") lastError = null;
    const atBottom = timeline.scrollHeight - timeline.scrollTop - timeline.clientHeight < 40;
    timeline.append(timelineItem(e));
    if (atBottom) timeline.scrollTop = timeline.scrollHeight;
    if (e.type !== "evidence") soon();
  }
  function onReset() {  // replay only: seeking backwards rebuilds the log
    timeline.replaceChildren();
    seen = new Set();
    lastError = null;
    lastSig = null;
  }
  const stop = src.start(onEvent, onReset, soon);
  cleanup.push(() => { stop(); clearTimeout(pending); });
  await refresh();
}

// --- replay of a recorded run (static site) --------------------------------------------------

const GAP_CAP = 6;  // seconds: long waits (a human deciding, a restart) are shortened in replay

async function loadRecording(runId) {
  const r = await fetch(`runs/${runId}.json`);
  if (!r.ok) throw new Error(`No recording called ${runId}`);
  const data = await r.json();
  await showRun(runId, replaySource(data));
}

function replaySource(data) {
  // One clock for events and checkpoint frames; real gaps are kept but capped.
  const items = [...data.events.map((e) => ({ t: e.t, e })), ...data.frames.map((f) => ({ t: f.t, f }))]
    .sort((a, b) => a.t - b.t);
  let vt = 0;
  for (let i = 0; i < items.length; i++) {
    vt += i ? Math.min(Math.max(items[i].t - items[i - 1].t, 0), GAP_CAP) : 0;
    items[i].vt = vt;
  }
  const total = vt;
  let now = 0, speed = 4, playing = false, timer = null, next = 0;
  let onEvent = () => {}, onReset = () => {}, onChange = () => {};
  const recorded = new Date(data.meta.created_at);

  const playBtn = h("button", { class: "primary", onclick: () => (playing ? pause() : play()) });
  const speedSel = h("select", { class: "speed", "aria-label": "Speed", onchange: (e) => (speed = Number(e.target.value)) },
    [1, 4, 16].map((x) => h("option", { value: x, selected: x === speed }, `${x}×`)));
  const bar = h("input", { type: "range", min: 0, max: total.toFixed(1), step: 0.1, value: 0, "aria-label": "Position",
    oninput: (e) => seek(Number(e.target.value)) });
  const clock = h("span", { class: "mono small muted" });
  const hint = h("div", { class: "small replay-hint" });
  const controls = h("section", { class: "panel replay" },
    h("div", { class: "row spread" },
      h("div", {}, h("b", {}, "Replay of a real run"),
        h("span", { class: "muted small" }, ` · recorded ${recorded.toLocaleDateString()} · real models, real E2B sandbox; ` +
          "long waits are shortened")),
      h("div", { class: "row" }, playBtn, speedSel,
        h("button", { onclick: () => { pause(); seek(total); } }, "Skip to end"))),
    h("div", { class: "row replay-track" }, bar, clock), hint);

  const fmt = (x) => `${Math.floor(x / 60)}:${String(Math.floor(x % 60)).padStart(2, "0")}`;
  function show() {
    bar.value = now;
    clock.textContent = `${fmt(now)} / ${fmt(total)}`;
    playBtn.textContent = playing ? "Pause" : now >= total ? "Replay" : "Play";
  }
  function deliver(quiet) {
    let changed = false, gate = false;
    while (next < items.length && items[next].vt <= now + 1e-9) {
      const it = items[next++];
      if (it.e) {
        onEvent(it.e);
        if (it.e.type === "status" && it.e.status === "awaiting_approval") gate = true;
      } else changed = true;
    }
    if (changed || quiet) onChange();
    return gate;
  }
  function tick() {
    now = Math.min(total, now + 0.1 * speed);
    if (deliver(false) && now < total) {
      pause();
      hint.textContent = "Paused at the approval gate. In the live system, a person decides here; press Play to see what the reviewer chose.";
    }
    if (now >= total) pause();
    show();
  }
  function play() {
    if (now >= total) seek(0);
    hint.textContent = "";
    playing = true;
    clearInterval(timer);
    timer = setInterval(tick, 100);
    show();
  }
  function pause() { playing = false; clearInterval(timer); show(); }
  function seek(x) {
    now = Math.max(0, Math.min(total, x));
    onReset();
    next = 0;
    hint.textContent = "";
    deliver(true);
    show();
  }

  function frameAt() {
    let f = null, status = null;
    for (const it of items) {
      if (it.vt > now + 1e-9) break;
      if (it.f) f = it.f;
      if (it.e?.type === "status") status = it.e.status;
    }
    const base = f ? f.run : { meta: data.meta, status: "running", next: [], approval: null, state: null };
    return { ...base, status: status || base.status };
  }

  return {
    replay: true,
    controls,
    get: async () => frameAt(),
    history: async () => data.history,
    decisionAfter() {
      const it = items.find((x) => x.vt > now + 1e-9 && x.e?.type === "decision");
      return it ? it.e : null;
    },
    start(ev, reset, change) {
      onEvent = ev; onReset = reset; onChange = change;
      show();
      play();
      return () => clearInterval(timer);
    },
  };
}

function timelineItem(e) {
  const t = h("span", { class: "t" }, new Date(e.t * 1000).toLocaleTimeString());
  switch (e.type) {
    case "node":
      return h("li", { class: "node" }, t, h("span", { class: "lbl" }, e.label), e.detail ? ` — ${e.detail}` : "");
    case "evidence":
      return h("li", { class: "evidence" }, t, h("span", { class: "mono" }, e.id), ` ${e.tool}: ${e.summary}`);
    case "decision":
      return h("li", { class: "decision" }, t, h("span", { class: "lbl" }, `${e.decision} by ${e.approver}`),
        e.feedback ? ` — ${e.feedback}` : "");
    case "error":
      return h("li", { class: "error" }, t, h("span", { class: "lbl" }, "error"), ` ${e.message}`);
    default:
      return h("li", { class: "status" }, t, h("span", { class: "lbl" }, STATUS[e.status] || e.status),
        e.detail ? ` — ${e.detail}` : "");
  }
}

function diffView(patch) {
  return h("div", { class: "diff" }, patch.split("\n").map((ln) => {
    let cls = "";
    if (ln.startsWith("+++") || ln.startsWith("---")) cls = "file";
    else if (ln.startsWith("+")) cls = "add";
    else if (ln.startsWith("-")) cls = "del";
    else if (ln.startsWith("@@")) cls = "hunk";
    return h("span", { class: cls }, ln || " ");
  }));
}

function approvalCard(runId, req, refresh, recording) {
  const hy = req.hypothesis, p = req.proposal, v = req.verification;
  const fb = h("textarea", { id: "feedback", placeholder: "Required to reject: what should the next proposal do differently?" });
  const err = h("div", { class: "err" });
  const buttons = [];
  const send = (decision) => async () => {
    err.textContent = "";
    if (decision === "reject" && !fb.value.trim()) { err.textContent = "Say what should change, so the next proposal can do better."; fb.focus(); return; }
    if (decision === "abort" && !confirm("Abort: keep the diagnosis and apply nothing?")) return;
    buttons.forEach((b) => (b.disabled = true));
    try {
      await api(`/api/runs/${runId}/decision`, { decision, feedback: fb.value, approver: nameValue("approver") });
      refresh();
    } catch (e) { err.textContent = e.message; buttons.forEach((b) => (b.disabled = false)); }
  };
  buttons.push(
    h("button", { class: "approve", onclick: send("approve") }, "Approve and validate"),
    h("button", { onclick: send("reject") }, "Reject with feedback"),
    h("button", { class: "danger", onclick: send("abort") }, "Abort"));

  return h("section", { class: "panel attention" },
    h("h2", {}, `Approval needed · proposal ${req.attempt}`),
    h("dl", { class: "kv" },
      h("dt", {}, "Diagnosis"), h("dd", {}, `${hy.failure_class}: ${hy.statement}`),
      h("dt", {}, "Columns"), h("dd", {}, hy.affected_columns.join(", ")),
      h("dt", {}, "First bad file"), h("dd", { class: "mono" }, hy.first_bad_partition || "—"),
      h("dt", {}, "Confidence"), h("dd", {}, pct(hy.confidence)),
      h("dt", {}, "Verified"), h("dd", {}, `${v.outcome}: ${v.observations}`)),
    h("h3", {}, "Evidence"),
    h("div", { class: "table-wrap" }, h("table", {}, h("tbody", {}, req.evidence.map((e) =>
      h("tr", {}, h("td", { class: "mono" }, e.id), h("td", { class: "mono small" }, e.tool), h("td", {}, e.summary)))))),
    h("h3", {}, "Proposed change (not applied yet)"),
    diffView(req.patch),
    h("dl", { class: "kv" },
      h("dt", {}, "Rationale"), h("dd", {}, p.rationale),
      h("dt", {}, "Blast radius"), h("dd", {}, p.blast_radius),
      h("dt", {}, "Expected"), h("dd", {}, p.expected_effects.join("; ")),
      h("dt", {}, "Rollback"), h("dd", {}, p.rollback),
      h("dt", {}, "Fixer confidence"), h("dd", {}, pct(p.confidence)),
      h("dt", {}, "Spent so far"), h("dd", {}, `${ktok(req.usage.input_tokens + req.usage.output_tokens)} tokens, ${req.usage.tool_calls} tool calls`)),
    h("div", { class: "banner info", style: null },
      "If you approve, the harness applies this to a copy in a fresh sandbox and re-runs the pipeline and quality " +
      "tests on current and last-good data. Nothing outside the sandbox changes; a fix that fails validation is not reported as fixed."),
    recording ? recordedDecision(recording.decision) : [
      nameField("approver"),
      h("div", { class: "field" }, h("label", { for: "feedback" }, "Feedback (for a rejection)"), fb),
      h("div", { class: "row" }, buttons), err]);
}

function recordedDecision(d) {
  const verb = { approve: "approved it", reject: "rejected it", abort: "aborted the fix" };
  return h("div", { class: "banner warn" },
    h("b", {}, "Recording: "), "this is where a person decides (approve, reject with feedback, or abort). ",
    d ? [`In this run, ${d.approver} ${verb[d.decision] || d.decision}`, d.feedback ? `: "${d.feedback}"` : ".",
      " Press Play to continue."] : "The run was still waiting here when it was recorded.");
}

function reportPanel(runId, s, key, replay) {
  const r = s.report, d = r.diagnosis;
  const tone = { fixed: "ok", diagnosed_unfixed: "info", escalated: "bad" }[r.status];
  const parts = [
    h("h2", {}, "Report"),
    h("div", { class: `banner ${tone}` }, `${STATUS[r.status]} — ${r.terminal_reason}`),
  ];
  if (d) {
    parts.push(h("dl", { class: "kv" },
      h("dt", {}, "Summary"), h("dd", {}, d.summary),
      h("dt", {}, "Class"), h("dd", {}, d.failure_class),
      h("dt", {}, "Root cause"), h("dd", {}, d.root_cause),
      h("dt", {}, "Columns"), h("dd", {}, (d.affected_columns || []).join(", ")),
      h("dt", {}, "First bad file"), h("dd", { class: "mono" }, d.first_bad_partition || "—"),
      h("dt", {}, "Suggested fix"), h("dd", {}, d.suggested_fix || "—"),
      h("dt", {}, "Cited evidence"), h("dd", { class: "mono" }, (d.evidence_ids || []).join(", "))));
  }
  if (r.validation) {
    parts.push(h("h3", {}, `Validation in the sandbox: ${r.validation.passed ? "passed" : "failed"}`),
      ...r.validation.checks.map((c) => h("div", { class: `check ${c.ok ? "ok" : "fail"}` },
        h("span", { class: "mark" }, c.ok ? "ok" : "FAIL"), checkDetail(c))));
  }
  if (r.patch) {
    parts.push(h("h3", {}, "Validated patch"), diffView(r.patch),
      h("p", { class: "small" }, replay
        ? h("a", { href: URL.createObjectURL(new Blob([r.patch], { type: "text/x-diff" })), download: `${runId}.patch` }, "Download .patch")
        : h("a", { href: `/api/runs/${runId}/patch` }, "Download .patch"),
        h("span", { class: "muted" }, " · review it and apply it yourself (git apply): the agent never changes your repository.")));
  }
  if (r.approvals?.length) {
    parts.push(h("h3", {}, "Audit trail"), h("table", {}, h("tbody", {}, r.approvals.map((a) => h("tr", {},
      h("td", {}, a.decision), h("td", {}, a.approver), h("td", {}, a.feedback || ""), h("td", { class: "small muted" }, fmtTime(a.decided_at)))))));
  }
  if (key) {
    const g = key.grade || {};
    const row = (label, mine, truth, ok) => h("tr", {}, h("td", {}, label), h("td", {}, mine), h("td", {}, truth),
      h("td", {}, ok == null ? "" : ok ? "✓" : "✗"));
    parts.push(h("h3", {}, "Answer key (from the fault injector; the agent never saw it)"),
      h("div", { class: "table-wrap" }, h("table", {},
        h("thead", {}, h("tr", {}, ["", "Diagnosis", "Answer key", ""].map((x) => h("th", {}, x)))),
        h("tbody", {},
          row("Class", d?.failure_class || "—", key.failure_class, g.failure_class),
          row("Columns", (d?.affected_columns || []).join(", ") || "—", key.affected_columns.join(", "), g.affected_columns),
          row("First bad file", d?.first_bad_partition || "—", key.first_bad_partition, g.first_bad_partition)))),
      h("p", { class: "small muted" }, key.root_cause));
  }
  const u = r.usage;
  parts.push(h("h3", {}, "Spend"), h("p", { class: "small" },
    `${ktok(u.input_tokens)} input + ${ktok(u.output_tokens)} output tokens · ${u.requests} model requests · ${u.tool_calls} tool calls · ` +
    `${s.investigations} investigation rounds · ${s.fix_attempts} fix proposals`),
    h("p", { class: "small muted" }, Object.entries(r.usage_by_model || {}).map(([m, x]) =>
      `${m}: ${ktok(x.input_tokens + x.output_tokens)}`).join(" · ")));
  return h("section", { class: "panel" }, parts);
}

function checkDetail(c) {
  // Some checks carry a whole pipeline log: show the start, fold the rest.
  if (c.detail.length <= 140) return h("span", {}, h("b", {}, c.name), " ", h("span", { class: "detail" }, c.detail));
  return h("details", { class: "detail-fold" }, h("summary", {}, h("b", {}, c.name), " ",
    h("span", { class: "detail" }, `${c.detail.slice(0, 120)}…`)), h("pre", { class: "log" }, c.detail));
}

function investigationPanel(s) {
  const parts = [h("h2", {}, "Investigation")];
  if (s.triage) {
    const t = s.triage;
    parts.push(h("h3", {}, "Triage"), h("dl", { class: "kv" },
      h("dt", {}, "Symptom"), h("dd", {}, t.symptom),
      h("dt", {}, "Outcome"), h("dd", {}, t.run_outcome),
      h("dt", {}, "Candidates"), h("dd", {}, t.candidate_classes.join(", ")),
      h("dt", {}, "Suspects"), h("dd", {}, t.suspect_columns.join(", ") || "—"),
      h("dt", {}, "First checks"), h("dd", {}, t.first_checks.join(" · "))));
  }
  if (s.hypotheses) {
    const top = s.hypotheses.hypotheses.reduce((a, b) => (b.confidence > a.confidence ? b : a));
    parts.push(h("h3", {}, "Hypotheses"), ...s.hypotheses.hypotheses.map((x) =>
      h("div", { class: `hyp ${x === top ? "top" : ""}` },
        h("div", {}, h("b", {}, `${x.id} · ${x.failure_class} · ${pct(x.confidence)}`), " ", x.statement),
        h("div", { class: "small muted" }, `cites ${x.evidence_ids.join(", ")} · would be disproved by: ${x.falsification_check}`))));
  }
  if (s.verification) {
    const v = s.verification;
    parts.push(h("h3", {}, "Verification"), h("p", {}, h("b", {}, `${v.hypothesis_id} ${v.outcome}`), ` — ${v.observations}`),
      h("p", { class: "small muted" }, `cites ${v.evidence_ids.join(", ")}`));
  }
  if (s.fix_feedback?.length) {
    parts.push(h("h3", {}, "Why earlier fix proposals were not accepted"),
      h("ul", { class: "small" }, s.fix_feedback.map((f) => h("li", {}, f))));
  }
  if (parts.length === 1) parts.push(h("p", { class: "empty" }, "Nothing yet."));
  return h("section", { class: "panel" }, parts);
}

function evidencePanel(s) {
  return h("section", { class: "panel" }, h("details", {},
    h("summary", {}, `Evidence (${s.evidence.length}) — every tool call the agent made, recorded by the harness`),
    h("div", { class: "table-wrap" }, h("table", {},
      h("thead", {}, h("tr", {}, ["ID", "Tool", "Arguments", "Result"].map((x) => h("th", {}, x)))),
      h("tbody", {}, s.evidence.map((e) => h("tr", {},
        h("td", { class: "mono" }, e.id), h("td", { class: "mono small" }, e.tool),
        h("td", { class: "mono small" }, JSON.stringify(e.args)), h("td", {}, e.summary))))))));
}

function historyPanel(load) {
  const box = h("div", {}, h("p", { class: "empty" }, "Loading…"));
  const det = h("details", {}, h("summary", {}, "Checkpoints (the graph state is saved after every step)"), box);
  det.addEventListener("toggle", async () => {
    if (!det.open) return;
    try {
      const rows = await load();
      box.replaceChildren(h("div", { class: "table-wrap" }, h("table", {},
        h("thead", {}, h("tr", {}, ["Step", "Next", "Evidence", "Tokens", "Checkpoint"].map((x) => h("th", {}, x)))),
        h("tbody", {}, rows.map((r) => h("tr", {},
          h("td", {}, r.step), h("td", { class: "mono small" }, r.next.join(", ") || "(done)"),
          h("td", {}, r.evidence), h("td", {}, ktok(r.tokens)), h("td", { class: "mono small muted" }, r.checkpoint_id)))))));
    } catch (e) { box.replaceChildren(h("p", { class: "err" }, e.message)); }
  });
  return h("section", { class: "panel" }, det);
}

// --- boot ---------------------------------------------------------------------------------

(async function boot() {
  if (REPLAY) {  // static site: no server, no config
    config = { auth: false };
    window.addEventListener("hashchange", route);
    route();
    return;
  }
  try {
    [config, cases] = await Promise.all([api("/api/config"), api("/api/cases")]);
  } catch (e) {
    document.getElementById("main").replaceChildren(h("div", { class: "banner bad" }, `Cannot reach the server: ${e.message}`));
    return;
  }
  if (config.user) document.getElementById("who").textContent = `signed in as ${config.user}`;
  window.addEventListener("hashchange", route);
  route();
})();
