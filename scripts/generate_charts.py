#!/usr/bin/env python3
"""Thanatos sample -- reproducible summary + chart generator.

Reads the shipped, already-graded artifacts under this repository:

    <uuid>/task.toml                                       -- task.uuid_v5, keywords[0] (language
                                                               tag), metadata.difficulty (declared,
                                                               not calibrated)
    <uuid>/instruction.md                                   -- first line "# org/repo", the verbatim
                                                               task prompt (actual migration domain)
    <uuid>/trajectories/<model>/run_*/result.json           -- per-run verifier_result.scores
                                                               (score_eval, score_binary, score,
                                                               score_continuous_v2, ...),
                                                               verifier_result.status,
                                                               verifier_result.score_version,
                                                               verifier_result.assay.completion_status,
                                                               verifier_result.assay.code_quality.score,
                                                               agent_result.cost_usd,
                                                               agent_result.metadata.n_episodes
    <uuid>/tests/rubrics.json                                -- per-task item count (weighted,
                                                               judge-scored criteria)
    <uuid>/trajectories/<model>/run_*/verifier/process.json  -- read ONLY for one corroborating
                                                               check (see check_score_composition
                                                               below): its `composition` block is
                                                               not this script's source for any
                                                               aggregate printed or charted

and does three things:

  1. Prints a plain-text, reproducible summary to stdout: a per-task table (every model/task
     cell's run count `n`, since two model/task cells have no runs at all in this corpus), pooled
     (run-weighted) and task-macro (task-weighted) aggregates per model, language coverage,
     declared-difficulty coverage, corpus-wide harness-label counts (verbatim field values, no
     pass/fail reading attached), and rubric item counts. Run this script and diff the printed
     numbers against README.md -- they are the same numbers, computed the same way, from the
     same files.
  2. Regenerates six chart SVGs under images/: mean score_eval by task and mean agent cost by
     task (each light + dark, two-series line charts against the SAME 3 tasks, not a
     difficulty tier), and the language-coverage donut across all 3 tasks (light + dark).
  3. Checks (does not generate from) one corroborating fact: that each scored run's own
     `verifier/process.json` `composition` block reproduces that same run's `result.json`
     `score_eval` via `min(bucket_d_score, bucket_n_ceiling) * score_regression_factor`. This
     is a corroborating check over an independently-shipped field, not a second computation
     this script's aggregates depend on -- every aggregate above is built from `result.json`
     alone.

This script uses only the Python standard library -- Python 3.9+ compatible, including a small
hand-written `task.toml` reader (stdlib `tomllib` requires 3.11+, so it is not used here) --
no third-party charting library, no network access, no dependency installation.

It emits SVG only. It does NOT rasterize PNGs: the matching hero.png-style .png fallbacks are
separate, browser-rendered exports of these exact SVGs, not output of this script.

It also does not execute any task's Docker environment, agent, or verifier -- it only reads
the JSON/TOML/Markdown artifacts already shipped in this repository.

Primary metric: the metric this script (and README.md) treats as primary is the continuous
`score_eval` in [0, 1], reported as a mean, times 100 for a percentage -- it is not a pass
rate. Separately, `verifier_result.scores.score`, `score_binary`, and `score_continuous_v2`
are each `0.0`, and `verifier_result.status` is the literal string `"vacuous"`, on every one
of the 32 scored runs. This script prints those fields verbatim and does not attach a
pass/fail (or any other) reading to them -- their semantics are not defined anywhere in the
shipped data this script reads.
"""

import glob
import json
import math
import os
import statistics
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_DIR = os.path.join(REPO_ROOT, "images")

MODELS = ["claude-opus-5", "glm-5.3"]
EXPECTED_TASKS = 3
EXPECTED_RUN_DIRS = 32
EXPECTED_SCORED = 32


# ---------------------------------------------------------------------------
# Minimal TOML reader for this repo's specific task.toml shape: flat
# `key = "value"` / `key = 123` / `key = true` lines, one string array
# (`keywords = ["a", "b", "c"]`), grouped under `[section]` / `[section.sub]`
# headers. Not a general TOML parser -- deliberately narrow, targeting Python
# 3.9+ compatibility (stdlib tomllib requires 3.11+, so it is not used here),
# and a TOML dependency is out of scope for a stdlib-only script.
# ---------------------------------------------------------------------------
def parse_task_toml(path):
    out = {}
    section = ()
    for raw in open(path, encoding="utf-8"):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("[") and line.endswith("]"):
            section = tuple(line[1:-1].split("."))
            continue
        if "=" not in line:
            continue
        key, val = line.split("=", 1)
        key, val = key.strip(), val.strip()
        node = out
        for part in section:
            node = node.setdefault(part, {})
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            items = [] if not inner else [s.strip().strip('"') for s in inner.split(",")]
            node[key] = items
        elif val.startswith('"') and val.endswith('"'):
            node[key] = val[1:-1]
        elif val in ("true", "false"):
            node[key] = val == "true"
        else:
            try:
                node[key] = int(val)
            except ValueError:
                try:
                    node[key] = float(val)
                except ValueError:
                    node[key] = val
    return out


def repo_from_instruction(uuid):
    """First line of instruction.md is always '# org/repo' in this corpus."""
    path = os.path.join(REPO_ROOT, uuid, "instruction.md")
    with open(path, encoding="utf-8") as f:
        first = f.readline().strip()
    assert first.startswith("# "), f"{uuid}: instruction.md does not open with '# org/repo'"
    return first[2:].strip()


