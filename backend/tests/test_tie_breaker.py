"""Test script for tie-breaker logic (Story 4-6)."""

import sys
sys.path.insert(0, '.')

from services.ranking_service import (
    detect_tie_breaker_candidates,
    apply_tie_breaker_flags,
    get_tie_breaker_summary
)


def test_detect_tie_breaker_candidates():
    """Test detection of candidates with close scores."""
    print("\n=== Test 1: Detect tie-breaker candidates ===")

    # Case 1: Two candidates within 5%
    rankings = [
        {'candidate_id': 'a', 'match_score': 85},
        {'candidate_id': 'b', 'match_score': 83},  # Within 5% of 'a'
        {'candidate_id': 'c', 'match_score': 70},  # Not within 5% of 'b'
    ]
    tie_ids = detect_tie_breaker_candidates(rankings)

    assert 'a' in tie_ids, "Candidate 'a' should be in tie-breaker"
    assert 'b' in tie_ids, "Candidate 'b' should be in tie-breaker"
    assert 'c' not in tie_ids, "Candidate 'c' should NOT be in tie-breaker"
    print(f"✓ Basic detection: {tie_ids}")

    # Case 2: Chain of close scores
    rankings = [
        {'candidate_id': 'a', 'match_score': 90},
        {'candidate_id': 'b', 'match_score': 88},  # Within 5% of 'a'
        {'candidate_id': 'c', 'match_score': 85},  # Within 5% of 'b'
        {'candidate_id': 'd', 'match_score': 70},  # Not within 5% of 'c'
    ]
    tie_ids = detect_tie_breaker_candidates(rankings)

    assert 'a' in tie_ids
    assert 'b' in tie_ids
    assert 'c' in tie_ids
    assert 'd' not in tie_ids
    print(f"✓ Chain detection: {tie_ids}")

    # Case 3: No tie-breakers (all far apart)
    rankings = [
        {'candidate_id': 'a', 'match_score': 90},
        {'candidate_id': 'b', 'match_score': 80},
        {'candidate_id': 'c', 'match_score': 70},
    ]
    tie_ids = detect_tie_breaker_candidates(rankings)

    assert len(tie_ids) == 0
    print("✓ No tie-breakers when scores far apart")

    # Case 4: All within 5%
    rankings = [
        {'candidate_id': 'a', 'match_score': 85},
        {'candidate_id': 'b', 'match_score': 84},
        {'candidate_id': 'c', 'match_score': 82},
    ]
    tie_ids = detect_tie_breaker_candidates(rankings)

    assert len(tie_ids) == 3
    print(f"✓ All in tie-breaker when close: {tie_ids}")

    # Case 5: Exact same score
    rankings = [
        {'candidate_id': 'a', 'match_score': 85},
        {'candidate_id': 'b', 'match_score': 85},
    ]
    tie_ids = detect_tie_breaker_candidates(rankings)

    assert 'a' in tie_ids
    assert 'b' in tie_ids
    print("✓ Exact same scores detected")

    # Case 6: Empty list
    tie_ids = detect_tie_breaker_candidates([])
    assert len(tie_ids) == 0
    print("✓ Empty list handled")

    # Case 7: Single candidate
    tie_ids = detect_tie_breaker_candidates([{'candidate_id': 'a', 'match_score': 90}])
    assert len(tie_ids) == 0
    print("✓ Single candidate handled")


def test_apply_tie_breaker_flags():
    """Test applying tie-breaker flags."""
    print("\n=== Test 2: Apply tie-breaker flags ===")

    rankings = [
        {'candidate_id': 'a', 'match_score': 85, 'scores': {'experience': 90, 'skills': 80}},
        {'candidate_id': 'b', 'match_score': 83, 'scores': {'experience': 75, 'skills': 85}},
        {'candidate_id': 'c', 'match_score': 70, 'scores': {'experience': 60, 'skills': 70}},
    ]

    # With CRITICAL experience
    priorities = {'experience': 'CRITICAL', 'skills': 'IMPORTANT'}
    result = apply_tie_breaker_flags(rankings, priorities)

    # a and b should have tie-breaker
    assert result[0]['tie_breaker_applied'] == True
    assert result[1]['tie_breaker_applied'] == True
    assert result[2]['tie_breaker_applied'] == False

    # a should have reason about experience (CRITICAL)
    assert 'experience' in result[0]['tie_breaker_reason'].lower()
    assert '90' in result[0]['tie_breaker_reason']
    print(f"✓ Candidate a reason: {result[0]['tie_breaker_reason']}")

    # c should have no reason
    assert result[2]['tie_breaker_reason'] is None
    print("✓ Non-tie-breaker has no reason")


