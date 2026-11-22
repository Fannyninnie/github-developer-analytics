from validate_raw import compare_counts


def test_compare_counts_finds_nothing_when_equal():
    assert compare_counts({"commits": 10}, {"commits": 10}) == []


def test_compare_counts_reports_each_difference():
    problems = compare_counts({"commits": 10, "issues": 5}, {"commits": 8, "issues": 5})
    assert problems == [("commits", 10, 8)]