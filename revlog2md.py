#!/usr/bin/env python3
"""
revlog2md.py

Parse an ad-hoc, ascending-order "revision history" block (as commonly found
embedded in a version.h / header comment, or as a plain text file) and emit
a reversed-order, CHANGELOG.md-compatible Markdown file.

Designed to be reused across many similar-but-not-identical input files.
Most of the format is now auto-detected per line/per file, so in the common
case you just run:

    python3 revlog2md.py version.h

-----------------------------------------------------------------------------
INPUT ASSUMPTIONS
-----------------------------------------------------------------------------
- Entries appear in ASCENDING version order (oldest first).
- Each entry begins with a line whose first token is the version number,
  optionally prefixed with "V"/"v" (e.g. "6.11" or "V6.11" -- either is
  fine, and the two styles can even be mixed within one file).
- Immediately after the version, a date MAY be present. It is auto-detected
  per entry (see AUTO-DETECTED DATE below) -- some entries can have one and
  others not, in the same file.
- An entry may span multiple physical lines; continuation lines belong to
  the most recently started entry (they do NOT repeat the version number).
- Continuation lines (and sometimes the first line of an entry) may begin
  with a leading "-" to mark a distinct bullet point. This is optional;
  lines without it are still treated as their own message line.
- Lines that are not part of an entry (banner lines of repeated punctuation
  such as "====" or "****", blank lines, column-header lines, and -- for
  code-comment input -- any line that isn't a comment line at all, such as
  "#define VerNum ...") are discarded.

-----------------------------------------------------------------------------
AUTO-DETECTED INPUT FORMAT (used to be --format)
-----------------------------------------------------------------------------
The input file's extension picks the comment style automatically:
    .c .cpp .cxx .h .hpp  -> lines must start with "//" (others discarded)
    anything else         -> every line is a candidate, nothing stripped
Override with --format {cpp,text} or --comment-prefix if a file doesn't
follow this convention (e.g. a .h file that actually uses "#" comments).

-----------------------------------------------------------------------------
AUTO-DETECTED DATE (used to be --dates/--no-dates)
-----------------------------------------------------------------------------
After the version number, the next token is checked against a date pattern
(default: MM/DD/YY or MM/DD/YYYY, e.g. "3/11/24" or "03/11/2024"). If it
matches, it's consumed as the date and normalized to YYYY-MM-DD; if not,
that token is just the start of the message and the date field is left
blank. This is decided independently for every entry, so a file can freely
mix dated and undated versions.
Override the pattern with --date-regex if your dates use a different shape.

Other knobs (--version-regex, --date-informats) are exposed so future input
files with different version/date shapes don't require code changes.

-----------------------------------------------------------------------------
OUTPUT
-----------------------------------------------------------------------------
Standard Keep-a-Changelog-ish Markdown:

    # Changelog

    ## [6.11] - 2024-01-01
    - Include wbigcalc.ini in distribution, to provide register-value examples

    ## [6.10] -
    - Update help file to discuss script files
    ...

Entries are emitted newest-first (i.e. the input order is reversed), while
all lines belonging to a single entry stay together and in their original
relative order.

Output defaults to cltemp.md -- a scratch/staging file, since the
expectation is you maintain the real CHANGELOG.md by hand (with your own
preamble text etc.) and copy-paste the freshly generated entries in from
here.
"""

import argparse
import re
import sys
from pathlib import Path
from datetime import datetime


DEFAULT_VERSION_REGEX = r"[Vv]?\d+(?:\.\d+)+"
# MM/DD/YY or MM/DD/YYYY, e.g. "3/11/24", "03/11/2024"
DEFAULT_DATE_REGEX = r"\d{1,2}/\d{1,2}/(?:\d{4}|\d{2})"
DEFAULT_DATE_INFORMATS = [
    "%m/%d/%Y",
    "%m/%d/%y",
    "%Y-%m-%d",
    "%Y/%m/%d",
    "%d-%m-%Y",
    "%d/%m/%Y",
    "%B %d, %Y",
    "%b %d, %Y",
    "%b %d %Y",
]

# Extensions treated as code-comment files (comment-prefixed lines only).
CODE_EXTENSIONS = {".c", ".cpp", ".cxx", ".h", ".hpp"}

# A line consisting solely of repeated punctuation/whitespace, e.g.
# "*******" or "=======" or "-------" -- treated as decorative, not content.
BANNER_RE = re.compile(r"^[\*=_\-~#]{3,}\s*$")

# Leading bullet marker on a message line, e.g. "- Added foo"
BULLET_RE = re.compile(r"^-\s*")


class Entry:
    __slots__ = ("version", "date", "messages")

    def __init__(self, version, date=""):
        self.version = version
        self.date = date
        self.messages = []  # list[str]

    def add(self, content):
        content = content.strip()
        if not content:
            return

        # A leading "-" always starts a new bullet. No leading "-" means
        # this line is a word-wrapped continuation of the previous bullet
        # (unless there is no previous bullet yet, e.g. an entry whose
        # very first line has no dash at all).
        has_bullet = bool(BULLET_RE.match(content))
        text = BULLET_RE.sub("", content).strip()
        if not text:
            return

        if has_bullet or not self.messages:
            self.messages.append(text)
        else:
            self.messages[-1] = f"{self.messages[-1]} {text}"


