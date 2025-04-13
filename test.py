import openai
import os
from dotenv import load_dotenv
load_dotenv()
# 設置 Azure OpenAI 的 API 端點和密鑰
azure_endpoint =  os.getenv("AZURE_OPENAI_ENDPOINT")
api_key = os.getenv("AZURE_OPENAI_KEY")
api_version = "2025-01-01-preview"
deployment_name =  os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")  # 確保這是「部署名稱」，而非「模型名稱」

print("AZURE_OPENAI_API_KEY:", os.getenv("AZURE_OPENAI_KEY"))  # 應該顯示 API Key
print("AZURE_OPENAI_ENDPOINT:", os.getenv("AZURE_OPENAI_ENDPOINT"))  # 應該顯示 Azure 端點
print("AZURE_OPENAI_DEPLOYMENT_NAME:", os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"))  # 應該顯示 Azure 端點

# 建立 OpenAI 客戶端 (新版 API)
client = openai.AzureOpenAI(
    api_key=api_key,
    api_version=api_version,
    azure_endpoint=azure_endpoint
)

# 用戶輸入
user_input = input("You：").strip()

# 呼叫 Azure OpenAI API
try:
    response = client.chat.completions.create(
        model=deployment_name,  # 這裡應該使用「部署名稱」
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "請用繁體中文回覆"},
            {"role": "user", "content": user_input}
        ],
        temperature=0,  # 越高，回答越有創造性
        max_tokens=500,  # 控制回答長度
        top_p=0.95,  # 調整與控制AI模型輸出的隨機性
        frequency_penalty=0,  # 調控特定詞彙出現頻率
        presence_penalty=0  # 調控引入新概念的傾向性
    )
    
    # 取得 AI 回應
    response_text = response.choices[0].message.content

    # 顯示回應
    print("AI：" + response_text)

except openai.OpenAIError as e:
    print("❌ 測試失敗！錯誤訊息：")
    print(e)
