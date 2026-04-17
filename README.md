# AI Customer

- 这是存放AI客服相关代码与文档的仓库。
- 所有关于项目文档的文件都在docs目录下。


## Crawler

- Crawler script path: `src/crawler/dify_spider.py`
- Example input path: `src/crawler/dify_cases_example.csv`

Run:

```bash
python src/crawler/dify_spider.py \
  --input src/crawler/dify_cases_example.csv \
  --output src/crawler/tmp/dify_result.json \
  --base-url http://192.168.1.150/v1 \
  --api-key <YOUR_API_KEY> \
  --api-type workflow \
  --times 3
```


