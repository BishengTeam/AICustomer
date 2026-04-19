# Crawler Usage

## Files
- `dify_spider.py`: 批量请求 Dify API（每题多次）
- `h3cne_test_cases_v1.csv`: 输入样例

## Run
```bash
python src/crawler/dify_spider.py \
  --input src/crawler/h3cne_test_cases_v1.csv \
  --output src/crawler/tmp/dify_result.json \
  --base-url [YOUR_BASE_URL] \
  --api-key [<YOUR_API_KEY>] \
  --api-type workflow \
  --times 3 \
  --concurrency 10
```

## Concurrency

- `--concurrency`：并发请求数，默认 `1`（串行）
- 当前实现为 `asyncio` 调度 + 标准库 HTTP 调用的并发包装，不依赖额外第三方库
- 每道题的多次请求仍按顺序执行；不同题目之间可并发执行，便于加速全量回归

## Input format
支持 `.csv/.json/.jsonl`。

- 问题字段可用：`question` / `query` / `问题`
- 意向回答字段可用：`intended_answer` / `expected_answer` / `answer` / `意向回答` / `标准答案`

CSV 示例：
```csv
question,intended_answer
H3CNE 是什么？,介绍 H3CNE 的定位与适用人群
H3CNE 报名方式是什么？,说明报名入口和报名流程
```
