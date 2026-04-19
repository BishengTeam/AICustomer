import re
from typing import Dict, List

TOPIC_DEFAULT_CERT = "H3CNE-RS+"


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", "", (text or "").lower())


def contains_any(text: str, keywords: List[str]) -> bool:
    return any(k in text for k in keywords)


def contains_any_normalized(text: str, keywords: List[str]) -> bool:
    normalized = normalize_text(text)
    return any(k in normalized for k in keywords)


def is_high_risk_refuse_query(text: str) -> bool:
    normalized = normalize_text(text)
    patterns = [
        # 承诺通过类
        r"包过|保过|稳过|一次过|一次就过|包通过|保通过",
        r"保证.*过|保证通过",
        # 试题泄露/押题类
        r"押题|押中|预测题|预测.*题|真题|原题|题库|题库答案|泄题|透题",
        r"考前密卷|内部题|内部答案",
    ]
    return any(re.search(p, normalized) for p in patterns)


def is_value_query(text: str) -> bool:
    return contains_any_normalized(
        text,
        [
            "还有用吗",
            "还有必要考吗",
            "有必要考吗",
            "值不值得考",
            "值得考吗",
            "还有必要学吗",
            "有必要学吗",
            "还有必要拿吗",
            "有必要拿吗",
        ],
    )


def should_clarify_registration_target(text: str) -> bool:
    return contains_any_normalized(
        text,
        [
            "这个怎么报名",
            "这个怎么报",
            "这个如何报名",
            "这个如何报",
            "怎么报名",
            "怎么报",
        ],
    )


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

    if is_value_query(text):
        return "value"

    if contains_any(text, ["考试代码", "考什么", "考试内容", "考哪些", "科目", "题型", "exam code", "examcode"]):
        return "exam"

    if contains_any(
        text,
        [
            "适合考哪个证",
            "推荐哪个证",
            "考哪个",
            "怎么选认证",
            "从哪个证书开始",
            "从哪个 H3C 证书开始",
            "从哪个认证开始",
            "从哪个 H3C 认证开始",
            "认证路线",
            "路线怎么选",
            "最适合入门",
            "先考 H3CNE 还是别的",
            "先考H3CNE还是别的",
        ],
    ):
        return "recommendation"

    if contains_any(
        text,
        [
            "前置",
            "报考条件",
            "报名条件",
            "能不能考",
            "能报吗",
            "我能报吗",
            "我能报名吗",
            "能报名吗",
            "零基础",
            "基础要求",
            "必须培训",
            "一定要先参加培训",
            "必须先上课",
            "培训后才能考",
            "培训后才能考试",
            "参加培训才能考",
            "先参加培训才能考",
            "不培训能报名",
            "自学后报名",
            "可以自学报名",
        ],
    ):
        return "prerequisite"

    if contains_any(
        text,
        ["报名", "怎么报", "去哪报", "在哪里报", "预约考试", "考试平台", "报名入口", "预约平台", "在哪个平台预约", "约考"],
    ):
        return "registration"

    if contains_any(text, ["成绩", "查分", "分数", "多久出分", "成绩查询"]):
        return "score"

    if contains_any(text, ["有效期", "多久过期", "过期", "续证", "重认证", "刷新有效期"]):
        return "recertification"

    if contains_any(
        text,
        ["课程", "培训", "学什么", "学习路径", "怎么学", "先学啥", "主要学", "学哪些内容", "学习内容", "课程内容", "主要学什么"],
    ):
        return "training"

    if contains_any(
        text,
        [
            "领证",
            "拿证",
            "拿证入口",
            "领证入口",
            "电子证书",
            "下载证书",
            "证书下载",
            "下载入口",
            "证书发放",
            "证书查询",
            "证书领取",
            "领取证书",
            "证书怎么领",
            "证书在哪下载",
            "证书去哪里下载",
            "证书去哪里领",
            "通过后证书",
            "下载电子证书",
            "查看证书",
        ],
    ):
        return "certificate"

    if contains_any(
        text,
        ["是什么", "是干嘛的", "介绍", "有啥用", "有没有用", "适合什么人", "适合谁", "适合人群", "哪些岗位", "适合哪些岗位", "什么岗位", "在职运维", "学生还是在职运维"],
    ):
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
        "value",
    }

    if cert_name == "H3CNE":
        return TOPIC_DEFAULT_CERT

    if cert_name == "" and question_type in defaultable_types:
        return TOPIC_DEFAULT_CERT

    return cert_name


