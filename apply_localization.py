#!/usr/bin/env python3
"""
AxiomBox (TrollStore) Chinese localization generator.

Approach is based on the community-proven project sbwml/TrollStore_zh_Hans:
wrap hardcoded UI string literals in NSLocalizedString(@"...", nil) and ship
en / zh-Hans / zh-Hant Localizable.strings bundles.

This variant is adapted for the already-rebranded sources (TrollStore ->
AxiomBox, trollstorehelper -> axiomboxhelper, opa334 -> axiomdev): translation
keys are looked up both verbatim and after mapping the rebrand back to the
original upstream wording.

Properties:
  - Idempotent: re-running never double-wraps strings.
  - Skips Exploits/ (signature layer), Pwnify/, Victim/, .git, build dirs.
  - Does NOT touch filesystem paths, bundle IDs, notification names, URL
    schemes, reuse identifiers or dictionary keys (only known UI strings are
    wrapped, driven by translations.json).
  - Revert with: git checkout -- TrollStore TrollHelper Shared TrollStoreLite

Usage:
  python apply_localization.py            # apply + generate .strings
  python apply_localization.py --dry-run  # preview only
"""

import os
import sys
import json
import plistlib

ROOT = os.path.dirname(os.path.abspath(__file__))
TRANS_PATH = os.path.join(ROOT, "localization", "translations.json")

# Source dirs whose UI code we localize
SRC_DIRS = ["TrollStore", "TrollHelper", "Shared", "TrollStoreLite"]
# Never touch these (signature / certificate layer and vendored code)
SKIP_DIRS = {"Exploits", "Pwnify", "Victim", "_build", ".theos", ".git", "localization"}
# Files where a matching string is a logic identifier, not display text.
# TrollHelper/main.m compares @"Default Configuration" against a scene config
# name returned by the system; localizing it would break the comparison.
SKIP_FILES = {"TrollHelper/main.m"}
SRC_EXTS = (".m", ".h")

# Rebrand map: current (modified) token -> upstream original token.
# Used to find a translation for a rebranded key in the upstream table.
REBRAND_TO_UPSTREAM = [
    ("AxiomBoxHelper", "TrollStore Persistence Helper"),
    ("AxiomboxHelper", "TrollStore Persistence Helper"),
    ("axiomboxhelper", "trollstorehelper"),
    ("AxiomBox", "TrollStore"),
    ("axiomdev", "opa334"),
]

# Language tags and their index in each translation value pair [hans, hant]
LANGS = {"en": None, "zh-Hans": 0, "zh-Hant": 1}


def load_translations():
    with open(TRANS_PATH, encoding="utf-8") as f:
        return json.load(f)  # {upstream_english_key: [hans, hant]}


def build_key_maps(trans):
    """
    Build lookup: every concrete key currently in source -> its upstream key.
    We generate the rebranded variants of each upstream key so we can match
    strings like 'Updating AxiomBox' back to 'Updating TrollStore'.
    """
    # upstream key -> variant (current source) key
    up_to_cur = {}
    for up in trans:
        cur = up
        # apply in a fixed order; longest/full forms first
        cur = cur.replace("TrollStore Persistence Helper", "AxiomBoxHelper")
        cur = cur.replace("trollstorehelper", "axiomboxhelper")
        cur = cur.replace("TrollStore", "AxiomBox")
        cur = cur.replace("opa334", "axiomdev")
        # Some places use "Trollstore Lite" upstream; nothing to do here.
        up_to_cur[up] = cur

    # current key -> upstream key (reverse). If a current key maps from several
    # upstream keys, keep the first (deterministic: sorted upstream).
    cur_to_up = {}
    for up in sorted(up_to_cur):
        cur = up_to_cur[up]
        cur_to_up.setdefault(cur, up)
    return up_to_cur, cur_to_up


def iter_source_files():
    for d in SRC_DIRS:
        base = os.path.join(ROOT, d)
        for dirpath, dirnames, filenames in os.walk(base):
            dirnames[:] = [x for x in dirnames if x not in SKIP_DIRS]
            for fn in filenames:
                if fn.endswith(SRC_EXTS):
                    full = os.path.join(dirpath, fn)
                    rel = os.path.relpath(full, ROOT).replace("\\", "/")
                    if rel in SKIP_FILES:
                        continue
                    yield full


