---
name: h3cne-rag-eval
description: Use when optimizing H3CNE / H3CNE-RS+ RAG data in this repository, running Dify regression tests directly with src/crawler/dify_spider.py, comparing src/crawler/tmp/dify_result.md with docs/H3CNE/H3CNE_测试问题清单_V1.md, updating pass/fail remarks, or prioritizing fixes for failed test cases such as T003 T004 T005 T009 T019 T022.
---

# H3CNE RAG Eval

用于这个仓库里的 **H3CNE / H3CNE-RS+ 知识优化、批量测试、结果判分、问题清单分析**。

## 何时使用

当用户要你做以下任一事情时使用：

- 优化 H3CNE 知识切片 / 高风险字段 / Chatflow
- 执行 Dify 批量回归测试
- 对照 `src/crawler/tmp/dify_result.md` 更新 `docs/H3CNE/H3CNE_测试问题清单_V1.md`
- 对比本轮与上一轮结果
- 根据失败题号给出修复优先级

## 先读哪些文件

按这个顺序读，避免跑偏：

1. `docs/H3CNE/H3CNE_测试问题清单_V1.md`
2. `src/crawler/tmp/dify_result.md`
3. `src/crawler/h3cne_test_cases_v1.csv`
4. `src/crawler/h3cne_test_cases_v1_positive_only.csv`
5. `src/crawler/dify_spider.py`
6. 需要定位问题时再读 `references/file-map.md`

如果是行为问题，再读：

- `src/AI客服.yml`

如果是知识问题，再按题号读对应切片：

- `T004/T019` → `docs/H3CNE/H3CNE-RS+清洗数据/切片版/12_H3CNE-RS+_考试代码与方向区分.md`
- `T009/T022` → `docs/H3CNE/H3CNE-RS+清洗数据/切片版/09_H3CNE-RS+_重认证说明.md`
- `T005/T013` → `docs/H3CNE/H3CNE-RS+清洗数据/切片版/05_H3CNE-RS+_报名方式.md`
- `T003/T020` → `docs/H3CNE/H3CNE-RS+清洗数据/切片版/13_H3CNE-RS+_是否必须培训与报名条件.md`
- `T006` → `docs/H3CNE/H3CNE-RS+清洗数据/切片版/06_H3CNE-RS+_成绩查询.md`
- `T007` → `docs/H3CNE/H3CNE-RS+清洗数据/切片版/07_H3CNE-RS+_证书发放与下载.md`
- `T008/T014/T021` → `docs/H3CNE/H3CNE-RS+清洗数据/切片版/08_H3CNE-RS+_证书有效期.md`

高风险统一口径再读：

- `src/Suggestion/10_H3CNE-RS+_高风险字段正式版.md`

## 标准工作流

### 1) 优化数据

先按失败题号定位，再最小修改：

- 考试代码：先修 `12_考试代码与方向区分`
- 重认证：先修 `09_重认证说明`
- 报名入口：先修 `05_报名方式`
- 前置条件：先修 `13_是否必须培训与报名条件`

修改原则：

- 一份切片只承接一个主题
- 对高风险字段尽量给 **可直接回答模板**
- 不把“推荐”写成“强制”
- 不把“到期前”和“到期后”混答
- 当前专题默认按 `H3CNE-RS+` 理解

### 2) 执行测试

测试对话**只使用** `src/crawler/dify_spider.py`。

本 skill 不再维护单独的包装脚本；统一直接执行 `src/crawler/dify_spider.py`，参数、输出结构和 Markdown 报告逻辑都以它为准。

#### 正向用例测试

```powershell
python src/crawler/dify_spider.py `
  --input src/crawler/h3cne_test_cases_v1_positive_only.csv `
  --output src/crawler/tmp/dify_result.json `
  --markdown-output src/crawler/tmp/dify_result.md `
  --base-url http://192.168.1.150/v1 `
  --api-key <YOUR_KEY> `
  --api-type workflow `
  --workflow-input-key query `
  --times 3 `
  --timeout 60 `
  --user batch-evaluator
```

