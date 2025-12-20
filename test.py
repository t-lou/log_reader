#!/usr/bin/env python3

"""Simple tests without pytest."""

from src.filter import Filter


def _precheck_assert():
    try:
        assert False
        print("assert not working")
    except:
        print("assert working")


def test_filter_plain():
    filter = Filter([{"reg": False, "keyword": "et"}], True)

    assert filter.match("et")
    assert filter.match("et1")
    assert filter.match("1et")
    assert not filter.match("te")
    assert not filter.match("sd")
    assert not filter.match("")


def test_filter_regex():
    filter = Filter([{"reg": True, "keyword": r"etc:\s*-?\d+(?:\.\d+)?(?!$)"}], True)

    assert filter.match("etc: 3.14")
    assert filter.match("prefix etc: 3.14")
    assert filter.match("etc: 3.14 suffix")
    assert filter.match("prefix etc: 3.14")
    assert filter.match("etc: 3.14,")
    assert filter.match("prefix etc: 42 end")
    assert filter.match("prefix etc: -0.5 end")
    assert not filter.match("prefix etc: end")
    assert not filter.match("prefix etc: ,")


def test_filter_all():
    filter = Filter(
        [{"reg": False, "keyword": "sand"}, {"reg": False, "keyword": "wich"}], True
    )

    assert filter.match("sandwich")
    assert filter.match("wichsand")
    assert filter.match("sand,wich")
    assert filter.match("wich,sand")
    assert filter.match("sandwichor")
    assert filter.match("andwichsand")
    assert not filter.match("sand*ich")
    assert not filter.match("sand")
    assert not filter.match("wich")


def test_filter_any():
    filter = Filter(
        [{"reg": False, "keyword": "sand"}, {"reg": False, "keyword": "wich"}], False
    )

    assert filter.match("sandwich")
    assert filter.match("wichsand")
    assert filter.match("sand,wich")
    assert filter.match("wich,sand")
    assert filter.match("sandwichor")
    assert filter.match("andwichsand")
    assert not filter.match("san**ich")
    assert filter.match("sand")
    assert filter.match("wich")
    assert filter.match("sandy")
    assert filter.match("swich")


if __name__ == "__main__":
    _precheck_assert()
    test_filter_plain()
    test_filter_regex()
    test_filter_all()
    test_filter_any()
