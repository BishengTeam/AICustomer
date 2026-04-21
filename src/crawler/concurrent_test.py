import asyncio
import aiohttp
import time
from typing import List, Dict

# 接口配置
API_URL = "http://192.168.1.150/v1/workflows/run"
API_KEY = "app-d1nktiKrJQpYpvIs0LhX4jNj"
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# 测试用的问题列表（共100种不同问法，覆盖真实用户提问习惯）
TEST_QUERIES = [
    # === 1. H3CNE是什么相关（10种） ===
    "H3CNE是什么？",
    "什么是H3CNE？",
    "H3CNE指的是什么？",
    "H3CNE是什么证书？",
    "H3CNE是什么认证？",
    "想问下H3CNE是什么？",
    "H3CNE到底是什么东西？",
    "H3CNE是什么意思？",
    "经常听说H3CNE，是什么呀？",
    "H3CNE是啥？",

    # === 2. H3CNE考试代码相关（10种） ===
    "H3CNE的考试代码是什么？",
    "H3CNE考试的代码是多少？",
    "H3CNE的报考代码是什么？",
    "H3CNE考试代号是多少？",
    "H3CNE的考试编号是什么？",
    "考H3CNE的考试代码是啥？",
    "H3CNE考试对应的代码是什么？",
    "想问下H3CNE的考试代码是多少？",
    "H3CNE考试的报名代码是什么？",
    "H3CNE的考试代码是多少呀？",

    # === 3. H3CNE报名相关（10种） ===
    "H3CNE怎么报名？",
    "H3CNE怎么报考？",
    "想考H3CNE要怎么报名？",
    "H3CNE考试怎么报名？",
    "H3CNE的报名方式是什么？",
    "怎么报名参加H3CNE考试？",
    "H3CNE在哪里报名？",
    "想考H3CNE去哪报名？",
    "H3CNE考试报名流程是什么？",
    "请问H3CNE怎么报名啊？",

    # === 4. H3CNE报考条件相关（10种） ===
    "H3CNE报考条件是什么？",
    "考H3CNE需要什么条件？",
    "H3CNE报名有什么要求？",
    "什么人可以考H3CNE？",
    "报考H3CNE需要满足什么条件？",
    "零基础可以考H3CNE吗？",
    "考H3CNE有学历要求吗？",
    "H3CNE报考需要什么基础吗？",
    "想考H3CNE有什么限制条件吗？",
    "H3CNE的报名条件是什么？",

    # === 5. H3CNE成绩查询相关（10种） ===
    "H3CNE成绩怎么查询？",
    "H3CNE考试完怎么查分？",
    "怎么查询H3CNE的考试成绩？",
    "H3CNE成绩在哪里查？",
    "H3CNE考试成绩查询方式是什么？",
    "考完H3CNE多久可以查成绩？怎么查？",
    "怎么查我H3CNE的考试分数？",
    "H3CNE的成绩查询入口在哪？",
    "请问H3CNE成绩怎么查啊？",
    "H3CNE考试成绩怎么查询？",

    # === 6. H3CNE证书有效期相关（10种） ===
    "H3CNE证书有效期多久？",
    "H3CNE证书有效期是多长时间？",
    "H3CNE证书多久过期？",
    "H3CNE证书的有效期是几年？",
    "考下来的H3CNE证书能管多久？",
    "H3CNE证书有效期是3年吗？",
    "H3CNE证书多长时间失效？",
    "H3CNE证书的有效期限是多久？",
    "拿到H3CNE证书之后有效期多久？",
    "H3CNE证书会过期吗？有效期是多久？",

    # === 7. H3CNE培训相关（10种） ===
    "H3CNE需要培训吗？",
    "考H3CNE必须参加培训吗？",
    "考H3CNE一定要上课吗？",
    "不培训可以直接考H3CNE吗？",
    "H3CNE考试需要先参加培训吗？",
    "考H3CNE有没有强制培训要求？",
    "自学可以考H3CNE吗？还是必须培训？",
    "H3CNE报考必须要培训证明吗？",
    "想考H3CNE，必须先参加培训吗？",
    "考H3CNE可以不参加培训直接考吗？",

    # === 8. H3CNE学习内容相关（10种） ===
    "H3CNE学什么内容？",
    "H3CNE考试考什么内容？",
    "考H3CNE需要学哪些东西？",
    "H3CNE的考试内容有哪些？",
    "H3CNE主要学习什么？",
    "H3CNE考试范围是什么？",
    "备考H3CNE需要学哪些内容？",
    "H3CNE的课程内容有哪些？",
    "H3CNE都考哪些知识点？",
    "想考H3CNE，需要学习什么内容？",

    # === 9. H3CNE证书下载相关（10种） ===
    "H3CNE证书怎么下载？",
    "H3CNE证书在哪里下载？",
    "考完H3CNE怎么拿证书？",
    "H3CNE电子证书怎么下载？",
    "H3CNE证书下载入口在哪？",
    "怎么获取H3CNE的电子证书？",
    "H3CNE考试通过后怎么下载证书？",
    "H3CNE证书领取方式是什么？",
    "H3CNE证书可以自己下载吗？怎么弄？",
    "通过H3CNE考试后，怎么下载证书？",

    # === 10. H3CNE重认证相关（10种） ===
    "H3CNE重认证规则是什么？",
    "H3CNE证书到期了怎么办？",
    "H3CNE怎么重认证？",
    "H3CNE证书过期了怎么续期？",
    "H3CNE重认证要求是什么？",
    "H3CNE证书到期了需要重新考试吗？",
    "H3CNE怎么刷新证书有效期？",
    "H3CNE重认证流程是什么？",
    "H3CNE证书快过期了怎么续？",
    "H3CNE重认证需要满足什么条件？"
]