def c_escape(s):
    """Escape a string for use inside an ObjC @"..." literal."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def wrap_source(text, cur_to_up, stats):
    """
    Replace @"<key>" with NSLocalizedString(@"<key>", nil) for keys that are
    known UI strings. Skip if already wrapped. Process longest keys first so
    substrings don't interfere.
    """
    keys = sorted(cur_to_up, key=len, reverse=True)
    out = text
    for key in keys:
        esc = c_escape(key)
        literal = '@"' + esc + '"'
        wrapped = 'NSLocalizedString(@"' + esc + '", nil)'
        # Skip literals already inside NSLocalizedString(...)
        start = 0
        while True:
            idx = out.find(literal, start)
            if idx < 0:
                break
            # Detect if already wrapped: look back for NSLocalizedString(
            prefix = out[max(0, idx - len("NSLocalizedString(")):idx]
            if prefix.endswith("NSLocalizedString("):
                start = idx + len(literal)
                continue
            out = out[:idx] + wrapped + out[idx + len(literal):]
            stats["wrapped"] += 1
            start = idx + len(wrapped)
    return out


def localize_brand(text):
    """Keep translated brand names consistent with the rebranded app."""
    for old, new in [
        ("TrollStore Persistence Helper", "AxiomBox 持久化助手"),
        ("TrollStore", "AxiomBox"),
        ("trollstorehelper", "axiomboxhelper"),
        ("TrollHelper", "AxiomBoxHelper"),
        ("opa334", "axiomdev"),
    ]:
        text = text.replace(old, new)
    return text


# A few long strings were untranslated upstream; supply Chinese ourselves.
EXTRA_TRANSLATIONS = {
    "zh-Hans": {
        "Alfie": "Alfie",
        "AxiomBox %@\n\n© 2022-2026 Lars Fröder (axiomdev)\n\nAxiomBox is NOT for piracy!\n\nCredits:\nGoogle TAG, @alfiecg_dev: CoreTrust bug\n@lunotech11, @SerenaKit, @tylinux, @TheRealClarity, @dhinakg, @khanhduytran0: Various contributions\n@ProcursusTeam: uicache, ldid\n@cstar_ow: uicache\n@saurik: ldid":
            "AxiomBox %@\n\n© 2022-2026 Lars Fröder (axiomdev)\n\nAxiomBox 拒绝盗版应用行为！\n\n鸣谢:\nGoogle TAG, @alfiecg_dev: CoreTrust bug\n@lunotech11, @SerenaKit, @tylinux, @TheRealClarity, @dhinakg, @khanhduytran0: Various contributions\n@ProcursusTeam: uicache, ldid\n@cstar_ow: uicache\n@saurik: ldid",
    },
    "zh-Hant": {
        "Alfie": "Alfie",
        "AxiomBox %@\n\n© 2022-2026 Lars Fröder (axiomdev)\n\nAxiomBox is NOT for piracy!\n\nCredits:\nGoogle TAG, @alfiecg_dev: CoreTrust bug\n@lunotech11, @SerenaKit, @tylinux, @TheRealClarity, @dhinakg, @khanhduytran0: Various contributions\n@ProcursusTeam: uicache, ldid\n@cstar_ow: uicache\n@saurik: ldid":
            "AxiomBox %@\n\n© 2022-2026 Lars Fröder (axiomdev)\n\nAxiomBox 拒絕盜版應用程式行為！\n\n鳴謝:\nGoogle TAG, @alfiecg_dev: CoreTrust bug\n@lunotech11, @SerenaKit, @tylinux, @TheRealClarity, @dhinakg, @khanhduytran0: Various contributions\n@ProcursusTeam: uicache, ldid\n@cstar_ow: uicache\n@saurik: ldid",
    },
}


def write_strings(lang, trans, up_to_cur, target_dirs):
    """Generate a binary plist .strings file mapping current keys -> translation."""
    table = {}
    for up, vals in trans.items():
        key = up_to_cur[up]  # current source key
        if lang == "en":
            value = key  # English base = the (rebranded) source text
        else:
            value = vals[LANGS[lang]]
            # Adapt brand wording to the rebranded app; translate any string
            # that upstream left in English but that we have a key for.
            if value == up:
                value = EXTRA_TRANSLATIONS.get(lang, {}).get(key, key)
            else:
                value = localize_brand(value)
        table[key] = value

    data = plistlib.dumps(table, fmt=plistlib.FMT_BINARY, sort_keys=True)
    for res in target_dirs:
        lproj = os.path.join(res, lang + ".lproj")
        os.makedirs(lproj, exist_ok=True)
        path = os.path.join(lproj, "Localizable.strings")
        with open(path, "wb") as f:
            f.write(data)
        print(f"  wrote {os.path.relpath(path, ROOT)} ({len(table)} entries)")


def main():
    dry = "--dry-run" in sys.argv
    trans = load_translations()
    up_to_cur, cur_to_up = build_key_maps(trans)
    print(f"Loaded {len(trans)} translations; {len(cur_to_up)} distinct source keys.")

    stats = {"wrapped": 0, "files": 0}
    for path in iter_source_files():
        with open(path, encoding="utf-8", errors="surrogateescape") as f:
            text = f.read()
        new = wrap_source(text, cur_to_up, stats)
        if new != text:
            stats["files"] += 1
            if not dry:
                with open(path, "w", encoding="utf-8", errors="surrogateescape") as f:
                    f.write(new)
            print(f"  {'[dry] ' if dry else ''}localized {os.path.relpath(path, ROOT)}")

    print(f"\nWrapped {stats['wrapped']} literals across {stats['files']} files.")

    target_dirs = [
        os.path.join(ROOT, "TrollStore", "Resources"),
        os.path.join(ROOT, "TrollStoreLite", "Resources"),
    ]
    if not dry:
        print("\nGenerating .strings bundles:")
        for lang in LANGS:
            write_strings(lang, trans, up_to_cur, target_dirs)

        print("\nDeclaring CFBundleLocalizations in Info.plist:")
        for res in target_dirs:
            plist = os.path.join(res, "Info.plist")
            declare_localizations(plist)
    else:
        print("\n[dry-run] no .strings written.")


def declare_localizations(plist_path):
    """Add CFBundleLocalizations / CFBundleDevelopmentRegion (idempotent)."""
    with open(plist_path, encoding="utf-8") as f:
        text = f.read()
    if "CFBundleLocalizations" in text:
        print(f"  already declared: {os.path.relpath(plist_path, ROOT)}")
        return
    block = """\t<key>CFBundleDevelopmentRegion</key>
\t<string>en</string>
\t<key>CFBundleLocalizations</key>
\t<array>
\t\t<string>en</string>
\t\t<string>zh-Hans</string>
\t\t<string>zh-Hant</string>
\t</array>
"""
    idx = text.rfind("</dict>")
    if idx < 0:
        print(f"  WARNING: no </dict> in {plist_path}")
        return
    new = text[:idx] + block + text[idx:]
    with open(plist_path, "w", encoding="utf-8") as f:
        f.write(new)
    print(f"  declared: {os.path.relpath(plist_path, ROOT)}")


if __name__ == "__main__":
    main()
