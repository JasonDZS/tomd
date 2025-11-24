from tomd import tomd
print(
    tomd(
        "https://papers.nips.cc/paper_files/paper/2024/file/000f947dcaff8fbffcc3f53a1314f358-Paper-Conference.pdf",
        llm_enhance=False,
        use_browser=False,
    )
)
