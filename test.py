#!/usr/bin/env python3
"""
Simple tests without pytest.
Run with:  python test_all.py
"""

from src.filter import Filter
from src.utils import make_name_filename

# -------------------------
# Utility
# -------------------------


def _precheck_assert():
    try:
        assert False
        print("assert NOT working (unexpected)")
    except AssertionError:
        print("assert working")


def _run(test_fn):
    """Run a test function and print a friendly message."""
    name = test_fn.__name__
    try:
        test_fn()
        print(f"[  OK  ] {name}")
    except AssertionError as e:
        print(f"[FAILED] {name}: {e}")
        raise
    except Exception as e:
        print(f"[ERROR ] {name}: unexpected exception {e}")
        raise


# -------------------------
# Tests
# -------------------------


def test_filter_plain():
    f = Filter([{"reg": False, "keyword": "et"}], True)

    assert f.match("et")
    assert f.match("et1")
    assert f.match("1et")
    assert not f.match("te")
    assert not f.match("sd")
    assert not f.match("")


def test_filter_regex():
    f = Filter([{"reg": True, "keyword": r"etc:\s*-?\d+(?:\.\d+)?(?!$)"}], True)

    assert f.match("etc: 3.14")
    assert f.match("prefix etc: 3.14")
    assert f.match("etc: 3.14 suffix")
    assert f.match("etc: 3.14,")
    assert f.match("prefix etc: 42 end")
    assert f.match("prefix etc: -0.5 end")
    assert not f.match("prefix etc: end")
    assert not f.match("prefix etc: ,")


def test_filter_all():
    f = Filter(
        [
            {"reg": False, "keyword": "sand"},
            {"reg": False, "keyword": "wich"},
        ],
        True,
    )

    assert f.match("sandwich")
    assert f.match("wichsand")
    assert f.match("sand,wich")
    assert f.match("wich,sand")
    assert f.match("sandwichor")
    assert f.match("andwichsand")
    assert not f.match("sand*ich")
    assert not f.match("sand")
    assert not f.match("wich")


def test_filter_any():
    f = Filter(
        [
            {"reg": False, "keyword": "sand"},
            {"reg": False, "keyword": "wich"},
        ],
        False,
    )

    assert f.match("sandwich")
    assert f.match("wichsand")
    assert f.match("sand,wich")
    assert f.match("wich,sand")
    assert f.match("sandwichor")
    assert f.match("andwichsand")
    assert not f.match("san**ich")
    assert f.match("sand")
    assert f.match("wich")
    assert f.match("sandy")
    assert f.match("swich")


def test_name_conversion():
    test_data = {
        "ab": "ab",
        "a b": "a_b",
        "a&b": "a_and_b",
        "a|b": "a_or_b",
        "a:b": "ab",
        "a/b": "ab",
        "a\\b": "ab",
        "a?b": "ab",
        "a<b": "ab",
        "a>b": "ab",
        "a*b": "ab",
    }

    for name, expected in test_data.items():
        result = make_name_filename(name)
        assert result == expected, f"'{name}' -> '{result}', expected '{expected}'"


# -------------------------
# Main
# -------------------------

if __name__ == "__main__":
    _precheck_assert()

    tests = [
        test_filter_plain,
        test_filter_regex,
        test_filter_all,
        test_filter_any,
        test_name_conversion,
    ]

    for t in tests:
        _run(t)

    print("\nAll tests passed.")
