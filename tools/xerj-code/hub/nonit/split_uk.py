#!/usr/bin/env python3
"""split_uk.py — legislation.gov.uk CLML act XML → per-section text files.

One file per parliamentary section (P1) and per Schedule, with a breadcrumb
header (act — PART — CHAPTER — cross-heading) for retrieval context. The
data.xml feed we split IS the current revised version (RestrictStartDate pins
the version date), which is the whole point: current-law lookup.

Usage: split_uk.py <year> <chapter> <xml-file> <outdir>
Output: <outdir>/acts/<year>-<c>/s<N>.txt | sched-<N>.txt | _act.txt
"""
import pathlib
import sys
import xml.etree.ElementTree as ET

NS_DC = "{http://purl.org/dc/elements/1.1/}"
NS = "{http://www.legislation.gov.uk/namespaces/legislation}"
NS_META = "{http://www.legislation.gov.uk/namespaces/metadata}"

# text-bearing blocks, in document order; everything else is structure
TEXT_TAGS = {"Text", "Title", "Number", "Pnumber", "Heading", "TitleBlock", "Xheading"}


def clean(s):
    return " ".join((s or "").split())


def flatten(el, out, pend, top=False):
    tag = el.tag.split("}")[-1]
    if tag == "Pnumber":
        if top:
            return  # section/schedule number is already the filename
        t = clean(" ".join(el.itertext()))
        if t:
            pend[0] = t  # prefixes the next text block: "(2) ..."
        return
    if tag in TEXT_TAGS:
        t = clean(" ".join(el.itertext()))
        if t:
            if pend[0]:
                out.append(f"({pend[0]}) {t}\n")
                pend[0] = None
            else:
                out.append(t + "\n")
        return
    if tag in ("CommentaryRef", "Ref", "Marker", "Note", "Fnote", "Signature"):
        return
    for child in el:
        flatten(child, out, pend)


def main(year, chap, src, outroot):
    outdir = pathlib.Path(outroot) / "acts" / f"{year}-{chap}"
    outdir.mkdir(parents=True, exist_ok=True)
    tree = ET.parse(src)
    root = tree.getroot()
    title = ""
    meta = root.find(f"{NS_META}Metadata")
    if meta is not None:
        e = meta.find(f"{NS_DC}title")
        title = clean(e.text) if e is not None and e.text else ""
    version = root.get("RestrictStartDate", "")
    body = root.find(f"{NS}Primary/{NS}Body")
    act_line = f"{title or 'ukpga ' + year + ' c' + chap} (current as at {version})"
    n_sec = n_sched = 0
    part = chapter = group = ""
    if body is not None:
        for el in body.iter():
            tag = el.tag.split("}")[-1]
            if tag == "Part":
                num = el.find(f"{NS}Number")
                ttl = el.find(f"{NS}Title")
                part = (clean(" ".join(num.itertext())) + " — " +
                        clean(" ".join(ttl.itertext()) if ttl is not None else "")) if num is not None else ""
            elif tag == "Chapter":
                num = el.find(f"{NS}Number")
                ttl = el.find(f"{NS}Title")
                if num is not None and ttl is not None:
                    chapter = clean(" ".join(num.itertext())) + " — " + clean(" ".join(ttl.itertext()))
                elif num is not None:
                    chapter = clean(" ".join(num.itertext()))
            elif tag == "P1group":
                ttl = el.find(f"{NS}Title")
                group = clean(" ".join(ttl.itertext())) if ttl is not None else ""
            elif tag == "P1":
                num = el.find(f"{NS}Pnumber")
                sn = clean(" ".join(num.itertext())) if num is not None else ""
                out = [act_line]
                for crumb in (part, chapter, group):
                    if crumb:
                        out.append(crumb)
                out.append("")
                flatten(el, out, [None], top=True)
                f = outdir / f"s{sn or n_sec}.txt"
                f.write_text("\n".join(out).strip() + "\n")
                n_sec += 1
    scheds = root.find(f"{NS}Primary/{NS}Schedules")
    if scheds is not None:
        for i, sch in enumerate(scheds.findall(f"{NS}Schedule"), 1):
            num = sch.find(f"{NS}Pnumber")
            ttl = sch.find(f"{NS}Title")
            name = clean(" ".join(num.itertext())) if num is not None else ""
            head = clean(" ".join(ttl.itertext())) if ttl is not None else ""
            out = [act_line]
            if part:
                out.append(part)
            out.append(f"SCHEDULE {name} — {head}".rstrip(" —"))
            out.append("")
            flatten(sch, out, [None], top=True)
            (outdir / f"sched-{name or i}.txt").write_text("\n".join(out).strip() + "\n")
            n_sched += 1
    (outdir / "_act.txt").write_text(
        f"{act_line}\n{NS and ''}source: https://www.legislation.gov.uk/ukpga/{year}/{chap}/data.xml\n"
        f"sections: {n_sec}; schedules: {n_sched}\n")
    print(f"{year} c{chap}: {title[:50]!r} — {n_sec} sections, {n_sched} schedules")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
