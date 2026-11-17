#!/usr/bin/env python3
"""TrollStore 静态标识去特征化 (套餐 A - 保守)

把所有可被扫描识别的静态标识一致替换为中性身份。
只改"静态标识层"，不触碰签名密码学层 (Exploits/ 下的伪造 Apple CA、
AppStoreCodeDirectory 里的 icraze/T8ALTGMVXN 正版伪装身份) 与 host 工具。

用法:
  python apply_stealth_identity.py           # 应用替换
  python apply_stealth_identity.py --check   # 只检查残留，不修改

想换成你自己的身份: 修改下方 ID_* 变量后重新运行即可。
"""
import os
import sys

# ---------------------------------------------------------------------------
# 可配置身份 (改成你自己的即可，全仓库会保持一致)
# ---------------------------------------------------------------------------
DEV_PREFIX = "com.axiomdev"          # bundle id 域名前缀
APP_NAME = "AxiomBox"                # 主 App 名 (大小写敏感，用于 CFBundleIdentifier)
APP_NAME_LOW = "axiombox"            # 小写形式 (用于包名 / UTType / 文件名)
HELPER_NAME = "AxiomBoxHelper"       # 持久化 helper app 名

# ---------------------------------------------------------------------------
# 替换映射: key -> value。脚本按 key 长度降序执行，避免子串互相覆盖。
# ---------------------------------------------------------------------------
MAPPING = {
    # --- bundle id / 包名 (长的在前，避免短 id 抢占) ---
    "com.opa334.trollstorepersistencehelper": f"{DEV_PREFIX}.{APP_NAME_LOW}.helper",
    "com.opa334.trollstoreroothelper":        f"{DEV_PREFIX}.{APP_NAME_LOW}.roothelper",
    "com.opa334.trollstorehelper":            f"{DEV_PREFIX}.{APP_NAME_LOW}.helperalt",
    "com.opa334.TrollStoreLite":              f"{DEV_PREFIX}.{APP_NAME}Lite",
    "com.opa334.trollstorelite":              f"{DEV_PREFIX}.{APP_NAME_LOW}lite",
    "com.opa334.trollstore.tipa":             f"{DEV_PREFIX}.{APP_NAME_LOW}.pkg",
    "com.opa334.TrollStore":                  f"{DEV_PREFIX}.{APP_NAME}",
    "com.opa334.trollstore":                  f"{DEV_PREFIX}.{APP_NAME_LOW}",

    # --- 标记文件 / helper 名 / 路径 ---
    ".TrollStorePersistenceHelper": f".{HELPER_NAME}",
    "_TrollStoreLite":              f"_{APP_NAME}Lite",
    "TrollStorePersistenceHelper":  HELPER_NAME,
    "trollstorehelper_lite":        f"{APP_NAME_LOW}helper_lite",
    "trollstorehelper":             f"{APP_NAME_LOW}helper",
    "TrollStoreLite":               f"{APP_NAME}Lite",
    "TrollHelper":                  f"{APP_NAME_LOW[:1].upper() + APP_NAME_LOW[1:]}Helper",
    "TrollStore":                   APP_NAME,
    "Trollstore Lite":              f"{APP_NAME} Lite",
    "Trollstore":                   APP_NAME,

    # --- 会编译进二进制的明文字符串常量 ---
    "_TROLLSTORE_BACKUP": f"_{APP_NAME_LOW.upper()}_BACKUP",

    # --- 兜底 (作者名 / 小写路径 / mime / 变量名 / URL) ---
    "opa334":     DEV_PREFIX.split(".")[-1],
    "trollstore": APP_NAME_LOW,
}

SKIP_DIRS = {".git", "Exploits", "Pwnify", "Victim", "_build", ".theos"}
EXTS = (".m", ".h", ".c", ".plist", "Makefile", "control")

# 源码目录名必须保持原样:它们是磁盘上的真实文件夹,改了会导致 make -C 找不到目录。
# 替换前先把这些路径片段替换成哨兵,替换后再还原。
DIR_TOKENS = [
    "./TrollStoreLite", "../TrollStoreLite", "./TrollStore/", "../TrollStore/",
    "./TrollHelper", "../TrollHelper", "./TrollStore", "../TrollStore",
    "TrollStore/Resources", "TrollHelper/Resources", "TrollStoreLite/Resources",
    "../TrollStore/*.m", "../TrollHelper/*.m",
]
SENTINEL = "\x00DIR{}\x00"


def protect_dirs(text):
    for i, tok in enumerate(DIR_TOKENS):
        text = text.replace(tok, SENTINEL.format(i))
    return text


def restore_dirs(text):
    for i, tok in enumerate(DIR_TOKENS):
        text = text.replace(SENTINEL.format(i), tok)
    return text


def target_files():
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        base = os.path.basename(root)
        for name in files:
            if name in ("Makefile", "control") or name.endswith(EXTS):
                yield os.path.join(root, name)


def apply():
    ordered = sorted(MAPPING.items(), key=lambda kv: len(kv[0]), reverse=True)
    total = 0
    for path in target_files():
        with open(path, "r", encoding="utf-8", errors="surrogateescape") as f:
            text = f.read()
        new = protect_dirs(text)
        n = 0
        for old, repl in ordered:
            c = new.count(old)
            if c:
                new = new.replace(old, repl)
                n += c
        new = restore_dirs(new)
        if n:
            with open(path, "w", encoding="utf-8", errors="surrogateescape") as f:
                f.write(new)
            print(f"{n:4d}  {path}")
            total += n
    print(f"\n共替换 {total} 处。")


def check():
    leftovers = []
    for path in target_files():
        with open(path, "r", encoding="utf-8", errors="surrogateescape") as f:
            for i, line in enumerate(f, 1):
                low = line.lower()
                if "opa334" in low or "trollstore" in low or "trollhelper" in low:
                    leftovers.append(f"{path}:{i}: {line.rstrip()}")
    if leftovers:
        print("发现残留 (需人工确认是否为签名层/注释):")
        print("\n".join(leftovers))
    else:
        print("OK: 静态标识层无残留。")


if __name__ == "__main__":
    if "--check" in sys.argv:
        check()
    else:
        apply()
        print("\n--- 复查 ---")
        check()
