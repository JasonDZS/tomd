from tomd import tomd
print(
    tomd(
        "https://arxiv.org/pdf/2511.14777",
        llm_enhance=False,
        use_browser=False,
    )
)
