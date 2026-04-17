from __future__ import annotations

import argparse
import csv
import json
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple
from urllib import error, request

QUESTION_KEYS = ("question", "query", "问题")
ANSWER_KEYS = ("intended_answer", "expected_answer", "answer", "意向回答", "标准答案")


@dataclass
class ApiResult:
    ok: bool
    status_code: int
    elapsed_ms: int
    answer: str
    raw_json: Dict[str, Any]
    error: str


def pick_value(row: Dict[str, Any], candidates: Tuple[str, ...], default: str = "") -> str:
    for key in candidates:
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return default


def load_cases(input_path: Path) -> List[Dict[str, str]]:
    suffix = input_path.suffix.lower()
    if suffix == ".csv":
        return load_cases_from_csv(input_path)
    if suffix == ".json":
        return load_cases_from_json(input_path)
    if suffix == ".jsonl":
        return load_cases_from_jsonl(input_path)
    raise ValueError("仅支持 .csv / .json / .jsonl 输入文件")


def load_cases_from_csv(input_path: Path) -> List[Dict[str, str]]:
    cases: List[Dict[str, str]] = []
    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError("CSV 缺少表头")

        for line_no, row in enumerate(reader, start=2):
            question = pick_value(row, QUESTION_KEYS)
            if not question:
                continue
            intended_answer = pick_value(row, ANSWER_KEYS)
            cases.append(
                {
                    "question": question,
                    "intended_answer": intended_answer,
                    "source_line": str(line_no),
                }
            )

    return cases


def load_cases_from_json(input_path: Path) -> List[Dict[str, str]]:
    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, list):
        raise ValueError("JSON 输入必须是数组")

    cases: List[Dict[str, str]] = []
    for idx, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            continue
        question = pick_value(item, QUESTION_KEYS)
        if not question:
            continue
        intended_answer = pick_value(item, ANSWER_KEYS)
        cases.append(
            {
                "question": question,
                "intended_answer": intended_answer,
                "source_line": str(idx),
            }
        )
    return cases


def load_cases_from_jsonl(input_path: Path) -> List[Dict[str, str]]:
    cases: List[Dict[str, str]] = []
    with input_path.open("r", encoding="utf-8") as f:
        for idx, line in enumerate(f, start=1):
            text = line.strip()
            if not text:
                continue
            item = json.loads(text)
            if not isinstance(item, dict):
                continue
            question = pick_value(item, QUESTION_KEYS)
            if not question:
                continue
            intended_answer = pick_value(item, ANSWER_KEYS)
            cases.append(
                {
                    "question": question,
                    "intended_answer": intended_answer,
                    "source_line": str(idx),
                }
            )
    return cases


def extract_answer(payload: Dict[str, Any]) -> str:
    if not isinstance(payload, dict):
        return ""

    answer = payload.get("answer")
    if isinstance(answer, str) and answer.strip():
        return answer.strip()

    data = payload.get("data")
    if isinstance(data, dict):
        inner_answer = data.get("answer")
        if isinstance(inner_answer, str) and inner_answer.strip():
            return inner_answer.strip()

        outputs = data.get("outputs")
        if isinstance(outputs, dict):
            for key in ("answer", "text", "result", "output", "content"):
                value = outputs.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
            for value in outputs.values():
                if isinstance(value, str) and value.strip():
                    return value.strip()

    return ""


def call_dify(url: str, api_key: str, body: Dict[str, Any], timeout: int) -> ApiResult:
    request_body = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        url,
        data=request_body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    start = time.perf_counter()
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            response_text = resp.read().decode("utf-8", errors="replace")
            status_code = int(resp.getcode())
            elapsed_ms = int((time.perf_counter() - start) * 1000)
            parsed = json.loads(response_text) if response_text else {}
            answer = extract_answer(parsed)
            return ApiResult(
                ok=200 <= status_code < 300,
                status_code=status_code,
                elapsed_ms=elapsed_ms,
                answer=answer,
                raw_json=parsed if isinstance(parsed, dict) else {"raw": parsed},
                error="",
            )
    except error.HTTPError as e:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        err_text = e.read().decode("utf-8", errors="replace")
        parsed: Dict[str, Any]
        try:
            candidate = json.loads(err_text) if err_text else {}
            parsed = candidate if isinstance(candidate, dict) else {"raw": candidate}
        except json.JSONDecodeError:
            parsed = {"raw": err_text}
        return ApiResult(
            ok=False,
            status_code=int(getattr(e, "code", 0) or 0),
            elapsed_ms=elapsed_ms,
            answer=extract_answer(parsed),
            raw_json=parsed,
            error=f"HTTPError: {e}",
        )
    except Exception as e:  # noqa: BLE001
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return ApiResult(
            ok=False,
            status_code=0,
            elapsed_ms=elapsed_ms,
            answer="",
            raw_json={},
            error=f"{type(e).__name__}: {e}",
        )