#### 全量用例测试

```powershell
python src/crawler/dify_spider.py `
  --input src/crawler/h3cne_test_cases_v1.csv `
  --output src/crawler/tmp/dify_result.json `
  --markdown-output src/crawler/tmp/dify_result.md `
  --base-url http://192.168.1.150/v1 `
  --api-key <YOUR_KEY> `
  --api-type workflow `
  --workflow-input-key query `
  --times 3 `
  --timeout 60 `
  --user batch-evaluator
```

#### 保留多轮结果

不要覆盖默认 `dify_result.*`，直接指定输出文件名：

```powershell
python src/crawler/dify_spider.py `
  --input src/crawler/h3cne_test_cases_v1.csv `
  --output src/crawler/tmp/h3cne_full_<TAG>.json `
  --markdown-output src/crawler/tmp/h3cne_full_<TAG>.md `
  --base-url http://192.168.1.150/v1 `
  --api-key <YOUR_KEY> `
  --api-type workflow `
  --workflow-input-key query `
  --times 3 `
  --timeout 60 `
  --user batch-evaluator
```

#### 关键参数说明

`src/crawler/dify_spider.py` 当前支持这些关键参数：

- `--input`：输入测试集，支持 `.csv / .json / .jsonl`
- `--output`：JSON 结果输出路径
- `--markdown-output`：Markdown 报告输出路径；不填时默认和 JSON 同名 `.md`
- `--base-url`：Dify 服务地址
- `--api-key`：Dify API Key
- `--api-type`：`workflow` 或 `chat`
- `--workflow-input-key`：workflow 模式下问题所在字段，默认 `query`
- `--times`：每题请求次数
- `--timeout`：单次请求超时秒数
- `--delay`：请求间隔秒数
- `--user`：传给 Dify 的 user 字段

#### 分析脚本代码时要抓住的实现点

如果要修改测试逻辑，优先直接看 `src/crawler/dify_spider.py` 里的这些函数：

- `load_cases()`：决定输入文件怎么读
- `build_payload()`：决定请求体怎么组装
- `call_dify()`：决定怎么请求 Dify 接口
- `extract_answer()`：决定从响应里提取哪个字段
- `write_markdown()`：决定 `dify_result.md` 的结构

也就是说，这个 skill 里的“测试对话代码”默认就指 `src/crawler/dify_spider.py` 本体。

### 3) 分析问题清单

对照 `src/crawler/tmp/dify_result.md` 更新：

- `docs/H3CNE/H3CNE_测试问题清单_V1.md`

更新规则：

- 出现在结果里的题：必须写 `是否通过` 与 `备注`
- 未出现在结果里的题：标记 `未测`
- 备注要写 **为什么通过 / 为什么不通过**
- 高风险题要重点看：是否乱编、是否前后不一致、是否给依据
- 更新 `综合评分` 与 `测试结论`

### 4) 对比两轮结果

至少输出：

- 上一轮通过数 vs 本轮通过数
- 新增通过题号
- 回退题号
- 持续失败题号
- 下一步修复优先级

## 输出要求

默认按这个顺序汇报：

1. 本轮结果
2. 核心问题
3. 已修改文件
4. 下一步建议

引用文件时使用内联路径，如：

- `docs/H3CNE/H3CNE_测试问题清单_V1.md`
- `src/crawler/tmp/dify_result.md`

## 不要做的事

- 不要把测试清单、风险清单、历史草稿整包导回知识库
- 不要只说“去官网看”，要尽量给入口 / 渠道 / 步骤
- 不要因为保守就把本可回答的问题全答成“无法确认”
- 不要在没有证据时扩写考试代码、重认证规则、报名要求

## 附加资源

- 文件定位参考：`references/file-map.md`
- 测试权威脚本：`src/crawler/dify_spider.py`