def build_missing_fields(query: str, cert_name: str, question_type: str) -> List[str]:
    missing = []

    if question_type == "recommendation":
        missing.extend(["user_background", "target_direction"])
    elif question_type == "value":
        missing.append("value_dimension")
    elif cert_name == "" and question_type == "prerequisite":
        missing.append("cert_name")
    elif cert_name == "" and question_type == "registration" and should_clarify_registration_target(query):
        missing.append("cert_name")
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

    if question_type == "value":
        return (
            "你这里说的“还有用/还有必要考”，可能是在问两件不同的事：\n"
            "1. 你想问 H3CNE-RS+ 现在值不值得考、对求职或学习有没有帮助；\n"
            "2. 你想问 H3CNE-RS+ 证书是否还在有效期内、会不会过期。\n"
            "你更想了解哪一种？"
        )

    field_map = {
        "cert_name": "当前应用主要回答 H3CNE-RS+ 相关问题。如果你想问其他 H3C 认证，请明确认证名称，例如 H3CSE-RS+。",
        "user_background": "请补充你的当前基础情况。",
        "target_direction": "请补充你想发展的技术方向。",
        "value_dimension": "请补充你更想了解证书价值，还是证书是否仍有效。",
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
            "适合哪些岗位",
            "学生还是在职运维",
        ],
        "prerequisite": [
            "H3CNE 有前置条件吗",
            "H3CNE 必须培训后才能考试吗",
            "H3CNE 一定要先参加培训吗",
            "H3CNE 先参加培训才能考试吗",
            "H3CNE 不培训能报名吗",
            "前置条件",
            "报考条件",
            "是否需要培训",
        ],
        "training": [
            "H3CNE 需要先学啥",
            "H3CNE 学什么",
            "H3CNE 学习内容有哪些",
            "H3CNE 课程内容有哪些",
            "培训课程",
            "学习路径",
            "主要学哪些内容",
            "课程内容",
            "计算机网络基础 H3C 网络设备操作 局域网交换 IP 路由 SDN",
        ],
        "exam": [
            "H3CNE 的考试代码是什么",
            "H3CNE 的考试代码是多少",
            "H3CNE考试代码是什么",
            "H3CNE考试代码是多少",
            "考试代码",
            "考试代码是什么",
            "考试代码是多少",
            "exam code",
        ],
        "registration": [
            "H3CNE 去哪里报名",
            "H3CNE 去哪报",
            "H3CNE 怎么报名",
            "报名方式",
            "考试预约",
            "官方入口",
            "报名入口",
            "预约平台",
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
            "H3CNE 通过后证书去哪里下载",
            "H3CNE 证书在哪下载",
            "H3CNE 证书去哪里下载",
            "H3CNE 通过后怎么领取电子证书",
            "证书发放",
            "证书查询",
            "证书下载",
            "拿证入口",
            "电子证书在哪领",
            "证书查询与下载入口",
            "新华三技术认证官微 证书查询",
            "http://www.h3c.com/CN/BizPortal/TrainingPartner/Tester/AP_Edu_SearchScoreLogin.aspx",
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
            "从哪个认证开始",
            "从哪个 H3C 证书开始",
            "认证路线怎么选",
            "最适合入门",
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

    raw_cert_name = extract_cert_name(query)
    question_type = extract_question_type(query)

    if question_type == "high_risk_refuse":
        return {
            "cert_name": raw_cert_name,
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

    cert_name = normalize_cert_name(raw_cert_name, question_type)
    missing_fields = build_missing_fields(query, raw_cert_name, question_type)
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
