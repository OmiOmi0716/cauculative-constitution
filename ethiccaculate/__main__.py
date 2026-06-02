"""
CLI entry point for ethiccaculate.

Usage:
  ethiccaculate                        run the default demo
  ethiccaculate demo                   run the full demo (single + multi + six-axis)
  ethiccaculate formula                print the ethics formula reference
  ethiccaculate formula --demo         print reference + run demo pipeline
  ethiccaculate text "<text>"          quick ethics audit on text
  ethiccaculate text "<t>" --json      output audit result as JSON
  ethiccaculate batch "<t1>" "<t2>"    run quick audit on multiple texts
"""

from __future__ import annotations

import json
import sys


def _cmd_demo() -> None:
    from .demo import main as demo_main
    demo_main()


def _cmd_formula(show_demo: bool) -> None:
    from .formula import get_formula_reference, demo_pipeline
    print(get_formula_reference())
    if show_demo:
        result = demo_pipeline()
        print("\nDEMO PIPELINE (balanced BCG profile)")
        print(result.format_card())


def _cmd_text(text: str, as_json: bool) -> None:
    from .text_ethics import quick_ethics_audit
    report = quick_ethics_audit(text)
    if as_json:
        print(json.dumps(report.to_dict(), indent=2))
    else:
        print(report.format_report())


def _cmd_batch(texts: list[str], as_json: bool) -> None:
    from .text_ethics import batch_audit_texts
    reports = batch_audit_texts(texts)
    if as_json:
        print(json.dumps([r.to_dict() for r in reports], indent=2))
    else:
        for i, report in enumerate(reports, start=1):
            print(f"\n[{i}/{len(reports)}]")
            print(report.format_report())


def _print_usage() -> None:
    print(__doc__)


def main(argv: list[str] | None = None) -> None:
    args = list(argv if argv is not None else sys.argv[1:])

    if not args or args[0] == "demo":
        _cmd_demo()
        return

    cmd = args[0]

    if cmd == "formula":
        show_demo = "--demo" in args
        _cmd_formula(show_demo)
        return

    if cmd == "text":
        rest = [a for a in args[1:] if not a.startswith("--")]
        as_json = "--json" in args
        if not rest:
            print("Usage: ethiccaculate text \"<text>\" [--json]", file=sys.stderr)
            sys.exit(1)
        _cmd_text(" ".join(rest), as_json)
        return

    if cmd == "batch":
        rest = [a for a in args[1:] if not a.startswith("--")]
        as_json = "--json" in args
        if not rest:
            print("Usage: ethiccaculate batch \"<text1>\" \"<text2>\" ... [--json]", file=sys.stderr)
            sys.exit(1)
        _cmd_batch(rest, as_json)
        return

    if cmd in ("-h", "--help", "help"):
        _print_usage()
        return

    print(f"Unknown command: {cmd!r}", file=sys.stderr)
    _print_usage()
    sys.exit(1)


if __name__ == "__main__":
    main()
