import re
from typing import Dict, List

TOPIC_DEFAULT_CERT = "H3CNE-RS+"


def contains_any(text: str, keywords: List[str]) -> bool:
    return any(k in text for k in keywords)


def is_high_risk_refuse_query(text: str) -> bool:
    normalized = re.sub(r"\s+", "", (text or "").lower())
    patterns = [
        # 承诺通过类
        r"包过|保过|稳过|一次过|一次就过|包通过|保通过",
        r"保证.*过|保证通过",
        # 试题泄露/押题类
        r"押题|押中|预测题|预测.*题|真题|原题|题库|题库答案|泄题|透题",
        r"考前密卷|内部题|内部答案",
    ]
    return any(re.search(p, normalized) for p in patterns)


def extract_cert_name(text: str) -> str:
    t = (text or "").upper()

    if "H3CNE-RS+" in t or "H3CNE RS+" in t or "RS+" in t:
        return "H3CNE-RS+"
    if "H3CNE" in t:
        return "H3CNE"

    if contains_any(text, ["新华三", "H3C认证", "h3c认证"]):
        return "H3C"

    return ""


def extract_question_type(text: str) -> str:
    if is_high_risk_refuse_query(text):
        return "high_risk_refuse"

    if contains_any(text, ["考试代码", "考什么", "考试内容", "考哪些", "科目", "题型"]):
        return "exam"

    if contains_any(text, ["报名", "怎么报", "去哪报", "在哪里报", "预约考试", "考试平台"]):
        return "registration"

    if contains_any(text, ["成绩", "查分", "分数", "多久出分", "成绩查询"]):
        return "score"

    if contains_any(text, ["有效期", "多久过期", "过期", "续证", "重认证", "刷新有效期"]):
        return "recertification"

    if contains_any(text, ["证书", "领证", "下载证书", "证书发放", "证书查询"]):
        return "certificate"

    if contains_any(
        text,
        [
            "前置",
            "报考条件",
            "报名条件",
            "能不能考",
            "能报吗",
            "我能报吗",
            "零基础",
            "基础要求",
            "必须培训",
            "必须先上课",
            "培训后才能考",
            "培训后才能考试",
            "不培训能报名",
            "自学后报名",
            "可以自学报名",
        ],
    ):
        return "prerequisite"

    if contains_any(text, ["课程", "培训", "学什么", "学习路径", "怎么学", "先学啥"]):
        return "training"

    if contains_any(text, ["适合考哪个证", "推荐哪个证", "考哪个", "怎么选认证"]):
        return "recommendation"

    if contains_any(text, ["是什么", "是干嘛的", "介绍", "有啥用", "有没有用", "适合什么人", "适合谁", "适合人群"]):
        return "intro"

    return "unknown"


def normalize_cert_name(cert_name: str, question_type: str) -> str:
    defaultable_types = {
        "intro",
        "prerequisite",
        "training",
        "exam",
        "registration",
        "score",
        "certificate",
        "recertification",
    }

    if cert_name == "H3CNE":
        return TOPIC_DEFAULT_CERT

    if cert_name == "" and question_type in defaultable_types:
        return TOPIC_DEFAULT_CERT

    return cert_name


def build_missing_fields(cert_name: str, question_type: str) -> List[str]:
    missing = []

    if question_type == "recommendation":
        missing.extend(["user_background", "target_direction"])
    elif question_type == "unknown" and cert_name == "":
        missing.append("cert_name")

    return missing


def build_clarify_text(missing_fields: List[str], question_type: str) -> str:
    if question_type == "recommendation":
        return (
            "为了更准确给你推荐 H3C 认证，我还需要了解两点：\n"
            "1. 你现在的基础如何（零基础 / 有网络基础 / 有项目经验）？\n"
            "2. 你未来想往哪个方向发展（路由交换 / 安全 / 云计算 / 无线）？"
        )

    field_map = {
        "cert_name": "当前应用主要回答 H3CNE-RS+ 相关问题。如果你想问其他 H3C 认证，请明确认证名称，例如 H3CSE-RS+。",
        "user_background": "请补充你的当前基础情况。",
        "target_direction": "请补充你想发展的技术方向。",
    }

    parts = [field_map.get(f, f"请补充字段：{f}") for f in missing_fields]
    return "\n".join(parts) if parts else "请补充更具体的问题信息。"