def build_payload(api_type: str, question: str, user: str, workflow_input_key: str) -> Dict[str, Any]:
    if api_type == "workflow":
        return {
            "inputs": {workflow_input_key: question},
            "response_mode": "blocking",
            "user": user,
        }

    return {
        "inputs": {},
        "query": question,
        "response_mode": "blocking",
        "conversation_id": "",
        "user": user,
    }


def write_markdown(output_path: Path, results: Dict[str, Any]) -> None:
    lines: List[str] = []
    lines.append("# Dify 批量问答结果")
    lines.append("")
    lines.append(f"- 生成时间: {results['generated_at']}")
    lines.append(f"- Dify 接口: {results['request']['url']}")
    lines.append(f"- 每题请求次数: {results['request']['times']}")
    lines.append("")

    for idx, item in enumerate(results["results"], start=1):
        lines.append(f"## {idx}. {item['question']}")
        lines.append("")
        lines.append(f"- 意向回答: {item['intended_answer'] or '（未提供）'}")
        lines.append("")
        for attempt in item["attempts"]:
            lines.append(
                f"- 第 {attempt['attempt']} 次 | 状态: {attempt['status_code']} | 成功: {attempt['ok']} | 耗时: {attempt['elapsed_ms']}ms"
            )
            if attempt["error"]:
                lines.append(f"  - 错误: {attempt['error']}")
            lines.append(f"  - 返回: {attempt['answer'] or '（无可提取 answer 字段）'}")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="批量请求 Dify API（每个问题请求多次并落盘）")
    parser.add_argument("--input", required=True, help="输入文件（.csv/.json/.jsonl）")
    parser.add_argument(
        "--output",
        default="src/crawler/tmp/dify_result.json",
        help="输出 JSON 文件路径，默认 src/crawler/tmp/dify_result.json",
    )
    parser.add_argument("--base-url", required=True, help="Dify 服务地址，例如 http://127.0.0.1/v1")
    parser.add_argument("--api-key", required=True, help="Dify API Key")
    parser.add_argument(
        "--api-type",
        choices=["chat", "workflow"],
        default="chat",
        help="接口类型：chat -> /chat-messages，workflow -> /workflows/run",
    )
    parser.add_argument("--times", type=int, default=3, help="每个问题请求次数，默认 3")
    parser.add_argument("--timeout", type=int, default=60, help="单次请求超时（秒）")
    parser.add_argument("--delay", type=float, default=0.0, help="每次请求之间间隔（秒）")
    parser.add_argument("--user", default="batch-evaluator", help="传给 Dify 的 user 字段")
    parser.add_argument(
        "--workflow-input-key",
        default="query",
        help="workflow 接口中承载问题的 inputs 字段名，默认 query",
    )
    parser.add_argument(
        "--markdown-output",
        default="",
        help="可选：额外导出一份 Markdown 报告路径",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.times < 1:
        raise ValueError("--times 必须 >= 1")

    input_path = Path(args.input)
    output_path = Path(args.output)
    markdown_path = Path(args.markdown_output) if args.markdown_output else output_path.with_suffix(".md")

    cases = load_cases(input_path)
    if not cases:
        raise ValueError("输入中没有可用问题，请检查列名是否包含 question / query / 问题")

    endpoint = "/chat-messages" if args.api_type == "chat" else "/workflows/run"
    base_url = args.base_url.rstrip("/")
    request_url = f"{base_url}{endpoint}"

    all_results: List[Dict[str, Any]] = []

    for idx, case in enumerate(cases, start=1):
        question = case["question"]
        intended_answer = case["intended_answer"]

        attempts: List[Dict[str, Any]] = []
        for attempt_idx in range(1, args.times + 1):
            user_id = f"{args.user}-{idx}-{attempt_idx}-{uuid.uuid4().hex[:6]}"
            payload = build_payload(args.api_type, question, user_id, args.workflow_input_key)
            api_result = call_dify(request_url, args.api_key, payload, args.timeout)

            attempts.append(
                {
                    "attempt": attempt_idx,
                    "ok": api_result.ok,
                    "status_code": api_result.status_code,
                    "elapsed_ms": api_result.elapsed_ms,
                    "answer": api_result.answer,
                    "error": api_result.error,
                    "raw": api_result.raw_json,
                }
            )

            if args.delay > 0 and attempt_idx < args.times:
                time.sleep(args.delay)

        all_results.append(
            {
                "index": idx,
                "source_line": case["source_line"],
                "question": question,
                "intended_answer": intended_answer,
                "attempts": attempts,
            }
        )

    result_doc = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "request": {
            "url": request_url,
            "api_type": args.api_type,
            "times": args.times,
            "timeout": args.timeout,
            "delay": args.delay,
            "workflow_input_key": args.workflow_input_key,
        },
        "results": all_results,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result_doc, ensure_ascii=False, indent=2), encoding="utf-8")

    if markdown_path:
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(markdown_path, result_doc)

    print(f"完成：共处理 {len(all_results)} 个问题，每题 {args.times} 次")
    print(f"JSON 输出：{output_path}")
    print(f"Markdown 输出：{markdown_path}")


if __name__ == "__main__":
    main()
