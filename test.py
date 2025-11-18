from tomd import tomd
print(
    tomd(
        "https://openai.com/index/gartner-2025-emerging-leader/",
        llm_enhance=False,
        use_browser=False,
    )
)
