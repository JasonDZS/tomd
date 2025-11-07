from tomd import tomd
print(
    tomd(
        "https://aws.amazon.com/cn/blogs/china/agentive-ai-infrastructure-practice-series-1/",
        llm_enhance=False,
        language="Chinese",
        # use_browser=True,
        # content_selector="div.blog-content",
    )
)
