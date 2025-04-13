import google.generativeai as genai
genai.configure(api_key="AIzaSyCmcPvXPFyQea9RHzvt1pBXXW2zd_0ZkkI")

for m in genai.list_models():
    print(m.name, "→ 支援 content:", "generateContent" in m.supported_generation_methods)