def test_apply_tie_breaker_no_critical():
    """Test tie-breaker when no CRITICAL dimensions."""
    print("\n=== Test 3: Tie-breaker without CRITICAL dims ===")

    rankings = [
        {'candidate_id': 'a', 'match_score': 85, 'scores': {'experience': 90}},
        {'candidate_id': 'b', 'match_score': 83, 'scores': {'experience': 75}},
    ]

    # No CRITICAL dimensions
    priorities = {'experience': 'IMPORTANT', 'skills': 'NICE_TO_HAVE'}
    result = apply_tie_breaker_flags(rankings, priorities)

    assert result[0]['tie_breaker_applied'] == True
    assert 'overall profile' in result[0]['tie_breaker_reason'].lower()
    print(f"✓ Fallback reason: {result[0]['tie_breaker_reason']}")


def test_get_tie_breaker_summary():
    """Test tie-breaker summary generation."""
    print("\n=== Test 4: Tie-breaker summary ===")

    rankings = [
        {
            'candidate_id': 'a',
            'rank': 1,
            'match_score': 85,
            'tie_breaker_applied': True,
            'tie_breaker_reason': 'Higher experience score'
        },
        {
            'candidate_id': 'b',
            'rank': 2,
            'match_score': 83,
            'tie_breaker_applied': True,
            'tie_breaker_reason': 'Close to rank 1'
        },
        {
            'candidate_id': 'c',
            'rank': 3,
            'match_score': 70,
            'tie_breaker_applied': False,
            'tie_breaker_reason': None
        },
    ]

    summary = get_tie_breaker_summary(rankings)

    assert summary['count'] == 2
    assert 1 in summary['affected_ranks']
    assert 2 in summary['affected_ranks']
    assert 3 not in summary['affected_ranks']
    assert len(summary['candidates']) == 2
    print(f"✓ Summary count: {summary['count']}")
    print(f"✓ Affected ranks: {summary['affected_ranks']}")


def test_edge_cases():
    """Test edge cases."""
    print("\n=== Test 5: Edge cases ===")

    # Boundary case: exactly 5% difference
    rankings = [
        {'candidate_id': 'a', 'match_score': 85},
        {'candidate_id': 'b', 'match_score': 80},  # Exactly 5% difference
    ]
    tie_ids = detect_tie_breaker_candidates(rankings)
    assert 'a' in tie_ids
    assert 'b' in tie_ids
    print("✓ Boundary (exactly 5%) included")

    # Just over 5%
    rankings = [
        {'candidate_id': 'a', 'match_score': 85},
        {'candidate_id': 'b', 'match_score': 79},  # 6% difference
    ]
    tie_ids = detect_tie_breaker_candidates(rankings)
    assert len(tie_ids) == 0
    print("✓ Just over 5% excluded")

    # Custom threshold
    rankings = [
        {'candidate_id': 'a', 'match_score': 85},
        {'candidate_id': 'b', 'match_score': 75},  # 10% difference
    ]
    tie_ids = detect_tie_breaker_candidates(rankings, threshold=10.0)
    assert 'a' in tie_ids
    assert 'b' in tie_ids
    print("✓ Custom threshold works")


def test_preserve_existing_reason():
    """Test that existing tie-breaker reasons are preserved."""
    print("\n=== Test 6: Preserve existing reasons ===")

    rankings = [
        {
            'candidate_id': 'a',
            'match_score': 85,
            'scores': {'experience': 90},
            'tie_breaker_applied': True,
            'tie_breaker_reason': 'Custom reason from Gemini'
        },
        {
            'candidate_id': 'b',
            'match_score': 83,
            'scores': {'experience': 75}
        },
    ]

    priorities = {'experience': 'CRITICAL'}
    result = apply_tie_breaker_flags(rankings, priorities)

    # a's custom reason should be preserved
    assert result[0]['tie_breaker_reason'] == 'Custom reason from Gemini'
    print("✓ Existing reason preserved")

    # b should get a new reason
    assert result[1]['tie_breaker_applied'] == True
    assert 'experience' in result[1]['tie_breaker_reason'].lower()
    print(f"✓ New reason generated: {result[1]['tie_breaker_reason']}")


if __name__ == '__main__':
    print("Testing Tie-Breaker Logic (Story 4-6)")
    print("=" * 50)

    test_detect_tie_breaker_candidates()
    test_apply_tie_breaker_flags()
    test_apply_tie_breaker_no_critical()
    test_get_tie_breaker_summary()
    test_edge_cases()
    test_preserve_existing_reason()

    print("\n" + "=" * 50)
    print("✓ All tests passed!")