def discover_task_uuids():
    uuids = []
    for entry in sorted(glob.glob(os.path.join(REPO_ROOT, "*/"))):
        name = os.path.basename(entry.rstrip("/"))
        if name in ("images", "scripts") or name.startswith("."):
            continue
        if os.path.isfile(os.path.join(entry, "task.toml")):
            uuids.append(name)
    return uuids


def load_model_cell(uuid, model):
    """Every run directory under trajectories/<model>/ for this task, split into
    scored (has result.json) and the rest. Cell n is NOT assumed uniform -- this
    corpus has 8 runs per populated (task, model) cell, plus two cells with zero
    runs entirely (no glm-5.3/ directory at all for dan-nor98/pypostboy or
    MorAlekss/cli-migration-test-3)."""
    run_dirs = sorted(glob.glob(os.path.join(REPO_ROOT, uuid, "trajectories", model, "run_*")))
    scored = []
    for run_dir in run_dirs:
        result_path = os.path.join(run_dir, "result.json")
        if not os.path.isfile(result_path):
            continue
        d = json.load(open(result_path, encoding="utf-8"))
        vr = d["verifier_result"]
        assay = vr["assay"]
        cq = assay.get("code_quality", {})
        scored.append(
            {
                "run_id": os.path.basename(run_dir),
                "score_eval": vr["scores"]["score_eval"],
                "score_binary": vr["scores"]["score_binary"],
                "score": vr["scores"]["score"],
                "score_continuous_v2": vr["scores"]["score_continuous_v2"],
                "status": vr["status"],
                "score_version": vr["score_version"],
                "completion_status": assay.get("completion_status"),
                "code_quality_score": cq.get("score"),
                "cost_usd": d["agent_result"]["cost_usd"],
                "n_episodes": d["agent_result"]["metadata"].get("n_episodes"),
            }
        )
    return {"n_total": len(run_dirs), "n_scored": len(scored), "scored": scored}


def build_dataset():
    tasks = {}
    for uuid in discover_task_uuids():
        toml = parse_task_toml(os.path.join(REPO_ROOT, uuid, "task.toml"))
        keywords = toml.get("task", {}).get("keywords", [])
        language = keywords[0] if keywords else None
        difficulty = toml.get("metadata", {}).get("difficulty")
        row = {
            "uuid": uuid,
            "repo": repo_from_instruction(uuid),
            "language": language,
            "difficulty": difficulty,
        }
        for model in MODELS:
            row[model] = load_model_cell(uuid, model)
        tasks[uuid] = row
    assert len(tasks) == EXPECTED_TASKS, f"expected {EXPECTED_TASKS} tasks, found {len(tasks)}"

    n_run_dirs = sum(t[m]["n_total"] for t in tasks.values() for m in MODELS)
    n_scored = sum(t[m]["n_scored"] for t in tasks.values() for m in MODELS)
    assert n_run_dirs == EXPECTED_RUN_DIRS, f"expected {EXPECTED_RUN_DIRS} run dirs, found {n_run_dirs}"
    assert n_scored == EXPECTED_SCORED, f"expected {EXPECTED_SCORED} scored runs, found {n_scored}"

    # Cross-check: every scored run's verifier_result.status is the literal string
    # "vacuous", score_version is the literal string "binary", and score_binary is 0.0.
    # This script prints those three fields verbatim (see print_summary) and does not
    # attach a pass/fail or any other reading to them anywhere in this script or in
    # README.md -- their semantics are not defined in the shipped data this script reads.
    for t in tasks.values():
        for m in MODELS:
            for r in t[m]["scored"]:
                assert r["status"] == "vacuous", f"{t['uuid']}/{m}/{r['run_id']}: status != vacuous"
                assert r["score_version"] == "binary", f"{t['uuid']}/{m}/{r['run_id']}: score_version != binary"
                assert r["score_binary"] == 0.0, f"{t['uuid']}/{m}/{r['run_id']}: score_binary != 0.0"
                assert r["score"] == 0.0, f"{t['uuid']}/{m}/{r['run_id']}: score != 0.0"
                assert r["score_continuous_v2"] == 0.0, f"{t['uuid']}/{m}/{r['run_id']}: score_continuous_v2 != 0.0"

    return tasks


def scored_tasks(tasks):
    """The tasks with at least one scored run in at least one model cell (all 3 here)."""
    return {u: t for u, t in tasks.items() if any(t[m]["n_scored"] > 0 for m in MODELS)}


def cell_mean(cell, field):
    vals = [r[field] for r in cell["scored"]]
    return statistics.mean(vals) if vals else None


def pooled_mean(tasks, model, field):
    vals = [r[field] for t in tasks.values() for r in t[model]["scored"]]
    return (statistics.mean(vals), len(vals)) if vals else (None, 0)


def macro_mean(tasks, model, field):
    means = []
    for t in tasks.values():
        if t[model]["n_scored"] == 0:
            continue
        m = cell_mean(t[model], field)
        assert m is not None, f"{t['uuid']}/{model}: n_scored > 0 but cell_mean({field}) is None"
        means.append(m)
    return (statistics.mean(means), len(means)) if means else (None, 0)


def language_counts(tasks):
    counts = {}
    for t in tasks.values():
        lang = t["language"] or "unknown"
        counts[lang] = counts.get(lang, 0) + 1
    unexpected = set(counts) - set(LANGUAGE_ORDER)
    assert not unexpected, (
        f"language tag(s) not in LANGUAGE_ORDER, would be silently dropped from the donut: {unexpected}"
    )
    return counts


