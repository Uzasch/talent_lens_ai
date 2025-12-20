"""Test script for analysis service (Story 4-7)."""

import sys
sys.path.insert(0, '.')

from services.analysis_service import (
    generate_why_not_others,
    ANALYSIS_PHASES,
    format_top_candidates
)


def test_generate_why_not_others():
    """Test why_not_others explanation generation."""
    print("\n=== Test 1: Generate why_not_others ===")

    # Case 1: Some eliminated, some below top 6
    rankings = [
        {'candidate_id': f'c{i}', 'match_score': 90 - i*5}
        for i in range(10)
    ]  # Scores: 90, 85, 80, 75, 70, 65, 60, 55, 50, 45

    eliminated = [
        {'id': 'e1', 'name': 'Eliminated 1', 'reason': 'Low score'},
        {'id': 'e2', 'name': 'Eliminated 2', 'reason': 'Low score'},
    ]

    pool_size = 12

    result = generate_why_not_others(rankings, eliminated, pool_size)

    assert '12 candidates' in result
    assert '2 eliminated' in result
    assert '4 candidates ranked below' in result
    print(f"✓ Full explanation: {result}")

    # Case 2: No eliminations
    result = generate_why_not_others(rankings, [], 10)
    assert '10 candidates' in result
    assert 'eliminated' not in result
    print("✓ No eliminations handled")

    # Case 3: All in top 6 (no below)
    small_rankings = rankings[:6]
    result = generate_why_not_others(small_rankings, [], 6)
    assert '6 candidates' in result
    assert 'below' not in result
    print("✓ All in top 6 handled")

    # Case 4: Empty rankings
    result = generate_why_not_others([], [], 0)
    assert '0 candidates' in result
    print("✓ Empty rankings handled")


def test_analysis_phases():
    """Test analysis phases constant."""
    print("\n=== Test 2: Analysis phases ===")

    assert len(ANALYSIS_PHASES) == 7
    assert ANALYSIS_PHASES[0] == "Extracting resumes"
    assert ANALYSIS_PHASES[-1] == "Complete"
    print(f"✓ Phases: {ANALYSIS_PHASES}")


def test_format_top_candidates():
    """Test top candidates formatting."""
    print("\n=== Test 3: Format top candidates ===")

    top_candidates = [
        {
            'candidate_id': 'c1',
            'rank': 1,
            'match_score': 92,
            'scores': {'experience': 95, 'skills': 90},
            'summary': ['Strong Python', 'AWS expert'],
            'why_selected': 'Best match',
            'compared_to_pool': 'Top scorer',
            'tie_breaker_applied': False,
            'tie_breaker_reason': None
        }
    ]

    pool = [
        {'id': 'c1', 'name': 'Alice Smith', 'email': 'alice@example.com'},
        {'id': 'c2', 'name': 'Bob Jones', 'email': 'bob@example.com'},
    ]

    result = format_top_candidates(top_candidates, pool)

    assert len(result) == 1
    assert result[0]['name'] == 'Alice Smith'
    assert result[0]['email'] == 'alice@example.com'
    assert result[0]['match_score'] == 92
    assert result[0]['rank'] == 1
    print(f"✓ Formatted candidate: {result[0]['name']} (rank {result[0]['rank']})")

    # Missing pool data
    top_candidates_missing = [
        {'candidate_id': 'unknown', 'rank': 1, 'match_score': 50}
    ]
    result = format_top_candidates(top_candidates_missing, pool)
    assert result[0]['name'] == 'Unknown'
    print("✓ Missing pool data handled")


def test_edge_cases():
    """Test edge cases."""
    print("\n=== Test 4: Edge cases ===")

    # Empty top candidates
    result = format_top_candidates([], [])
    assert result == []
    print("✓ Empty top candidates handled")

    # Rankings with no match_score
    rankings = [
        {'candidate_id': 'c1'},
        {'candidate_id': 'c2'}
    ]
    result = generate_why_not_others(rankings, [], 2)
    assert '2 candidates' in result
    print("✓ Missing match_score handled")


if __name__ == '__main__':
    print("Testing Analysis Service (Story 4-7)")
    print("=" * 50)

    test_generate_why_not_others()
    test_analysis_phases()
    test_format_top_candidates()
    test_edge_cases()

    print("\n" + "=" * 50)
    print("✓ All tests passed!")