# 并发数（固定100并发同时请求）
CONCURRENCY = 100
# 测试轮次：1=只跑一遍所有问题，N=重复跑N轮（总请求数=100*N）
TEST_ROUNDS = 1
# 请求超时时间（秒，100并发建议设置60-120秒，给服务端足够排队时间）
REQUEST_TIMEOUT = 60

async def test_workflow_request(semaphore: asyncio.Semaphore, session: aiohttp.ClientSession, user_id: int, query: str) -> Dict:
    """单个异步请求测试"""
    async with semaphore:  # 信号量控制并发数，确保同时最多10个请求
        start_time = time.time()
        try:
            async with session.post(
                API_URL,
                headers=HEADERS,
                json={
                    "inputs": {"query": query},
                    "response_mode": "blocking",
                    "user": f"test-user-{user_id}"
                },
                timeout=aiohttp.ClientTimeout(total=REQUEST_TIMEOUT)  # 可配置超时时间
            ) as response:
                response.raise_for_status()
                await response.json()  # 读取响应内容
                elapsed = time.time() - start_time
                return {
                    "success": True,
                    "user_id": user_id,
                    "query": query,
                    "status_code": response.status,
                    "elapsed": round(elapsed * 1000, 2),  # 毫秒
                    "error": None
                }
        except Exception as e:
            elapsed = time.time() - start_time
            # 优化错误信息，显示具体异常类型
            error_msg = f"{type(e).__name__}: {str(e) if str(e) else '请求超时/服务端无响应'}"
            return {
                "success": False,
                "user_id": user_id,
                "query": query,
                "status_code": getattr(e, 'status', None),
                "elapsed": round(elapsed * 1000, 2),
                "error": error_msg
            }

async def run_concurrent_test():
    """运行异步并发测试"""
    total_requests = len(TEST_QUERIES) * TEST_ROUNDS
    print(f"🚀 开始异步并发测试，并发数：{CONCURRENCY}，总请求数：{total_requests}")
    print(f"ℹ️  将遍历所有{len(TEST_QUERIES)}个测试问题，重复{TEST_ROUNDS}轮，请求超时：{REQUEST_TIMEOUT}秒")
    print("=" * 80)

    start_time = time.time()

    # 准备测试任务
    semaphore = asyncio.Semaphore(CONCURRENCY)  # 控制并发数为10
    tasks = []
    user_id_counter = 0

    async with aiohttp.ClientSession() as session:
        # 遍历所有测试问题，每个问题跑TEST_ROUNDS次
        for _ in range(TEST_ROUNDS):  # _ 表示不需要用到轮次编号
            for query in TEST_QUERIES:
                user_id_counter += 1
                # 创建异步任务
                task = asyncio.create_task(
                    test_workflow_request(semaphore, session, user_id_counter, query)
                )
                tasks.append(task)

        # 等待所有任务完成，边完成边输出
        results = []
        for future in asyncio.as_completed(tasks):
            result = await future
            results.append(result)
            status = "✅" if result["success"] else "❌"
            print(f"{status} 用户{result['user_id']:2d} | {result['elapsed']:6}ms | {result['query']}")

    # 统计结果
    total_time = time.time() - start_time
    success_count = sum(1 for r in results if r["success"])
    fail_count = len(results) - success_count
    avg_response_time = sum(r["elapsed"] for r in results) / len(results)
    max_response_time = max(r["elapsed"] for r in results)
    min_response_time = min(r["elapsed"] for r in results)

    # 输出统计报告
    print("\n" + "=" * 80)
    print("📊 测试结果统计")
    print(f"总请求数: {len(results)}")
    print(f"成功请求: {success_count} ({success_count/len(results)*100:.2f}%)")
    print(f"失败请求: {fail_count} ({fail_count/len(results)*100:.2f}%)")
    print(f"总耗时: {total_time:.2f}s")
    print(f"平均响应时间: {avg_response_time:.2f}ms")
    print(f"最大响应时间: {max_response_time:.2f}ms")
    print(f"最小响应时间: {min_response_time:.2f}ms")
    print(f"吞吐量: {len(results)/total_time:.2f} 请求/秒")

    # 输出错误详情
    if fail_count > 0:
        print("\n❌ 错误详情：")
        for result in results:
            if not result["success"]:
                print(f"用户{result['user_id']} | {result['query']} | 错误: {result['error']}")

if __name__ == "__main__":
    # 先安装依赖：pip install aiohttp
    asyncio.run(run_concurrent_test())
