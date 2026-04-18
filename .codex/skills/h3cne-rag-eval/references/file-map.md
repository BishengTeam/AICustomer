# H3CNE RAG Eval 文件映射

## 1. 测试与输出

| 路径 | 用途 |
| --- | --- |
| `src/crawler/h3cne_test_cases_v1.csv` | 全量 25 题回归集 |
| `src/crawler/h3cne_test_cases_v1_positive_only.csv` | 正向题回归集 |
| `src/crawler/tmp/dify_result.md` | 最新 Markdown 测试结果 |
| `src/crawler/tmp/dify_result.json` | 最新 JSON 测试结果 |
| `docs/H3CNE/H3CNE_测试问题清单_V1.md` | 人工判分清单 |

## 2. 行为层

| 路径 | 用途 |
| --- | --- |
| `src/AI客服.yml` | Dify Chatflow 导出文件 |
| `src/crawler/h3cne_intent_recognizer.py` | 意图识别逻辑参考 |

## 3. 知识层

| 症状 / 题号 | 优先看哪个文件 |
| --- | --- |
| 考试代码答不出来 / `T004 T019` | `docs/H3CNE/H3CNE-RS+清洗数据/切片版/12_H3CNE-RS+_考试代码与方向区分.md` |
| 重认证答不出来 / `T009 T022` | `docs/H3CNE/H3CNE-RS+清洗数据/切片版/09_H3CNE-RS+_重认证说明.md` |
| 报名入口太泛 / `T005 T013` | `docs/H3CNE/H3CNE-RS+清洗数据/切片版/05_H3CNE-RS+_报名方式.md` |
| 前置条件过度保守 / `T003 T020` | `docs/H3CNE/H3CNE-RS+清洗数据/切片版/13_H3CNE-RS+_是否必须培训与报名条件.md` |
| 成绩查询不清楚 / `T006` | `docs/H3CNE/H3CNE-RS+清洗数据/切片版/06_H3CNE-RS+_成绩查询.md` |
| 证书下载不清楚 / `T007` | `docs/H3CNE/H3CNE-RS+清洗数据/切片版/07_H3CNE-RS+_证书发放与下载.md` |
| 有效期口径不稳 / `T008 T014 T021` | `docs/H3CNE/H3CNE-RS+清洗数据/切片版/08_H3CNE-RS+_证书有效期.md` |

## 4. 高风险统一口径

| 路径 | 用途 |
| --- | --- |
| `src/Suggestion/10_H3CNE-RS+_高风险字段正式版.md` | 高风险字段统一答法 |
| `src/Suggestion/收集.md` | 当前项目收口口径的原始整理 |
