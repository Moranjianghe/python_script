#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速短随机 ID 生成工具（适合文件名后缀 / 临时标识）。
支持模式：random / ts / tsmilli / b36 / seq
"""

import argparse
import secrets
import string
import time
import sys
import os
from pathlib import Path

DEFAULT_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
NO_AMBIG_ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz"
SEQ_FILE = Path(os.getenv("LOCALAPPDATA", ".")) / "rid_seq.txt"


def base36(n: int) -> str:
    if n == 0:
        return "0"
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    s = []
    neg = n < 0
    n = abs(n)
    while n:
        n, r = divmod(n, 36)
        s.append(chars[r])
    if neg:
        s.append("-")
    return "".join(reversed(s))


def load_and_increment_seq() -> int:
    """
    简单持久计数（单机 + 非并发场景 OK）。
    并发高 / 频繁多进程不建议用这个方式（需要锁）。
    """
    try:
        if SEQ_FILE.exists():
            val = int(SEQ_FILE.read_text(encoding="utf-8").strip() or "0")
        else:
            val = 0
    except Exception:
        val = 0
    val += 1
    try:
        SEQ_FILE.write_text(str(val), encoding="utf-8")
    except Exception:
        pass
    return val


def get_random_chars(length: int, alphabet: str) -> str:
    # 用 secrets.choice 生成（每次调用均匀）；也可以随机字节取模，但这里更直观。
    return "".join(secrets.choice(alphabet) for _ in range(length))


def build_id(mode: str, length: int, alphabet: str, sep: str) -> str:
    prefix = ""
    if mode == "random":
        pass
    elif mode == "ts":
        prefix = str(int(time.time()))
    elif mode == "tsmilli":
        prefix = str(int(time.time() * 1000))
    elif mode == "b36":
        prefix = base36(int(time.time() * 1000))
    elif mode == "seq":
        prefix = str(load_and_increment_seq())
    else:
        raise ValueError("未知模式: " + mode)

    rand_part = get_random_chars(length, alphabet)
    if prefix:
        return prefix + (sep if sep else "") + rand_part
    return rand_part


def copy_clipboard(text: str):
    """
    尝试用多种方式复制到剪贴板：
    1. pyperclip (若已安装)
    2. Windows 原生命令 clip
    3. ctypes 调用（兜底简单版）
    """
    # 1. pyperclip
    try:
        import pyperclip  # type: ignore
        pyperclip.copy(text)
        return True
    except Exception:
        pass

    # 2. clip 命令
    try:
        import subprocess
        p = subprocess.Popen("clip", universal_newlines=True, stdin=subprocess.PIPE)
        p.communicate(text)
        if p.returncode == 0:
            return True
    except Exception:
        pass

    # 3. ctypes（仅简单 Unicode 写入）
    try:
        import ctypes
        from ctypes import wintypes

        CF_UNICODETEXT = 13
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        user32.OpenClipboard(0)
        user32.EmptyClipboard()
        # 分配全局内存
        data = text + "\0"
        h_global_mem = kernel32.GlobalAlloc(0x0002, (len(data) * 2))
        lp = kernel32.GlobalLock(h_global_mem)
        ctypes.memmove(lp, data.encode("utf-16le"), len(data) * 2)
        kernel32.GlobalUnlock(h_global_mem)
        user32.SetClipboardData(CF_UNICODETEXT, h_global_mem)
        user32.CloseClipboard()
        return True
    except Exception:
        pass

    return False


def notify(text: str):
    """
    Windows toast（可选），需要 pip install win10toast。
    """
    try:
        from win10toast import ToastNotifier  # type: ignore
        ToastNotifier().show_toast("RID 生成", text, duration=2, threaded=True)
    except Exception:
        # 静默失败即可
        pass


def parse_args():
    p = argparse.ArgumentParser(
        description="生成短随机 ID（默认 10 位），自动复制到剪贴板。",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("-l", "--length", type=int, default=10, help="随机部分长度（不含前缀）")
    p.add_argument(
        "-m",
        "--mode",
        choices=["random", "ts", "tsmilli", "b36", "seq"],
        default="random",
        help="生成模式",
    )
    p.add_argument(
        "-a",
        "--alphabet",
        type=str,
        help="自定义字符集（提供后将覆盖默认/去歧义设置）",
    )
    p.add_argument(
        "--omit-ambiguous",
        action="store_true",
        help="移除易混字符（0 O o 1 l I 等）",
    )
    p.add_argument("--upper", action="store_true", help="转为大写")
    p.add_argument("--lower", action="store_true", help="转为小写")
    p.add_argument("--sep", type=str, default="", help="前缀与随机部分分隔符")
    p.add_argument("--no-clip", action="store_true", help="不复制到剪贴板")
    p.add_argument("--notify", action="store_true", help="尝试弹出系统通知")
    p.add_argument("--quiet", action="store_true", help="不打印 ID（用于隐藏运行）")
    return p.parse_args()


def main():
    args = parse_args()

    if args.length < 1:
        print("长度必须 >= 1", file=sys.stderr)
        sys.exit(1)

    if args.alphabet:
        # 去重保持顺序
        seen = set()
        alphabet = "".join(c for c in args.alphabet if not (c in seen or seen.add(c)))
        if len(alphabet) < 2:
            print("字符集至少需要 2 个不同字符", file=sys.stderr)
            sys.exit(1)
    else:
        if args.omit_ambiguous:
            alphabet = NO_AMBIG_ALPHABET
        else:
            alphabet = DEFAULT_ALPHABET

    rid = build_id(args.mode, args.length, alphabet, args.sep)

    if args.upper and args.lower:
        # 若都给，优先 upper
        rid = rid.upper()
    elif args.upper:
        rid = rid.upper()
    elif args.lower:
        rid = rid.lower()

    if not args.no_clip:
        copied = copy_clipboard(rid)
        if not copied:
            print("[警告] 未能复制到剪贴板（缺少 clip 或权限问题）", file=sys.stderr)
            
    
    if not args.quiet:
        print(rid)

    if args.notify:
        notify(rid)


if __name__ == "__main__":
    main()