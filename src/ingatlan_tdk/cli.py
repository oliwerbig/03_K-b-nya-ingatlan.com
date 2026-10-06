# -*- coding: utf-8 -*-
"""ingatlan_tdk.cli — konzolos belépési pontok.

  python -m ingatlan_tdk build|report|verify|check [opciók]
  tdk-build / tdk-report / tdk-verify / tdk-check   (pip install -e . után)
"""
import sys


def verify_main() -> int:
    from .verify import main

    return main()


def check_main() -> int:
    from .checks import main

    return main()


def report_main() -> int:
    from .report_cli import main

    main()
    return 0


def build_main() -> int:
    """Teljes csővezeték: verify -> report -> verify (a CONTRIBUTING.md szerint)."""
    a = sys.argv[1:]
    skip = "--skip-verify" in a
    a = [x for x in a if x != "--skip-verify"]

    area = None
    if "--area" in a:
        i = a.index("--area")
        if i + 1 < len(a):
            area = a[i + 1]

    if not skip:
        rc = verify_main()
        if rc:
            return rc

    sys.argv = [sys.argv[0]] + (["--area", area] if area else ["--all"])
    rc = report_main()
    if rc:
        return rc

    if not skip:
        return verify_main()
    return 0


_CMDS = {
    "build": build_main,
    "report": report_main,
    "verify": verify_main,
    "check": check_main,
}


def main() -> int:
    a = sys.argv[1:]
    if not a or a[0] in ("-h", "--help"):
        print("Használat: python -m ingatlan_tdk {build|report|verify|check} [opciók]")
        return 0 if a else 2
    cmd, rest = a[0], a[1:]
    fn = _CMDS.get(cmd)
    if fn is None:
        print(f"Ismeretlen parancs: {cmd} (build|report|verify|check)")
        return 2
    sys.argv = [sys.argv[0]] + rest
    return fn() or 0


if __name__ == "__main__":
    sys.exit(main())