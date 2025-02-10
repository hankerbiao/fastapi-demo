API_URL = "https://api.siliconflow.cn/v1/chat/completions"
SYSTEM_PROMPT = """请你扮演一个高级文章摘要生成器。阅读我提供的文章后,请完成以下任务:

1. 生成文章摘要，50字左右
1. 提供1-2个相关的文章标签
2. 判断文章是否与金融或地产或其他金融数字相关，文章中涉及到金融数据相关，请写入摘要中。

请将结果以JSON格式输出,包含以下字段:
- summary: 文章摘要
- tags: 文章标签(数组格式)
- isFinanceOrEstate: 是否与金融/地产相关(布尔值)

下面是需要你分析的文章内容:"""
# ywm sk-kajcwwvoohfljguchcvillbbeyxybznpctbzkbfbyhfrhkks
# lb  sk-yissallpbndtfuunpjfkhljogxbvaaxkogrvsjjmvxrxhynd
# py  sk-jgigjkpbritnlxqwdblpbqmwifiwjtubqceoegpfxcwvwmat
# author_code = "sk-kajcwwvoohfljguchcvillbbeyxybznpctbzkbfbyhfrhkks"
author_code = "sk-yissallpbndtfuunpjfkhljogxbvaaxkogrvsjjmvxrxhynd"
# author_code = "sk-jgigjkpbritnlxqwdblpbqmwifiwjtubqceoegpfxcwvwmat"
HEADERS = {
    "Authorization": f"Bearer {author_code}",
    "Content-Type": "application/json"
}

PAYLOAD = {
    # "model": "deepseek-ai/DeepSeek-V3",
    "model": "Qwen/Qwen2.5-32B-Instruct",
    "messages": [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        }
    ],
    "stream": False,
    "max_tokens": 512,
    "stop": ["null"],
    "temperature": 0.7,
    "top_p": 0.7,
    "top_k": 50,
    "frequency_penalty": 0.5,
    "n": 1,
    "response_format": {"type": "text"},
    "tools": [
        {
            "type": "function",
            "function": {
                "description": "<string>",
                "name": "<string>",
                "parameters": {},
                "strict": False
            }
        }
    ]
}
