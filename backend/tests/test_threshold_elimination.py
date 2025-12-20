"""Test script for threshold elimination logic (Story 4-4)."""

import sys
sys.path.insert(0, '.')

from services.ranking_service import (
    apply_thresholds,
    get_elimination_summary,
    process_threshold_elimination
)

# Mock candidates for testing
MOCK_CANDIDATES = [
    {'id': 'c1', 'name': 'Alice High', 'email': 'alice@example.com'},
    {'id': 'c2', 'name': 'Bob Medium', 'email': 'bob@example.com'},
    {'id': 'c3', 'name': 'Carol Low', 'email': 'carol@example.com'},
    {'id': 'c4', 'name': 'Dave VeryLow', 'email': 'dave@example.com'},
]

# Mock scores
MOCK_SCORES = {
    'c1': {'experience': 85, 'skills': 90, 'projects': 80, 'positions': 75, 'education': 70},
    'c2': {'experience': 65, 'skills': 60, 'projects': 55, 'positions': 50, 'education': 60},
    'c3': {'experience': 45, 'skills': 50, 'projects': 40, 'positions': 35, 'education': 55},
    'c4': {'experience': 30, 'skills': 35, 'projects': 25, 'positions': 20, 'education': 40},
}


def test_no_thresholds():
    """Test with no thresholds enabled - should return all candidates."""
    print("\n=== Test 1: No thresholds enabled ===")

    thresholds = {}
    remaining, eliminated = apply_thresholds(MOCK_CANDIDATES.copy(), thresholds, MOCK_SCORES)

    assert len(remaining) == 4, f"Expected 4 remaining, got {len(remaining)}"
    assert len(eliminated) == 0, f"Expected 0 eliminated, got {len(eliminated)}"

    print(f"✓ All {len(remaining)} candidates passed (no thresholds)")


def test_single_threshold():
    """Test with single threshold eliminating some."""
    print("\n=== Test 2: Single threshold (experience >= 60) ===")

    thresholds = {
        'experience': {'enabled': True, 'minimum': 60}
    }
    remaining, eliminated = apply_thresholds(MOCK_CANDIDATES.copy(), thresholds, MOCK_SCORES)

    assert len(remaining) == 2, f"Expected 2 remaining, got {len(remaining)}"
    assert len(eliminated) == 2, f"Expected 2 eliminated, got {len(eliminated)}"

    remaining_names = [c['name'] for c in remaining]
    print(f"✓ Remaining: {remaining_names}")

    eliminated_names = [e['name'] for e in eliminated]
    print(f"✓ Eliminated: {eliminated_names}")

    # Check elimination reasons
    for e in eliminated:
        assert 'Experience score' in e['reason'], f"Bad reason format: {e['reason']}"
        print(f"  - {e['name']}: {e['reason']}")


def test_multiple_thresholds():
    """Test with multiple thresholds."""
    print("\n=== Test 3: Multiple thresholds (experience >= 40, skills >= 55) ===")

    thresholds = {
        'experience': {'enabled': True, 'minimum': 40},
        'skills': {'enabled': True, 'minimum': 55}
    }
    remaining, eliminated = apply_thresholds(MOCK_CANDIDATES.copy(), thresholds, MOCK_SCORES)

    # c1 (85, 90) passes both
    # c2 (65, 60) passes both
    # c3 (45, 50) fails skills (50 < 55)
    # c4 (30, 35) fails experience (30 < 40)

    assert len(remaining) == 2, f"Expected 2 remaining, got {len(remaining)}"
    assert len(eliminated) == 2, f"Expected 2 eliminated, got {len(eliminated)}"

    print(f"✓ Remaining: {[c['name'] for c in remaining]}")
    for e in eliminated:
        print(f"  - {e['name']}: {e['reason']}")


def test_elimination_summary():
    """Test elimination summary generation."""
    print("\n=== Test 4: Elimination summary ===")

    eliminated = [
        {'id': 'c3', 'name': 'Carol', 'reason': 'Experience score 45% < minimum 60%'},
        {'id': 'c4', 'name': 'Dave', 'reason': 'Experience score 30% < minimum 60%'},
        {'id': 'c5', 'name': 'Eve', 'reason': 'Skills score 40% < minimum 50%'},
    ]

    summary = get_elimination_summary(eliminated)

    assert summary['count'] == 3, f"Expected count 3, got {summary['count']}"
    assert 'experience' in summary['breakdown'], "Missing experience in breakdown"
    assert summary['breakdown']['experience'] == 2, f"Expected 2 for experience"
    assert summary['breakdown']['skills'] == 1, f"Expected 1 for skills"

    print(f"✓ Count: {summary['count']}")
    print(f"✓ Breakdown: {summary['breakdown']}")


def test_empty_elimination():
    """Test elimination summary with empty list."""
    print("\n=== Test 5: Empty elimination summary ===")

    summary = get_elimination_summary([])

    assert summary['count'] == 0
    assert summary['breakdown'] == {}
    assert summary['candidates'] == []

    print("✓ Empty summary returned correctly")


def test_disabled_thresholds():
    """Test that disabled thresholds are ignored."""
    print("\n=== Test 6: Disabled thresholds ignored ===")

    thresholds = {
        'experience': {'enabled': False, 'minimum': 100},  # Would eliminate all if enabled
        'skills': {'enabled': True, 'minimum': 40}
    }
    remaining, eliminated = apply_thresholds(MOCK_CANDIDATES.copy(), thresholds, MOCK_SCORES)

    # Only c4 should be eliminated (skills 35 < 40)
    assert len(eliminated) == 1, f"Expected 1 eliminated, got {len(eliminated)}"
    assert eliminated[0]['name'] == 'Dave VeryLow'

    print(f"✓ Only 1 eliminated (disabled threshold ignored)")
    print(f"  - {eliminated[0]['name']}: {eliminated[0]['reason']}")


def test_scores_attached():
    """Test that scores are attached to remaining candidates."""
    print("\n=== Test 7: Scores attached to remaining ===")

    candidates = MOCK_CANDIDATES.copy()
    thresholds = {'experience': {'enabled': True, 'minimum': 50}}
    remaining, _ = apply_thresholds(candidates, thresholds, MOCK_SCORES)

    for c in remaining:
        assert '_scores' in c, f"Missing _scores for {c['name']}"
        print(f"✓ {c['name']}: _scores = {c['_scores']}")


if __name__ == '__main__':
    print("Testing Threshold Elimination Logic (Story 4-4)")
    print("=" * 50)

    test_no_thresholds()
    test_single_threshold()
    test_multiple_thresholds()
    test_elimination_summary()
    test_empty_elimination()
    test_disabled_thresholds()
    test_scores_attached()

    print("\n" + "=" * 50)
    print("✓ All tests passed!")
