#!/usr/bin/env python3
"""
n8n_analyze.py - Static analysis of an n8n workflow export.

Given a workflow JSON file, extracts:
- Node graph (adjacency list + trigger identification)
- Credential requirements
- External API surface (outbound URLs + inbound webhooks)
- Expression dependencies (which nodes reference which upstream nodes)
- Code node bodies
- Secret-smell detection

Usage:
    python n8n_analyze.py path/to/workflow.json
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

TRIGGER_TYPE_SUFFIXES = (
    "trigger", "webhook", "cron", "formtrigger",
    "executeworkflowtrigger", "errortrigger", "chattrigger",
    "manualtrigger", "scheduletrigger",
)

URL_RE = re.compile(r"https?://[^\s\"'<>)}]+", re.IGNORECASE)

NODE_REF_RES = [
    re.compile(r'\$\(\s*[\'"]([^\'"]+)[\'"]\s*\)'),
    re.compile(r'\$node\[\s*[\'"]([^\'"]+)[\'"]\s*\]'),
    re.compile(r'\$items\(\s*[\'"]([^\'"]+)[\'"]\s*'),
]

EXPR_BLOCK_RE = re.compile(r"\{\{(.+?)\}\}", re.DOTALL)

SECRET_PATTERNS = [
    (re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"), "OpenAI-style key"),
    (re.compile(r"\bAIza[0-9A-Za-z_-]{20,}\b"), "Google API key"),
    (re.compile(r"\bxox[abrsp]-[A-Za-z0-9-]{10,}\b"), "Slack token"),
    (re.compile(r"\bghp_[A-Za-z0-9]{20,}\b"), "GitHub PAT"),
    (re.compile(r"(?i)bearer\s+[A-Za-z0-9._\-]{20,}"), "Bearer header"),
    (re.compile(r"(?i)(api[_-]?key|secret|password|token)['\"]?\s*[:=]\s*['\"][^'\"\s]{8,}"), "key/secret literal"),
]


def iter_strings(obj: Any) -> Iterable[str]:
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from iter_strings(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_strings(v)


def is_trigger(node: dict) -> bool:
    t = node.get("type", "").lower()
    return any(t.endswith(suffix) or suffix in t for suffix in TRIGGER_TYPE_SUFFIXES)


def iter_expressions(value: Any) -> Iterable[str]:
    for s in iter_strings(value):
        if s.startswith("="):
            for m in EXPR_BLOCK_RE.finditer(s[1:]):
                yield m.group(1)


def build_graph(wf: dict) -> dict:
    adj = defaultdict(list)
    for src, outputs in (wf.get("connections") or {}).items():
        for conn_type, port_list in outputs.items():
            for out_idx, targets in enumerate(port_list or []):
                for t in targets or []:
                    adj[src].append({
                        "target": t["node"],
                        "connectionType": conn_type,
                        "outputIndex": out_idx,
                    })
    return dict(adj)


def find_triggers(wf: dict) -> list[str]:
    referenced = {
        t["node"]
        for outs in (wf.get("connections") or {}).values()
        for port in outs.values()
        for lst in port or []
        for t in lst or []
    }
    triggers = []
    for n in wf.get("nodes", []):
        if is_trigger(n) or n["name"] not in referenced:
            triggers.append(n["name"])
    seen, out = set(), []
    for name in triggers:
        if name not in seen:
            seen.add(name)
            out.append(name)
    return out


def credential_requirements(wf: dict) -> dict:
    req = defaultdict(list)
    for n in wf.get("nodes", []):
        for cred_type, ref in (n.get("credentials") or {}).items():
            req[cred_type].append({
                "node": n["name"],
                "credentialName": (ref or {}).get("name"),
                "credentialId": (ref or {}).get("id"),
            })
    return dict(req)


def external_endpoints(wf: dict) -> dict:
    outbound, inbound = defaultdict(set), defaultdict(set)
    for n in wf.get("nodes", []):
        params = n.get("parameters") or {}
        for s in iter_strings(params):
            for m in URL_RE.findall(s):
                outbound[n["name"]].add(m.rstrip(".,);"))
        if n.get("webhookId"):
            path = params.get("path") or n["webhookId"]
            inbound[n["name"]].add(f"/webhook/{path}")
    return {
        "outbound": {k: sorted(v) for k, v in outbound.items()},
        "inbound": {k: sorted(v) for k, v in inbound.items()},
    }


def expression_dependencies(wf: dict) -> dict:
    deps = {}
    for n in wf.get("nodes", []):
        refs = set()
        for expr in iter_expressions(n.get("parameters") or {}):
            for rx in NODE_REF_RES:
                refs.update(rx.findall(expr))
        if refs:
            deps[n["name"]] = sorted(refs)
    return deps


def code_nodes(wf: dict) -> list[dict]:
    hits = []
    for n in wf.get("nodes", []):
        t = n.get("type", "")
        if t in {"n8n-nodes-base.code", "n8n-nodes-base.function", "n8n-nodes-base.functionItem"}:
            p = n.get("parameters") or {}
            hits.append({
                "node": n["name"],
                "language": p.get("language", "javaScript"),
                "code": p.get("jsCode") or p.get("pythonCode") or p.get("functionCode"),
            })
    return hits


def secret_smell_test(wf: dict) -> list[dict]:
    findings = []
    for n in wf.get("nodes", []):
        for s in iter_strings(n.get("parameters") or {}):
            for rx, label in SECRET_PATTERNS:
                if rx.search(s):
                    findings.append({
                        "node": n["name"],
                        "kind": label,
                        "sample": s[:120],
                    })
                    break
    return findings


def analyze(path: Path) -> dict:
    wf = json.loads(path.read_text())
    return {
        "workflow": {
            "name": wf.get("name"),
            "id": wf.get("id"),
            "active": wf.get("active"),
            "nodeCount": len(wf.get("nodes", [])),
            "executionOrder": (wf.get("settings") or {}).get("executionOrder"),
            "errorWorkflow": (wf.get("settings") or {}).get("errorWorkflow"),
        },
        "triggers": find_triggers(wf),
        "graph": build_graph(wf),
        "credentials": credential_requirements(wf),
        "endpoints": external_endpoints(wf),
        "expressionDependencies": expression_dependencies(wf),
        "codeNodes": code_nodes(wf),
        "possibleSecrets": secret_smell_test(wf),
        "pinnedNodes": list((wf.get("pinData") or {}).keys()),
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: n8n_analyze.py <workflow.json>", file=sys.stderr)
        sys.exit(2)
    result = analyze(Path(sys.argv[1]))
    json.dump(result, sys.stdout, indent=2, default=str)
    print()