def build_entry_regex(version_regex):
    # Captures the version, then everything after it as one blob; date vs.
    # message within that blob is decided separately per entry (some
    # entries have a date, some don't).
    return re.compile(rf"^(?P<version>{version_regex})\s+(?P<rest>.*\S)\s*$")


def build_date_lead_regex(date_regex):
    return re.compile(rf"^(?P<date>{date_regex})\s+(?P<message>.*\S)\s*$")


def normalize_date(raw_date, informats):
    raw_date = raw_date.strip()
    if not raw_date:
        return ""
    for fmt in informats:
        try:
            return datetime.strptime(raw_date, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    # Couldn't parse with any known format -- keep the raw text rather than
    # silently dropping it, but warn so the user can add a --date-informats
    # entry for their format.
    print(
        f"warning: could not parse date {raw_date!r} with known formats; "
        "leaving as-is (consider adding --date-informats)",
        file=sys.stderr,
    )
    return raw_date


def strip_version_prefix(version):
    # Normalize "V6.11"/"v6.11"/"6.11" all down to "6.11" for consistent
    # output, even when a single file mixes styles.
    return version[1:] if version and version[0] in "Vv" else version


def parse_entries(lines, comment_prefix, entry_re, date_lead_re, informats):
    entries = []
    current = None
    started = False

    for raw_line in lines:
        line = raw_line.rstrip("\r\n")

        if comment_prefix:
            if not line.startswith(comment_prefix):
                # Not a comment line at all (code, blank line outside the
                # block, etc.) -- always peripheral, discard unconditionally.
                continue
            rest = line[len(comment_prefix):]
        else:
            rest = line

        content = rest.strip()

        if not content:
            continue  # blank line
        if BANNER_RE.match(content):
            continue  # decorative banner line

        m = entry_re.match(content)
        if m:
            if current is not None:
                entries.append(current)

            version = strip_version_prefix(m.group("version"))
            remainder = m.group("rest")

            dm = date_lead_re.match(remainder)
            if dm:
                date = normalize_date(dm.group("date"), informats)
                message = dm.group("message")
            else:
                date = ""
                message = remainder

            current = Entry(version=version, date=date)
            current.add(message)
            started = True
        else:
            if started and current is not None:
                # Continuation line belonging to the most recent entry.
                current.add(content)
            # else: header/description text appearing before the first
            # real entry -- peripheral, discard.

    if current is not None:
        entries.append(current)

    return entries


def render_markdown(entries, title):
    out = [f"# {title}", ""]
    for entry in entries:
        out.append(f"## [{entry.version}] - {entry.date}")
        for msg in entry.messages:
            out.append(f"- {msg}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Reverse an ascending-order revision-history block into "
        "a CHANGELOG.md-compatible file, preserving multi-line entries.",
    )
    ap.add_argument("input", help="path to the input file")
    ap.add_argument(
        "-o",
        "--output",
        default="cltemp.md",
        help="output .md path (default: %(default)s) -- a scratch file meant "
        "to be copy-pasted into your hand-maintained CHANGELOG.md, not "
        "written to it directly",
    )
    ap.add_argument(
        "--format",
        choices=["auto", "cpp", "text"],
        default="auto",
        help="input line style: 'auto' (default) picks 'cpp' for "
        f"{sorted(CODE_EXTENSIONS)} files and 'text' otherwise. "
        "'cpp' = comment-prefixed lines only, 'text' = every line is a "
        "candidate, nothing stripped",
    )
    ap.add_argument(
        "--comment-prefix",
        default=None,
        help="override the comment marker to strip/require "
        "(default: '//' for cpp-style input, '' for text)",
    )
    ap.add_argument(
        "--version-regex",
        default=DEFAULT_VERSION_REGEX,
        help="regex matching a version token, incl. optional V/v prefix "
        "(default: %(default)r)",
    )
    ap.add_argument(
        "--date-regex",
        default=DEFAULT_DATE_REGEX,
        help="regex matching a date token; checked per-entry right after "
        "the version to decide if a date is present at all "
        "(default: MM/DD/YY[YY], %(default)r)",
    )
    ap.add_argument(
        "--date-informats",
        default=None,
        help="comma-separated strptime formats to try, in order, when "
        "normalizing dates to YYYY-MM-DD (default: a built-in common set)",
    )
    ap.add_argument(
        "--title",
        default="Changelog",
        help="H1 title for the generated Markdown (default: %(default)r)",
    )

    args = ap.parse_args(argv)

    fmt = args.format
    if fmt == "auto":
        fmt = "cpp" if Path(args.input).suffix.lower() in CODE_EXTENSIONS else "text"

    comment_prefix = args.comment_prefix
    if comment_prefix is None:
        comment_prefix = "//" if fmt == "cpp" else ""

    informats = (
        [f.strip() for f in args.date_informats.split(",")]
        if args.date_informats
        else DEFAULT_DATE_INFORMATS
    )

    entry_re = build_entry_regex(args.version_regex)
    date_lead_re = build_date_lead_regex(args.date_regex)

    with open(args.input, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()

    entries = parse_entries(lines, comment_prefix, entry_re, date_lead_re, informats)

    if not entries:
        print("warning: no entries were parsed -- check your options", file=sys.stderr)

    entries.reverse()

    markdown = render_markdown(entries, args.title)

    with open(args.output, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"Wrote {len(entries)} entries to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
