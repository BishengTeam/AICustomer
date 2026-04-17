# Crawler Usage

## Files
- `dify_spider.py`: 批量请求 Dify API（每题多次）
- `dify_cases_example.csv`: 输入样例

## Run
```bash
python src/crawler/dify_spider.py \
  --input src/crawler/dify_cases_example.csv \
  --output src/crawler/tmp/dify_result.json \
  --base-url http://192.168.1.150/v1 \
  --api-key <YOUR_API_KEY> \
  --api-type workflow \
  --times 3
```

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
