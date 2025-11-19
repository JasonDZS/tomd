from tomd import tomd
print(
    tomd(
        "https://cognition.ai/blog/devin-annual-performance-review-2025/",
        llm_enhance=False,
        use_browser=False,
    )
)
