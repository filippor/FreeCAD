#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


HEADER = "/tests:\n"


def parse_registered_tests(output: str) -> list[str]:
    tests: list[str] = []
    started = False

    for line in output.splitlines():
        if not started:
            if line.strip() == "Registered test units:":
                started = True
            continue

        stripped = line.strip()
        if not stripped:
            continue

        if stripped.startswith("Please choose one"):
            break
        if stripped.startswith("---"):
            break
        if stripped in {"OK", "System exit"}:
            break

        tests.append(stripped)

    return tests


def list_registered_tests(binary: str) -> list[str]:
    proc = subprocess.run(
        [binary, "-t"],
        input="0\n",
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    if proc.returncode not in (0, 1):
        raise RuntimeError(f"'{binary} -t' failed with exit code {proc.returncode}\n{proc.stdout}")

    tests = parse_registered_tests(proc.stdout)
    if not tests:
        raise RuntimeError(f"Could not parse registered tests from '{binary} -t' output\n{proc.stdout}")
    return tests


def render_gui_entry(test_name: str, binary: str) -> str:
    return f"    /{test_name:<22}:\n        test: wlheadless-run -- {binary}  -t  {test_name}\n"


def render_cmd_entry(test_name: str, binary: str) -> str:
    return f"  /{test_name:<22}:\n    test: {binary} -t  {test_name}\n"


def render_fmf_gui(tests: list[str], binary: str) -> str:
    return HEADER + "".join(render_gui_entry(test_name, binary) for test_name in tests)


def render_fmf_cmd(tests: list[str], binary: str) -> str:
    return HEADER + "".join(render_cmd_entry(test_name, binary) for test_name in tests)


def write_file(path: str, content: str) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")


def with_suffix(path: str, suffix: str) -> str:
    if not suffix:
        return path
    p = Path(path)
    return str(p.with_name(f"{p.stem}{suffix}{p.suffix}"))


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Generate package/fedora/tests/gui_tests.fmf and package/fedora/tests/cmd_tests.fmf "
            "from '<binary> -t' output."
        )
    )
    parser.add_argument(
        "--mode",
        choices=["both", "gui", "cmd"],
        default="both",
        help="Which outputs to generate (default: %(default)s)",
    )
    parser.add_argument("--gui-freecad", default="/usr/bin/FreeCAD", help="FreeCAD GUI executable")
    parser.add_argument(
        "--cmd-freecad",
        default="/usr/bin/FreeCADCmd",
        help="FreeCAD command-line executable",
    )
    parser.add_argument(
        "--gui-output",
        default="package/fedora/tests/gui_tests.fmf",
        help="Output GUI FMF file path",
    )
    parser.add_argument(
        "--cmd-output",
        default="package/fedora/tests/cmd_tests.fmf",
        help="Output CMD FMF file path",
    )
    parser.add_argument(
        "--suffix",
        default="",
        help="Optional suffix added before output extension (e.g. _1)",
    )
    args = parser.parse_args(argv)

    gui_output = with_suffix(args.gui_output, args.suffix)
    cmd_output = with_suffix(args.cmd_output, args.suffix)

    if args.mode in {"both", "gui"}:
        gui_tests = list_registered_tests(args.gui_freecad)
        gui_content = render_fmf_gui(gui_tests, args.gui_freecad)
        write_file(gui_output, gui_content)
        print(f"Wrote {gui_output} with {len(gui_tests)} tests")

    if args.mode in {"both", "cmd"}:
        cmd_tests = list_registered_tests(args.cmd_freecad)
        cmd_content = render_fmf_cmd(cmd_tests, args.cmd_freecad)
        write_file(cmd_output, cmd_content)
        print(f"Wrote {cmd_output} with {len(cmd_tests)} tests")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
