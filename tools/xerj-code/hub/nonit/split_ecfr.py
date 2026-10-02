#!/usr/bin/env python3
"""split_ecfr.py — eCFR bulk title XML → per-section text files (hub mirror repos).

GPO ships each eCFR title as ONE multi-MB XML; title 26's part 1 alone is 58 MB
of text. That is the ecma262 single-giant-file failure shape (G2: the unit a
query retrieves must be clause-level), so this splits a title into one file per
DIV8 section (§) or appendix, with a breadcrumb header for context:

    Title 29 CFR — Part 1910 (Occupational Safety and Health Standards)
    ## § 1910.28 Duty to have fall protection ...

Parts with no DIV8 sections (reserved ranges etc.) fall back to a single
per-part file. Long parts split across several DIV5s reusing the same N
("(CONTINUED)") merge into the same directory.

Usage: split_ecfr.py <title-number.xml> <outdir>
Output: <outdir>/parts/part-<N>/sec-<id>.txt + <outdir>/PROVENANCE.txt
"""
import pathlib
import re
import sys
import xml.etree.ElementTree as ET

SKIP_TAGS = {"CFRTOC", "GRAPHIC", "FP", "PRTPAGE", "BIB", "AMDDATE"}


def clean(s):
    return " ".join((s or "").split())


def flatten(div, out):
    for el in div:
        tag = el.tag.split("}")[-1]
        if tag in SKIP_TAGS:
            continue
        if tag.startswith("DIV"):
            head = el.find("HEAD")
            if head is not None and clean(head.text):
                out.append("\n## " + clean(head.text) + "\n")
            flatten(el, out)
        else:
            txt = clean(" ".join(el.itertext()))
            if txt:
                out.append(txt + "\n")


def slug(n):
    s = n.replace("§", "").strip()
    s = re.sub(r"\s+", "", s)
    return re.sub(r"[/\\]", "-", s) or "unnumbered"


def main(src, outdir):
    outdir = pathlib.Path(outdir)
    parts_dir = outdir / "parts"
    parts_dir.mkdir(parents=True, exist_ok=True)
    title_no = re.search(r"(\d+)", src.split("/")[-1].split(".")[0]).group(1)
    amd_date, stack = "", []
    stats = {"sections": 0, "parts": set(), "part_only": 0}
    for event, el in ET.iterparse(src, events=("start", "end")):
        tag = el.tag.split("}")[-1]
        if event == "start":
            stack.append(el)
            if tag == "AMDDATE" and not amd_date:
                amd_date = clean(el.text)
            continue
        stack.pop()
        if tag == "DIV5":
            num = el.get("N", "unk")
            pdir = parts_dir / f"part-{slug(num)}"
            pdir.mkdir(exist_ok=True)
            stats["parts"].add(num)
            # part preamble: direct HEAD/AUTH/SOURCE children
            pre = []
            head = el.find("HEAD")
            if head is not None and clean(head.text):
                pre.append(clean(head.text))
            for el2 in el:
                if el2.tag.split("}")[-1] in ("AUTH", "SOURCE"):
                    pre.append(clean(" ".join(el2.itertext())))
            if not any(pdir.glob("sec-*.txt")) and not any(pdir.glob("_all.txt")):
                if pre:
                    (pdir / "_part.txt").write_text("\n".join(pre) + "\n")
                if not any(True for _ in el.iter("DIV8")):
                    out = list(pre) + [""]
                    flatten(el, out)
                    (pdir / "_all.txt").write_text("\n".join(out).strip() + "\n")
                    stats["part_only"] += 1
        elif tag == "DIV8":
            # nearest DIV5/DIV6 ancestors give the breadcrumb
            part_head = sub_head = ""
            for anc in reversed(stack):
                atag = anc.tag.split("}")[-1]
                if atag == "DIV5" and not part_head:
                    h = anc.find("HEAD")
                    part_head = clean(h.text) if h is not None else ""
                elif atag in ("DIV6", "DIV7") and not sub_head:
                    h = anc.find("HEAD")
                    sub_head = clean(h.text) if h is not None else ""
            num = el.get("N", "?")
            pdir = None
            for anc in reversed(stack):
                if anc.tag.split("}")[-1] == "DIV5":
                    pdir = parts_dir / f"part-{slug(anc.get('N', 'unk'))}"
                    break
            pdir = pdir or parts_dir
            pdir.mkdir(exist_ok=True)
            head = el.find("HEAD")
            ph = part_head or ""
            ph = ph[5:] if ph.upper().startswith("PART ") else ph
            out = [f"Title {title_no} CFR — Part {ph}".rstrip() if ph else f"Title {title_no} CFR"]
            if sub_head:
                out.append(sub_head)
            if head is not None and clean(head.text):
                out.append("## " + clean(head.text))
            out.append("")
            flatten(el, out)
            f = pdir / f"sec-{slug(num)}.txt"
            if f.exists():  # same section id twice in one part: merge
                f.write_text(f.read_text() + "\n" + "\n".join(out).strip() + "\n")
            else:
                f.write_text("\n".join(out).strip() + "\n")
            stats["sections"] += 1
        if tag == "DIV8" or tag == "DIV5":
            el.clear()
    (outdir / "PROVENANCE.txt").write_text(
        f"source: https://www.govinfo.gov/bulkdata/ECFR/title-{title_no}/ECFR-title{title_no}.xml\n"
        f"AMDDATE in source XML: {amd_date}\n"
        f"parts: {len(stats['parts'])}; section files: {stats['sections']}; "
        f"section-less parts written whole: {stats['part_only']}\n"
    )
    print(f"{src}: {len(stats['parts'])} parts, {stats['sections']} sections, "
          f"{stats['part_only']} part-only, AMDDATE {amd_date!r}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
