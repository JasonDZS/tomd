from tomd import tomd
print(
    tomd(
        "https://openai.com/index/chatgpt-for-veterans/",
        llm_enhance=True,
        language="Chinese",
        # use_browser=True,
        # content_selector="div.blog-content",
    )
)