def build_retrieval_query(cert_name: str, question_type: str, query: str) -> str:
    boost_map = {
        "intro": [
            "H3CNE 是什么",
            "H3CNE 是干嘛的",
            "认证介绍",
            "适合人群",
        ],
        "prerequisite": [
            "H3CNE 有前置条件吗",
            "H3CNE 必须培训后才能考试吗",
            "H3CNE 不培训能报名吗",
            "前置条件",
            "报考条件",
            "是否需要培训",
        ],
        "training": [
            "H3CNE 需要先学啥",
            "H3CNE 学什么",
            "培训课程",
            "学习路径",
        ],
        "exam": [
            "H3CNE 的考试代码是什么",
            "H3CNE 的考试代码是多少",
            "H3CNE考试代码是什么",
            "H3CNE考试代码是多少",
            "考试代码",
            "考试代码是什么",
            "考试代码是多少",
        ],
        "registration": [
            "H3CNE 去哪里报名",
            "H3CNE 去哪报",
            "H3CNE 怎么报名",
            "报名方式",
            "考试预约",
            "官方入口",
        ],
        "score": [
            "H3CNE 成绩在哪里查询",
            "H3CNE 怎么查成绩",
            "成绩查询",
            "查分方式",
        ],
        "certificate": [
            "H3CNE 证书怎么领取",
            "H3CNE 证书怎么下载",
            "证书发放",
            "证书查询",
            "证书下载",
        ],
        "recertification": [
            "H3CNE 怎么重认证",
            "H3CNE 到期后怎么办",
            "H3CNE 到期后是不是只能重考",
            "证书有效期",
            "重认证",
            "刷新有效期",
        ],
        "recommendation": [
            "适合人群",
            "认证路径",
            "认证介绍",
        ],
        "unknown": [],
    }

    parts = [query, cert_name] + boost_map.get(question_type, [])
    cleaned: List[str] = []
    seen = set()
    for part in parts:
        part = re.sub(r"\s+", " ", (part or "")).strip()
        if not part or part in seen:
            continue
        seen.add(part)
        cleaned.append(part)
    return " ".join(cleaned)


def build_refuse_text() -> str:
    return (
        "这个问题我不能直接回答。\n"
        "如果你是在问包过、押题、真题预测或其他无法依据官方资料确认的内容，"
        "建议改问认证介绍、报考条件、考试代码、报名方式、成绩、证书或重认证规则。"
    )


def recognize_intent(query: str) -> Dict:
    query = (query or "").strip()

    if not query:
        return {
            "cert_name": "",
            "question_type": "unknown",
            "need_clarify": True,
            "missing_fields": ["query"],
            "clarify_text": "请输入你的问题，例如：H3CNE 的考试代码是什么？",
            "retrieval_query": "",
            "response_mode": "clarify",
            "direct_refuse": False,
            "refuse_text": "",
            "risk_level": "low",
        }

    cert_name = extract_cert_name(query)
    question_type = extract_question_type(query)

    if question_type == "high_risk_refuse":
        return {
            "cert_name": cert_name,
            "question_type": question_type,
            "need_clarify": False,
            "missing_fields": [],
            "clarify_text": "",
            "retrieval_query": "",
            "response_mode": "refuse",
            "direct_refuse": True,
            "refuse_text": build_refuse_text(),
            "risk_level": "high",
        }

    cert_name = normalize_cert_name(cert_name, question_type)
    missing_fields = build_missing_fields(cert_name, question_type)
    need_clarify = len(missing_fields) > 0
    clarify_text = build_clarify_text(missing_fields, question_type) if need_clarify else ""
    retrieval_query = build_retrieval_query(cert_name, question_type, query) if not need_clarify else ""
    response_mode = "clarify" if need_clarify else "retrieve"

    high_risk_domains = {"exam", "score", "certificate", "recertification", "prerequisite"}
    risk_level = "high" if question_type in high_risk_domains else "normal"

    return {
        "cert_name": cert_name,
        "question_type": question_type,
        "need_clarify": need_clarify,
        "missing_fields": missing_fields,
        "clarify_text": clarify_text,
        "retrieval_query": retrieval_query,
        "response_mode": response_mode,
        "direct_refuse": False,
        "refuse_text": "",
        "risk_level": risk_level,
    }


def main(query: str) -> Dict:
    """
    Dify Code 节点可直接调用的入口函数。
    输入建议：query
    """
    return recognize_intent(query)


if __name__ == "__main__":
    samples = [
        "H3CNE 是什么？",
        "H3CNE 的考试代码是什么？",
        "这个证怎么报名？",
        "我适合考哪个 H3C 认证？",
        "你保证我一次过吗？",
    ]

    for item in samples:
        print(f"\n>>> {item}")
        print(main(item))
