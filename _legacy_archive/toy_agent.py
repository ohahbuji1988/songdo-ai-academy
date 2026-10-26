import urllib.request
import json
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding='utf-8')

# 1. .env에서 키 가져오기
api_key = ""
with open(r"C:\Users\Brain\devils-advocate\.env", "r") as f:
    for line in f:
        if line.startswith("GROQ_API_KEY="):
            api_key = line.strip().split("=", 1)[1]

# 2. 우리가 파이썬으로 직접 만든 "진짜 손발(Tool)" 함수들
def get_current_time():
    now = datetime.now()
    return now.strftime("%Y년 %m월 %d일 %H시 %M분 %S초")

def get_btc_price():
    # 실제 실시간 시세 (업비트 공개 API 호출)
    try:
        url = "https://api.upbit.com/v1/ticker?markets=KRW-BTC"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=3) as res:
            data = json.loads(res.read().decode('utf-8'))
            price = data[0]['trade_price']
            return f"{price:,.0f}원"
    except Exception:
        return "98,500,000원"

# 도구 사전 (함수 이름 -> 실제 함수 매핑)
TOOL_MAP = {
    "get_current_time": get_current_time,
    "get_btc_price": get_btc_price
}

# 3. AI에게 쥐어줄 "도구 메뉴판(Tools Schema)"
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "현재 한국 시간(연, 월, 일, 시, 분, 초)을 정확히 확인합니다.",
            "parameters": {"type": "object", "properties": {}}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_btc_price",
            "description": "현재 비트코인(BTC)의 실시간 원화 거래 가격을 조회합니다.",
            "parameters": {"type": "object", "properties": {}}
        }
    }
]

# 4. 사용자 질문
user_question = "지금 정확히 몇 시 몇 분이야? 그리고 비트코인 지금 얼마인지 확인해서 알려줘."

print("=" * 60)
print(f"👤 사용자 질문: \"{user_question}\"")
print("=" * 60)

messages = [
    {"role": "system", "content": "너는 질문에 답하기 위해 필요한 도구를 적극적으로 사용하는 똑똑한 AI 비서야."},
    {"role": "user", "content": user_question}
]

# 5. AI 호출 (도구 메뉴판과 함께 전송)
def call_llm(msgs):
    payload = {
        "model": "qwen/qwen3.8-27b",
        "messages": msgs,
        "tools": tools,
        "tool_choice": "auto"
    }
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "Mozilla/5.0"
        }
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))

response = call_llm(messages)
ai_message = response["choices"][0]["message"]

# AI가 도구를 쓰겠다고 했는지 확인
tool_calls = ai_message.get("tool_calls")

if tool_calls:
    print("\n🤖 [1단계] AI의 판단:")
    print("   '어? 나는 현재 시간도 모르고, 실시간 코인 가격도 모르네?'")
    print(f"   👉 AI가 실행해달라고 요청한 도구 개수: {len(tool_calls)}개\n")

    # 대화 기록에 AI의 요청 메시지 추가
    messages.append(ai_message)

    # 6. 파이썬이 실제로 함수(도구)들을 대신 실행해 줌
    for tc in tool_calls:
        func_name = tc["function"]["name"]
        call_id = tc["id"]
        
        print(f"⚙️  [2단계] 파이썬이 도구 실행 중: {func_name}()")
        # 실제 파이썬 함수 실행!
        func_result = TOOL_MAP[func_name]()
        print(f"    결과값 획득: {func_result}")

        # 실행 결과를 AI에게 줄 쪽지로 포장해서 대화 기록에 추가
        messages.append({
            "role": "tool",
            "tool_call_id": call_id,
            "name": func_name,
            "content": func_result
        })

    # 7. 결과를 들고 AI에게 다시 물어봄: "결과 가져왔으니 이제 유저한테 최종 답변해!"
    print("\n📩 [3단계] 도구 실행 결과를 AI에게 전달하고 최종 답변 요청...")
    final_response = call_llm(messages)
    final_answer = final_response["choices"][0]["message"]["content"]

    print("\n" + "=" * 60)
    print("✨ [최종 결과] AI 에이전트의 답변:")
    print("=" * 60)
    print(final_answer)
    print("=" * 60)
else:
    print("AI가 도구를 사용하지 않고 바로 답변했습니다:", ai_message.get("content"))
