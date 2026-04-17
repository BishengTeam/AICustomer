# AI Customer

AI Customer 是一个面向 **B 端知识型问答 / 客服场景** 的项目仓库，当前聚焦于：

- 通用 AI 客服方案设计与需求沉淀
- H3C 认证场景（尤其是 `H3CNE` / `H3CNE-RS+`）的知识整理
- 基于规则的意图识别原型
- 连接 Dify Workflow 的前端演示页面

目前仓库处于 **方案设计 + 原型验证** 阶段，既包含产品文档，也包含少量可运行代码，适合用于后续继续做知识库、工作流、前端接入和业务验证。

## 项目目标

这个仓库的核心目标，是沉淀一个可复用的 AI 客服底座，用于支持不同业务场景的快速适配。当前重点包括：

- 把非结构化业务资料整理成可检索、可问答的知识内容
- 为高频客服问题建立稳定的意图识别与分流逻辑
- 通过 Dify Workflow 快速验证问答链路
- 为后续扩展到更多认证/培训/咨询类业务提供基础结构

## 当前仓库包含什么

### 1. 产品与方案文档
`docs/` 目录下保存了当前项目的 PRD、MVP 计划、AB 测试方案、领域知识整理等内容，是理解业务背景的主要入口。

### 2. Python 原型代码
当前提供了一个 H3C 认证问答场景的意图识别原型：

- 识别认证名称，如 `H3CNE`、`H3CNE-RS+`
- 识别问题类型，如介绍、报名、成绩、证书、重认证等
- 对高风险问题做直接拒答
- 在信息不完整时生成澄清话术
- 生成可用于后续检索的查询语句

核心文件：`src/h3cne_intent_recognizer.py`

### 3. 前端演示页面
`src/client/` 下提供了一个非常轻量的静态页面，可直接输入问题并调用 Dify Workflow 接口，便于演示问答流程。

## 目录结构

```text
.
├─ docs/                              # 产品文档、方案、知识整理材料
│  ├─ Universal_AI_Customer_Service_PRD.md
│  ├─ Exam_AI_Customer_Service_MVP_Dify_Flow_Design.md
│  ├─ Exam_AI_Customer_Service_MVP_One_Week_Plan.md
│  ├─ H3C_AI_Customer_Service_AB_Plan.md
│  └─ H3CNE/
│     ├─ H3CNE-RS+FAQ_V1.md
│     ├─ H3CNE_测试问题清单_V1.md
│     ├─ H3CNE_高风险问题清单.md
│     └─ H3CNE-RS+清洗数据/
├─ src/
│  ├─ h3cne_intent_recognizer.py      # H3C 场景意图识别原型
│  └─ client/
│     ├─ index.html                   # 静态演示页面
│     ├─ app.js                       # Dify Workflow 调用逻辑
│     └─ styles.css                   # 页面样式
├─ main.py                            # Python 入口占位文件
├─ pyproject.toml                     # 项目基础配置
└─ README.md
```

## 快速开始

### 环境要求

- Python `>= 3.13`

当前项目没有额外三方依赖，适合先做原型验证。

### 运行 Python 示例

执行入口文件：

```bash
python main.py
```

当前 `main.py` 只是一个占位示例。

如果你想直接验证 H3C 意图识别逻辑，可以运行：

```bash
python src/h3cne_intent_recognizer.py
```

该脚本内置了一组示例问题，会输出识别结果。

### 前端演示页面

前端页面位于：

- `src/client/index.html`

当前页面通过 `src/client/app.js` 中配置的 Dify Workflow 接口发起请求。使用前请先根据你的环境确认：

- `BASE_URL`
- `API_KEY`
- Workflow 接口是否可访问

如果只是本地预览页面结构，直接用浏览器打开 `index.html` 即可；如果要联调接口，请确保目标服务可访问且配置正确。

## 意图识别原型说明

`src/h3cne_intent_recognizer.py` 当前实现了一个基于规则的 PoC，适合作为后续接入工作流、知识库或模型前置分流器的基础。

### 已支持的识别维度

- **认证名称识别**：`H3CNE`、`H3CNE-RS+`、`H3C`
- **问题类型识别**：
  - `intro`
  - `prerequisite`
  - `training`
  - `exam`
  - `registration`
  - `score`
  - `certificate`
  - `recertification`
  - `recommendation`
  - `high_risk_refuse`
  - `unknown`

### 输出能力

识别结果会返回一个字典，重点字段包括：

- `cert_name`：识别出的认证名称
- `question_type`：问题类型
- `need_clarify`：是否需要补充信息
- `missing_fields`：缺失字段
- `clarify_text`：澄清话术
- `retrieval_query`：用于知识检索的查询语句
- `response_mode`：建议后续走澄清还是检索
- `direct_refuse` / `refuse_text`：高风险拒答控制
- `risk_level`：风险等级

## 文档导航

如果你准备继续推进这个项目，建议按下面顺序阅读：

### 产品与方案

- `docs/Universal_AI_Customer_Service_PRD.md`：通用 AI 客服项目 PRD
- `docs/Exam_AI_Customer_Service_MVP_Dify_Flow_Design.md`：Dify Flow 设计
- `docs/Exam_AI_Customer_Service_MVP_One_Week_Plan.md`：MVP 一周推进计划
- `docs/H3C_AI_Customer_Service_AB_Plan.md`：AB 测试/对比方案

### H3CNE 领域资料

- `docs/H3CNE/H3CNE-RS+FAQ_V1.md`：FAQ 草稿
- `docs/H3CNE/H3CNE_测试问题清单_V1.md`：测试问题清单
- `docs/H3CNE/H3CNE_高风险问题清单.md`：高风险问题定义
- `docs/H3CNE/H3CNE-RS+清洗数据/`：清洗后的知识内容与切片材料

## 当前状态

当前仓库更偏向 **“业务方案 + 原型验证”**，还不是完整的生产项目。现状包括：

- 有较完整的业务文档沉淀
- 有可运行的规则意图识别原型
- 有一个可用于联调 Dify 的轻量前端页面
- 暂未形成完整的后端服务、测试体系和部署方式

## 建议的下一步

如果后续继续建设，建议优先做下面几件事：

1. 将 `h3cne_intent_recognizer.py` 从单文件原型整理为可测试模块
2. 为意图识别补充单元测试和样例集
3. 把前端中的接口地址和密钥改为环境配置而不是硬编码
4. 结合 `docs/H3CNE/` 的清洗数据，建立正式知识库检索链路
5. 增加后端 API 层，统一承接前端、规则判断和工作流调用

## 适用场景

这个仓库适合用于：

- AI 客服 / AI 助手项目的前期方案设计
- 培训认证类业务的问答原型搭建
- Dify Workflow 联调验证
- 基于知识库 + 规则分流的客服实验项目

---

如果你是第一次接手这个仓库，建议先看：

1. `docs/Universal_AI_Customer_Service_PRD.md`
2. `docs/H3CNE/` 下的业务资料
3. `src/h3cne_intent_recognizer.py`
4. `src/client/` 前端演示页面