def difficulty_counts(tasks):
    counts = {}
    for t in tasks.values():
        d = t["difficulty"] or "unknown"
        counts[d] = counts.get(d, 0) + 1
    return counts


def print_summary(tasks):
    st = scored_tasks(tasks)
    print("=" * 92)
    print(
        f"THANATOS -- {len(tasks)} tasks, {EXPECTED_RUN_DIRS} run directories, "
        f"all {EXPECTED_SCORED} scored (result.json present), {len(MODELS)} models"
    )
    print("=" * 92)

    header = f"{'uuid':<10} {'repo':<24} {'lang':<10} {'diff':<8} {'opus n':>6} {'opus score_eval':>16} {'glm n':>5} {'glm score_eval':>15}"
    print(header)
    print("-" * len(header))
    for uuid in sorted(tasks, key=lambda u: tasks[u]["repo"].lower()):
        t = tasks[uuid]
        oc, gc = t["claude-opus-5"], t["glm-5.3"]
        om = cell_mean(oc, "score_eval")
        gm = cell_mean(gc, "score_eval")
        o_str = f"{om * 100:6.2f}%" if om is not None else f"N/A({oc['n_scored']}/{oc['n_total']})"
        g_str = f"{gm * 100:6.2f}%" if gm is not None else f"N/A({gc['n_scored']}/{gc['n_total']})"
        print(
            f"{uuid[:8]:<10} {t['repo'][:24]:<24} {str(t['language']):<10} {str(t['difficulty']):<8} "
            f"{oc['n_scored']:>3}/{oc['n_total']:<2} {o_str:>16} {gc['n_scored']:>2}/{gc['n_total']:<2} {g_str:>15}"
        )
    print("\nPooled (run-weighted; each of the 32 scored runs counted once) vs. task-macro")
    print("(each of the up-to-3 tasks a model has data on counted once, unequal cell n disclosed above):")
    for model in MODELS:
        p_mean, p_n = pooled_mean(st, model, "score_eval")
        m_mean, m_n = macro_mean(st, model, "score_eval")
        p_cost, _ = pooled_mean(st, model, "cost_usd")
        m_cost, _ = macro_mean(st, model, "cost_usd")
        assert p_mean is not None and m_mean is not None, f"{model}: no scored runs to aggregate score_eval"
        assert p_cost is not None and m_cost is not None, f"{model}: no scored runs to aggregate cost_usd"
        print(
            f"  {model:<14} pooled: n={p_n:>2} mean_score_eval={p_mean * 100:6.2f}%   "
            f"macro: n_tasks={m_n} mean_score_eval={m_mean * 100:6.2f}%   "
            f"pooled_cost=${p_cost:6.2f}   macro_cost=${m_cost:6.2f}"
        )

    both_pooled_vals = [r["score_eval"] for t in st.values() for m in MODELS for r in t[m]["scored"]]
    print(
        f"\n  both models pooled: n={len(both_pooled_vals)} "
        f"mean_score_eval={statistics.mean(both_pooled_vals) * 100:.2f}%"
    )
    task_combined_means = []
    for t in st.values():
        vals = [r["score_eval"] for m in MODELS for r in t[m]["scored"]]
        if vals:
            task_combined_means.append(statistics.mean(vals))
    print(
        f"  both models, task-macro (mean of each task's combined-model mean): "
        f"n_tasks={len(task_combined_means)} mean_score_eval={statistics.mean(task_combined_means) * 100:.2f}%"
    )

    print("\nLanguage coverage (task.toml keywords[0]; no keywords -> 'unknown'; all 3 tasks):")
    for lang, n in sorted(language_counts(tasks).items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {lang:<12} {n} task(s)")

    print("\nDeclared difficulty (task.toml metadata.difficulty; no metadata -> 'unknown'; descriptive tag, not a calibrated tier):")
    for diff, n in sorted(difficulty_counts(tasks).items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"  {diff:<12} {n} task(s)")

    print("\nField values across all 32 scored runs, printed verbatim (semantics not defined in the shipped data):")
    all_scored = [r for t in st.values() for m in MODELS for r in t[m]["scored"]]
    statuses = {}
    versions = {}
    scores = {}
    scores_binary = {}
    scores_cv2 = {}
    completions = {}
    cq_null = cq_present = 0
    for r in all_scored:
        statuses[r["status"]] = statuses.get(r["status"], 0) + 1
        versions[r["score_version"]] = versions.get(r["score_version"], 0) + 1
        scores[r["score"]] = scores.get(r["score"], 0) + 1
        scores_binary[r["score_binary"]] = scores_binary.get(r["score_binary"], 0) + 1
        scores_cv2[r["score_continuous_v2"]] = scores_cv2.get(r["score_continuous_v2"], 0) + 1
        completions[r["completion_status"]] = completions.get(r["completion_status"], 0) + 1
        if r["code_quality_score"] is None:
            cq_null += 1
        else:
            cq_present += 1
    print(f"  verifier_result.status:            {statuses}")
    print(f"  verifier_result.score_version:     {versions}")
    print(f"  verifier_result.scores.score:      {scores}")
    print(f"  verifier_result.scores.score_binary:        {scores_binary}")
    print(f"  verifier_result.scores.score_continuous_v2: {scores_cv2}")
    print(f"  assay.completion_status (counted, not read as an outcome signal): {completions}")
    print(f"  code_quality.score:            null={cq_null} present={cq_present} (null excluded from any quality figure, not treated as 0)")

    comp = check_score_composition(st)
    print(
        f"\nComposition check (verifier/process.json, schema {comp['schema']!r}, corroborating only -- see module docstring):\n"
        f"  score_eval == min(bucket_d_score, bucket_n_ceiling) * score_regression_factor\n"
        f"  reproduced on {comp['n_checked']}/{EXPECTED_SCORED} scored runs, max deviation {comp['max_deviation']:.2e} (< 1e-4)"
    )

    print("\nCost (agent_result.cost_usd, all 32 scored runs):")
    for model in MODELS:
        vals = [r["cost_usd"] for t in st.values() for r in t[model]["scored"]]
        zero = sum(1 for v in vals if v == 0.0)
        print(f"  {model:<14} n={len(vals):>2} mean=${statistics.mean(vals):6.4f} total=${sum(vals):8.2f} reported-$0.00={zero}")

    print("\nPer-task mean agent cost (the same figures the cost-by-task chart plots):")
    for uuid in order_by_repo(st):
        t = st[uuid]
        for model in MODELS:
            m = cell_mean(t[model], "cost_usd")
            if m is not None:
                print(f"  {t['repo']:<34} {model:<14} n={t[model]['n_scored']} mean=${m:.4f}")

    print("\nMean episodes per scored run (agent_result.metadata.n_episodes):")
    for model in MODELS:
        vals = [r["n_episodes"] for t in st.values() for r in t[model]["scored"] if r["n_episodes"] is not None]
        print(f"  {model:<14} n={len(vals):>2} mean_episodes={statistics.mean(vals):.1f}")

    print("\nMean score_eval by assay.completion_status value (reported as-is; no outcome reading attached):")
    for status in ("complete", "incomplete"):
        vals = [r["score_eval"] for t in st.values() for m in MODELS for r in t[m]["scored"] if r["completion_status"] == status]
        if not vals:
            print(f"  {status:<12} n= 0 mean_score_eval=N/A (no runs with this status)")
            continue
        print(f"  {status:<12} n={len(vals):>2} mean_score_eval={statistics.mean(vals) * 100:.2f}%")

    print("\nRubric item counts (tests/rubrics.json, all 3 tasks -- weighted, judge-scored criteria):")
    rubric_counts = load_rubric_item_counts(tasks)
    for uuid in sorted(tasks, key=lambda u: tasks[u]["repo"].lower()):
        print(f"  {tasks[uuid]['repo']:<34} {rubric_counts[uuid]} items")
    print(f"  total: {sum(rubric_counts.values())} items across {len(rubric_counts)} tasks")
    print("=" * 92)


def order_by_repo(st):
    return sorted(st, key=lambda u: st[u]["repo"].lower())


def check_score_composition(st):
    """A corroborating check, not this script's numeric source (see module docstring):
    reads verifier/process.json only for its `composition` block, and asserts that block's
    own formula reproduces the SAME run's already-loaded result.json score_eval. Every
    aggregate this script prints or charts is built from result.json alone, before and
    independent of this check."""
    max_dev = 0.0
    n_checked = 0
    schemas = set()
    for uuid, t in st.items():
        for model in MODELS:
            for r in t[model]["scored"]:
                proc_path = os.path.join(REPO_ROOT, uuid, "trajectories", model, r["run_id"], "verifier", "process.json")
                p = json.load(open(proc_path, encoding="utf-8"))
                comp = p["composition"]
                schemas.add(comp["schema"])
                predicted = min(comp["bucket_d_score"], comp["bucket_n_ceiling"]) * comp["score_regression_factor"]
                max_dev = max(max_dev, abs(predicted - r["score_eval"]))
                n_checked += 1
    assert n_checked == EXPECTED_SCORED, f"expected to check {EXPECTED_SCORED} runs, checked {n_checked}"
    assert schemas == {"thanatos.bucket-composition/v1"}, f"unexpected composition schema(s): {schemas}"
    assert max_dev < 1e-4, f"composition formula does not reproduce score_eval within 1e-4 (max deviation {max_dev})"
    return {"n_checked": n_checked, "max_deviation": max_dev, "schema": next(iter(schemas))}


def load_rubric_item_counts(tasks):
    counts = {}
    for uuid in tasks:
        path = os.path.join(REPO_ROOT, uuid, "tests", "rubrics.json")
        d = json.load(open(path, encoding="utf-8"))
        counts[uuid] = len(d.get("items", []))
    return counts


# ---------------------------------------------------------------------------
# SVG chart rendering
# ---------------------------------------------------------------------------
FONT_SERIF = "Georgia, 'Iowan Old Style', 'Times New Roman', ui-serif, serif"
FONT_MONO = "'JetBrains Mono','SF Mono','Berkeley Mono',ui-monospace,'Courier New',monospace"


def theme(dark):
    if dark:
        return dict(
            bg=("#050c0c", "#0a1e1c", "#071313"),
            text="#eef2ea",
            muted="#9fc4bc",
            grid="rgba(143,227,212,0.16)",
            axis="rgba(143,227,212,0.4)",
            teal="#35d0ba",
            gold="#e2ac52",
            marker_ring="#0f2723",
            donut_hub_fill="#0f2723",
            donut_hub_stroke="rgba(143,227,212,0.16)",
        )
    return dict(
        bg=("#faf8f4", "#f3efe6", "#faf8f4"),
        text="#0a1414",
        muted="#4a6560",
        grid="rgba(10,30,28,0.10)",
        axis="rgba(10,30,28,0.35)",
        teal="#0e8a78",
        gold="#b9781f",
        marker_ring="#ffffff",
        donut_hub_fill="#ffffff",
        donut_hub_stroke="rgba(10,30,28,0.10)",
    )


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def svg_header(w, h, title, th):
    return (
        f'<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
        f'role="img" aria-label="{esc(title)}">\n<defs>\n'
        f'<linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">'
        f'<stop offset="0%" stop-color="{th["bg"][0]}"/>'
        f'<stop offset="60%" stop-color="{th["bg"][1]}"/>'
        f'<stop offset="100%" stop-color="{th["bg"][2]}"/></linearGradient>\n'
        f'<filter id="glow" x="-80%" y="-80%" width="260%" height="260%"><feGaussianBlur stdDeviation="6"/></filter>\n'
        f"</defs>\n"
        f'<rect width="{w}" height="{h}" fill="url(#bg)"/>\n'
    )


def make_line_chart(path, title, subtitle, footnotes, categories, series_a, series_b, y_max, y_step, value_fmt, th):
    """series_a / series_b: list of dicts {"value": float|None, "n": int} aligned to categories.
    A None value means the model has zero scored runs on that task -- rendered as an N/A tick
    on the baseline, and the line breaks around it rather than interpolating across the gap."""
    W, H = 1600, 900
    left, right, top, bottom = 130, 1540, 160, 712
    plot_w = right - left
    k = len(categories)

    LABEL_GAP = 34
    N_GAP = 20
    STACK_GAP = 40
    STACK_THRESHOLD = 50
    BOTTOM_CLEARANCE = 100
    TOP_CLEARANCE = 70

    for s in list(series_a) + list(series_b):
        if s["value"] is not None:
            assert 0 <= s["value"] <= y_max, f"{title!r}: value {s['value']} outside [0, {y_max}]"

    def xpos(i):
        return left + (i + 0.5) * (plot_w / k)

    def ypos(v):
        return bottom - (v / y_max) * (bottom - top)

    out = [svg_header(W, H, title, th)]
    out.append(f'<text x="{left}" y="62" font-family="{FONT_SERIF}" font-size="38" fill="{th["text"]}">{esc(title)}</text>\n')
    out.append(f'<text x="{left}" y="94" font-family="{FONT_MONO}" font-size="19" fill="{th["muted"]}">{esc(subtitle)}</text>\n')

    out.append(f'<line x1="1120" y1="42" x2="1156" y2="42" stroke="{th["teal"]}" stroke-width="4" stroke-linecap="round"/>\n')
    out.append(f'<circle cx="1138" cy="42" r="6.5" fill="{th["teal"]}" stroke="{th["marker_ring"]}" stroke-width="2"/>\n')
    out.append(f'<text x="1170" y="49" font-family="{FONT_MONO}" font-size="19" fill="{th["text"]}">claude-opus-5</text>\n')
    out.append(f'<line x1="1360" y1="42" x2="1396" y2="42" stroke="{th["gold"]}" stroke-width="3.5" stroke-dasharray="9 7" stroke-linecap="round"/>\n')
    out.append(f'<polygon points="1378,35 1385,42 1378,49 1371,42" fill="{th["gold"]}" stroke="{th["gold"]}" stroke-width="1.5"/>\n')
    out.append(f'<text x="1408" y="49" font-family="{FONT_MONO}" font-size="19" fill="{th["text"]}">glm-5.3</text>\n')

    n_lines = int(round(y_max / y_step)) + 1
    for i in range(n_lines):
        v = i * y_step
        y = ypos(v)
        out.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="{th["grid"]}" stroke-width="1"/>\n')
        out.append(f'<text x="{left - 16}" y="{y + 7:.1f}" text-anchor="end" font-family="{FONT_MONO}" font-size="18" fill="{th["muted"]}">{value_fmt(v, axis=True)}</text>\n')
    y0 = ypos(0)
    out.append(f'<line x1="{left}" y1="{y0:.1f}" x2="{right}" y2="{y0:.1f}" stroke="{th["axis"]}" stroke-width="2"/>\n')

    xs = [xpos(i) for i in range(k)]
    for x in xs:
        out.append(f'<line x1="{x:.1f}" y1="{top}" x2="{x:.1f}" y2="{bottom}" stroke="{th["grid"]}" stroke-width="1" stroke-dasharray="2 5"/>\n')

    def draw_series(series, color, dashed):
        pts = [(x, ypos(s["value"])) if s["value"] is not None else None for x, s in zip(xs, series)]
        run = []
        segs = []
        for p in pts:
            if p is None:
                if len(run) > 1:
                    segs.append(run)
                run = []
            else:
                run.append(p)
        if len(run) > 1:
            segs.append(run)
        for seg in segs:
            pts_str = " ".join(f"{x:.1f},{y:.1f}" for x, y in seg)
            dash = ' stroke-dasharray="9 7"' if dashed else ""
            out.append(f'<polyline points="{pts_str}" fill="none" stroke="{color}"{dash} stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>\n')
        return pts

    pts_a = draw_series(series_a, th["teal"], False)
    pts_b = draw_series(series_b, th["gold"], True)

    for i, (x, cat) in enumerate(zip(xs, categories)):
        pa, pb = pts_a[i], pts_b[i]
        if pb is not None:
            _, yb = pb
            out.append(f'<polygon points="{x:.1f},{yb - 10:.1f} {x + 10:.1f},{yb:.1f} {x:.1f},{yb + 10:.1f} {x - 10:.1f},{yb:.1f}" fill="{th["gold"]}" opacity="0.28" filter="url(#glow)"/>\n')
            out.append(f'<polygon points="{x:.1f},{yb - 10:.1f} {x + 10:.1f},{yb:.1f} {x:.1f},{yb + 10:.1f} {x - 10:.1f},{yb:.1f}" fill="{th["gold"]}" stroke="{th["gold"]}" stroke-width="1.5"/>\n')
        if pa is not None:
            _, ya = pa
            out.append(f'<circle cx="{x:.1f}" cy="{ya:.1f}" r="9" fill="{th["teal"]}" opacity="0.28" filter="url(#glow)"/>\n')
            out.append(f'<circle cx="{x:.1f}" cy="{ya:.1f}" r="8" fill="{th["teal"]}" stroke="{th["marker_ring"]}" stroke-width="3"/>\n')

        if pa is None and pb is None:
            out.append(f'<text x="{x:.1f}" y="{y0 - 14:.1f}" text-anchor="middle" font-family="{FONT_MONO}" font-size="18" font-weight="bold" fill="{th["muted"]}">N/A</text>\n')
        elif pa is None:
            out.append(f'<text x="{x:.1f}" y="{y0 - 14:.1f}" text-anchor="middle" font-family="{FONT_MONO}" font-size="17" font-weight="bold" fill="{th["muted"]}">opus: N/A</text>\n')
        elif pb is None:
            out.append(f'<text x="{x:.1f}" y="{y0 - 14:.1f}" text-anchor="middle" font-family="{FONT_MONO}" font-size="17" font-weight="bold" fill="{th["muted"]}">glm: N/A</text>\n')

        ya = pa[1] if pa is not None else None
        yb = pb[1] if pb is not None else None

        def side_for(y_self, y_other):
            # Forced sides take priority over the natural (relative-to-the-other-series)
            # choice: a marker sitting close to the bottom axis must never place its label
            # below it, straight into the category-label band; likewise near the top edge.
            if bottom - y_self < BOTTOM_CLEARANCE:
                return "above"
            if y_self - top < TOP_CLEARANCE:
                return "below"
            if y_other is None:
                return "above"
            return "above" if y_self <= y_other else "below"

        side_a = side_for(ya, yb) if ya is not None else None
        side_b = side_for(yb, ya) if yb is not None else None

        value_y = {}
        if ya is not None and yb is not None and side_a == side_b and abs(ya - yb) < STACK_THRESHOLD:
            # Both labels want the same side AND the two markers sit close together:
            # stacking them (nearest marker's label closest in, the other pushed one
            # full block further out) is the only way to keep the two 2-line blocks
            # from overlapping each other, since independent placement would not.
            if side_a == "above":
                anchor = min(ya, yb)
                order = ("a", "b") if ya <= yb else ("b", "a")
                for rank, s in enumerate(order):
                    value_y[s] = anchor - LABEL_GAP - rank * STACK_GAP
            else:
                anchor = max(ya, yb)
                order = ("a", "b") if ya >= yb else ("b", "a")
                for rank, s in enumerate(order):
                    value_y[s] = anchor + LABEL_GAP + rank * STACK_GAP
        else:
            if ya is not None:
                value_y["a"] = ya - LABEL_GAP if side_a == "above" else ya + LABEL_GAP
            if yb is not None:
                value_y["b"] = yb - LABEL_GAP if side_b == "above" else yb + LABEL_GAP

        if pa is not None:
            va = series_a[i]["value"]
            ly = min(max(value_y["a"], top + 18), bottom - 10)
            out.append(f'<text x="{x:.1f}" y="{ly:.1f}" text-anchor="middle" font-family="{FONT_MONO}" font-size="18" font-weight="bold" fill="{th["teal"]}">{esc(value_fmt(va))}</text>\n')
            out.append(f'<text x="{x:.1f}" y="{ly + N_GAP:.1f}" text-anchor="middle" font-family="{FONT_MONO}" font-size="14" fill="{th["muted"]}">n={series_a[i]["n"]}</text>\n')
        if pb is not None:
            vb = series_b[i]["value"]
            ly = min(max(value_y["b"], top + 18), bottom - 10)
            out.append(f'<text x="{x:.1f}" y="{ly:.1f}" text-anchor="middle" font-family="{FONT_MONO}" font-size="18" font-weight="bold" fill="{th["gold"]}">{esc(value_fmt(vb))}</text>\n')
            out.append(f'<text x="{x:.1f}" y="{ly + N_GAP:.1f}" text-anchor="middle" font-family="{FONT_MONO}" font-size="14" fill="{th["muted"]}">n={series_b[i]["n"]}</text>\n')

        label_y = bottom + 34 + (18 if i % 2 else 0)
        out.append(f'<text x="{x:.1f}" y="{label_y}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="19" fill="{th["text"]}">{esc(cat)}</text>\n')

    # Empirical width for this monospace font at font-size 15 (measured via
    # SVGTextElement.getBBox in a browser); guards against a footnote silently
    # running off the right edge of the canvas instead of visibly failing here.
    FOOTNOTE_CHAR_WIDTH = 9.1
    max_chars = int((right - left) / FOOTNOTE_CHAR_WIDTH)
    fy = 800
    for line in footnotes:
        assert len(line) <= max_chars, (
            f"{title!r} footnote is {len(line)} chars, wider than the canvas fits (~{max_chars} chars): {line!r}"
        )
        out.append(f'<text x="{left}" y="{fy}" font-family="{FONT_MONO}" font-size="15" fill="{th["muted"]}">{esc(line)}</text>\n')
        fy += 22
    out.append("</svg>\n")
    text = "".join(out)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return text


def make_donut(path, title, subtitle, segments, th, dark):
    """segments: list of (key, label, count, light_hex, dark_hex)."""
    W, H = 1600, 1200
    cx, cy = 672.0, 672.0
    R, r = 330.0, 190.0
    total = sum(s[2] for s in segments)

    out = [svg_header(W, H, title, th)]
    out.append(f'<text x="80" y="90" font-family="{FONT_SERIF}" font-size="44" fill="{th["text"]}">{esc(title)}</text>\n')
    out.append(f'<text x="80" y="128" font-family="{FONT_MONO}" font-size="21" fill="{th["muted"]}">{esc(subtitle)}</text>\n')

    angle = -90.0
    rounded_pct_sum = 0
    for key, label, count, light_hex, dark_hex in segments:
        color = dark_hex if dark else light_hex
        frac = count / total
        rounded_pct_sum += round(100.0 * frac)
        span = frac * 360.0
        a0, a1 = math.radians(angle), math.radians(angle + span)
        large_arc = 1 if span > 180 else 0

        ox0, oy0 = cx + R * math.cos(a0), cy + R * math.sin(a0)
        ox1, oy1 = cx + R * math.cos(a1), cy + R * math.sin(a1)
        ix1, iy1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        ix0, iy0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        if span >= 359.999:
            # A full-circle wedge degenerates in SVG arc syntax (start == end draws
            # nothing), so a 100% segment is drawn as an annulus instead.
            d = (
                f"M {cx - R:.2f} {cy:.2f} A {R:.0f} {R:.0f} 0 1 1 {cx + R:.2f} {cy:.2f} "
                f"A {R:.0f} {R:.0f} 0 1 1 {cx - R:.2f} {cy:.2f} Z "
                f"M {cx - r:.2f} {cy:.2f} A {r:.0f} {r:.0f} 0 1 0 {cx + r:.2f} {cy:.2f} "
                f"A {r:.0f} {r:.0f} 0 1 0 {cx - r:.2f} {cy:.2f} Z"
            )
            out.append(f'<path d="{d}" fill="{color}" fill-rule="evenodd" stroke="{th["bg"][1]}" stroke-width="3"/>\n')
        else:
            d = (
                f"M {ox0:.2f} {oy0:.2f} A {R:.0f} {R:.0f} 0 {large_arc} 1 {ox1:.2f} {oy1:.2f} "
                f"L {ix1:.2f} {iy1:.2f} A {r:.0f} {r:.0f} 0 {large_arc} 0 {ix0:.2f} {iy0:.2f} Z"
            )
            out.append(f'<path d="{d}" fill="{color}" stroke="{th["bg"][1]}" stroke-width="3"/>\n')

        mid = math.radians(angle + span / 2.0)
        cosm, sinm = math.cos(mid), math.sin(mid)
        lead_x0, lead_y0 = cx + (R + 8) * cosm, cy + (R + 8) * sinm
        lead_x1, lead_y1 = cx + (R + 55) * cosm, cy + (R + 55) * sinm
        out.append(f'<line x1="{lead_x0:.1f}" y1="{lead_y0:.1f}" x2="{lead_x1:.1f}" y2="{lead_y1:.1f}" stroke="{color}" stroke-width="2"/>\n')
        out.append(f'<circle cx="{lead_x0:.1f}" cy="{lead_y0:.1f}" r="6" fill="{color}"/>\n')

        anchor_x, anchor_y = cx + (R + 90) * cosm, cy + (R + 90) * sinm
        right_side = cosm >= 0
        if right_side:
            rect_x = anchor_x
            text_x = rect_x + 18 + 16
            text_anchor = "start"
        else:
            rect_x = anchor_x - 18
            text_x = rect_x - 16
            text_anchor = "end"
        rect_y = anchor_y - 18
        out.append(f'<rect x="{rect_x:.1f}" y="{rect_y:.1f}" width="18" height="18" rx="3" fill="{color}"/>\n')
        out.append(f'<text x="{text_x:.1f}" y="{rect_y + 18:.1f}" text-anchor="{text_anchor}" font-family="{FONT_SERIF}" font-size="30" font-weight="bold" fill="{th["text"]}">{esc(label)}</text>\n')
        pct = 100.0 * frac
        plural = "s" if count != 1 else ""
        out.append(f'<text x="{text_x:.1f}" y="{rect_y + 50:.1f}" text-anchor="{text_anchor}" font-family="{FONT_MONO}" font-size="20" fill="{th["muted"]}">{count} task{plural} &#183; {pct:.0f}%</text>\n')

        angle += span

    out.append(f'<circle cx="{cx}" cy="{cy}" r="184" fill="{th["donut_hub_fill"]}" stroke="{th["donut_hub_stroke"]}" stroke-width="1.5"/>\n')
    out.append(f'<text x="{cx}" y="{cy - 6}" text-anchor="middle" font-family="{FONT_SERIF}" font-size="86" font-weight="bold" fill="{th["text"]}">{total}</text>\n')
    out.append(f'<text x="{cx}" y="{cy + 34}" text-anchor="middle" font-family="{FONT_MONO}" font-size="22" letter-spacing="4" fill="{th["muted"]}">TASKS</text>\n')
    out.append(f'<text x="{cx}" y="{cy + 66}" text-anchor="middle" font-family="{FONT_MONO}" font-size="18" fill="{th["muted"]}">{len(segments)} categor{"ies" if len(segments) != 1 else "y"}</text>\n')
    if rounded_pct_sum != 100:
        note = f"each share is rounded to the nearest whole percent; rounded shares sum to {rounded_pct_sum}%, not 100%"
        out.append(f'<text x="80" y="1150" font-family="{FONT_MONO}" font-size="16" fill="{th["muted"]}">{esc(note)}</text>\n')
    out.append("</svg>\n")
    text = "".join(out)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return text


LANGUAGE_LABEL = {"python": "Python", "go": "Go", "unknown": "Unknown"}
LANGUAGE_COLORS = {
    "python": ("#b9781f", "#e8b968"),
    "go": ("#123230", "#8aa39c"),
    "unknown": ("#6b6b63", "#9a9a90"),
}
LANGUAGE_ORDER = ["python", "go", "unknown"]


def main():
    os.makedirs(IMAGES_DIR, exist_ok=True)
    tasks = build_dataset()
    print_summary(tasks)

    st = scored_tasks(tasks)
    order = sorted(st, key=lambda u: st[u]["repo"].lower())
    # Chart x-axis labels use the repo-only path segment (e.g. "pypostboy", not
    # "dan-nor98/pypostboy") -- full org/repo strings do not fit legibly
    # side by side at this width; the full org/repo is in README.md's task table.
    categories = [st[u]["repo"].split("/")[-1] for u in order]

    def series(model, field, scale=1.0):
        out = []
        for u in order:
            cell = st[u][model]
            m = cell_mean(cell, field)
            out.append({"value": (m * scale) if m is not None else None, "n": cell["n_scored"]})
        return out

    for dark in (False, True):
        th = theme(dark)
        suffix = "dark" if dark else "light"

        make_line_chart(
            os.path.join(IMAGES_DIR, f"score_eval_by_task-{suffix}.svg"),
            title="Mean score_eval by task",
            subtitle="continuous score_eval \u00d7 100, mean of each cell's scored runs \u2014 not a pass rate",
            footnotes=[
                "3 tasks, alphabetical by repo \u00b7 each populated cell has n=8 runs, disclosed under each point \u2014 two glm-5.3 cells have no runs at all",
                "score_binary, score, score_continuous_v2 are 0.0; status is the literal string \"vacuous\" on all 32 runs \u2014 shown as-is, no pass/fail reading",
                "lines are a visual guide between categorical points, not a continuous trend; a gap marks a model with 0 scored runs on that task",
            ],
            categories=categories,
            series_a=series("claude-opus-5", "score_eval", 100.0),
            series_b=series("glm-5.3", "score_eval", 100.0),
            y_max=100,
            y_step=20,
            value_fmt=lambda v, axis=False: (f"{v:.0f}%" if axis else f"{v:.2f}%"),
            th=th,
        )
        make_line_chart(
            os.path.join(IMAGES_DIR, f"cost_by_task-{suffix}.svg"),
            title="Mean agent cost by task",
            subtitle="USD, agent_result.cost_usd \u2014 scored subset only, mean of each cell's scored runs",
            footnotes=[
                "3 tasks, alphabetical by repo \u00b7 each populated cell has n=8 runs, disclosed under each point",
                "glm-5.3 reports $0.00 on the one task it ran (all 8 glm-5.3 scored runs) \u2014 shown as reported, not imputed or excluded",
            ],
            categories=categories,
            series_a=series("claude-opus-5", "cost_usd"),
            series_b=series("glm-5.3", "cost_usd"),
            y_max=14,
            y_step=2,
            value_fmt=lambda v, axis=False: (f"${v:.0f}" if axis else f"${v:.2f}"),
            th=th,
        )

        counts = language_counts(tasks)
        segments = [
            (lang, LANGUAGE_LABEL[lang], counts.get(lang, 0), LANGUAGE_COLORS[lang][0], LANGUAGE_COLORS[lang][1])
            for lang in LANGUAGE_ORDER
            if counts.get(lang, 0) > 0
        ]
        declared_n = len([lang for lang in LANGUAGE_ORDER if lang != "unknown" and counts.get(lang, 0) > 0])
        unknown_part = " + 1 unknown bucket" if counts.get("unknown", 0) > 0 else ""
        n_repos = len(set(t["repo"] for t in tasks.values()))
        make_donut(
            os.path.join(IMAGES_DIR, f"tasks_by_language-{suffix}.svg"),
            title="Language coverage",
            subtitle=f"{len(tasks)} tasks, {declared_n} declared language tag{'s' if declared_n != 1 else ''}{unknown_part}, {n_repos} distinct upstream repositories",
            segments=segments,
            th=th,
            dark=dark,
        )

    print(f"\nWrote 6 SVGs to {os.path.relpath(IMAGES_DIR, REPO_ROOT)}/ "
          f"(score_eval_by_task, cost_by_task, tasks_by_language -- each light + dark).")
    print("SVG only: matching .png fallbacks are separate browser-rendered exports, not produced by this script.")


if __name__ == "__main__":
    sys.exit(main())
