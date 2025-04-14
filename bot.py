import asyncio
import sys
import loguru
import random
import string
from curl_cffi.requests import AsyncSession
from eth_account.messages import encode_defunct
import json
import time
from web3 import AsyncWeb3

logger = loguru.logger
logger.remove()
logger.add(sys.stdout, colorize=True, format="<g>{time:HH:mm:ss:SSS}</g> | <level>{message}</level>")


def get_random_line_from_file():
    try:
        with open("question.txt", 'r') as file:
            lines = file.readlines()  # 读取所有行
            random_line = random.choice(lines)  # 随机选择一行
            return random_line.strip()  # 去掉行末的换行符
    except Exception as e:
        print(f"发生错误: {e}")
        return None
      

class Di:
    def __init__(self, token: str,proxy):
        defaulf_headers = {
            "Authorization": f"{token}",
        }
        self.client = AsyncSession(timeout=120, impersonate="chrome120",proxy=proxy,headers=defaulf_headers)
        self.token = token



    async def chat(self):
        try:
            for i in range(50):
                question=get_random_line_from_file()
                json_data = {
                    "query": question,
                    "stream": True,
                    "message": []
                }
                res = await self.client.post("https://api.dolphinx.ai/api/llm/base-chat", json=json_data)
                if res.status_code == 200:
                    result = await self.client.get("https://api.dolphinx.ai/api/llm/access-info")
                    bonus = result.json()['data']['bonus']
                    used_count = result.json()['data']['used_count']
                    id = result.json()['data']['id']
                    logger.success(f"用户id：【{id}】,消息【{question}】发送成功,分数：【{bonus}】,今日聊天：【{used_count}】次")
                    sleep_time = random.uniform(10, 15)
                    logger.success(f"休眠 {sleep_time:.2f} 秒")
                    if int(used_count) >= 50:
                        logger.success(f"【{self.token}】今日聊天已完成")
                        break
            return True    
        except Exception as e:
            logger.error(f"系统异常: {e}")
            return False



async def do(semaphore, token,proxy):
    async with semaphore:
        for _ in range(3):
            if await Di(token,proxy).chat():
                break

async def main(filePath, thread):
    semaphore = asyncio.Semaphore(int(thread))
    tasks = []
    with open(filePath, 'r') as f:
        for account_line in f:
            account_line = account_line.strip().split('----')
            tasks.append(do(semaphore, account_line[0].strip(),account_line[1].strip()))
    await asyncio.gather(*tasks)

if __name__ == '__main__':
    asyncio.run(main("token.txt", 4))
    
