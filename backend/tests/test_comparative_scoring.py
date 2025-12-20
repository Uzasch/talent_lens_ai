"""Test script for comparative scoring logic (Story 4-5)."""

import sys
sys.path.insert(0, '.')

from services.ranking_service import (
    calculate_match_score,
    validate_weights,
    validate_rankings,
    generate_summary_fallback,
    DIMENSIONS
)

# Mock data for testing
MOCK_CANDIDATES = [
    {
        'id': 'c1',
        'name': 'Alice High',
        'email': 'alice@example.com',
        'experience_years': 5,
        'skills': ['Python', 'React', 'AWS', 'Docker'],
        'projects': [{'name': 'Project A'}, {'name': 'Project B'}],
        'education': [{'degree': 'MS Computer Science'}]
    },
    {
        'id': 'c2',
        'name': 'Bob Medium',
        'email': 'bob@example.com',
        'experience_years': 3,
        'skills': ['JavaScript', 'Node.js'],
        'projects': [{'name': 'Project X'}],
        'education': [{'degree': 'BS Engineering'}]
    },
]


def test_calculate_match_score():
    """Test weighted match score calculation."""
    print("\n=== Test 1: Calculate match score ===")

    scores = {
        'experience': 90,
        'skills': 85,
        'projects': 80,
        'positions': 75,
        'education': 70
    }

    # Equal weights (20 each)
    weights = {dim: 20 for dim in DIMENSIONS}
    result = calculate_match_score(scores, weights)

    # (90*20 + 85*20 + 80*20 + 75*20 + 70*20) / 100 = 80
    expected = 80
    assert result == expected, f"Expected {expected}, got {result}"
    print(f"✓ Equal weights: {result}")

    # Custom weights (experience heavy)
    weights = {
        'experience': 40,
        'skills': 20,
        'projects': 15,
        'positions': 15,
        'education': 10
    }
    result = calculate_match_score(scores, weights)
    # (90*40 + 85*20 + 80*15 + 75*15 + 70*10) / 100 = 83.25 -> 83
    expected = 83
    assert result == expected, f"Expected {expected}, got {result}"
    print(f"✓ Custom weights: {result}")

    # Zero weights edge case
    result = calculate_match_score(scores, {})
    # Should use defaults of 20 each
    assert result == 80, f"Expected 80 with empty weights, got {result}"
    print(f"✓ Empty weights (defaults): {result}")


def test_validate_weights():
    """Test weight validation and normalization."""
    print("\n=== Test 2: Validate weights ===")

    # Already sums to 100
    weights = {dim: 20 for dim in DIMENSIONS}
    result = validate_weights(weights)
    assert sum(result.values()) == 100
    print(f"✓ Already 100: {result}")

    # Sums to 50 - should normalize
    weights = {dim: 10 for dim in DIMENSIONS}
    result = validate_weights(weights)
    assert sum(result.values()) == 100
    print(f"✓ Normalized from 50: {result}")

    # Missing dimensions - should default to 20
    weights = {'experience': 30, 'skills': 25}
    result = validate_weights(weights)
    assert sum(result.values()) == 100
    assert 'projects' in result
    print(f"✓ Missing dims filled: {result}")

    # Sums to 200 - should normalize down
    weights = {dim: 40 for dim in DIMENSIONS}
    result = validate_weights(weights)
    assert sum(result.values()) == 100
    print(f"✓ Normalized from 200: {result}")


def test_validate_rankings():
    """Test ranking validation."""
    print("\n=== Test 3: Validate rankings ===")

    candidates = [{'id': 'c1'}, {'id': 'c2'}]

    # Valid ranking
    rankings = [
        {
            'candidate_id': 'c1',
            'match_score': 85,
            'scores': {'experience': 90, 'skills': 80, 'projects': 85, 'positions': 75, 'education': 70},
            'summary': ['Point 1', 'Point 2', 'Point 3'],
            'why_selected': 'Strong candidate',
            'compared_to_pool': 'Top of pool'
        }
    ]
    result = validate_rankings(rankings, candidates)
    assert len(result) == 1
    assert result[0]['candidate_id'] == 'c1'
    print(f"✓ Valid ranking passed: {result[0]['candidate_id']}")

    # Invalid candidate ID should be filtered
    rankings = [
        {'candidate_id': 'invalid', 'match_score': 50, 'scores': {}}
    ]
    result = validate_rankings(rankings, candidates)
    assert len(result) == 0
    print("✓ Invalid candidate ID filtered")

    # Missing scores should default to 50
    rankings = [
        {'candidate_id': 'c1', 'match_score': 50, 'scores': {'experience': 80}}
    ]
    result = validate_rankings(rankings, candidates)
    assert result[0]['scores']['skills'] == 50  # Defaulted
    assert result[0]['scores']['experience'] == 80  # Preserved
    print(f"✓ Missing scores defaulted: {result[0]['scores']}")

    # Scores clamped to 0-100
    rankings = [
        {'candidate_id': 'c1', 'match_score': 150, 'scores': {'experience': 150, 'skills': -10}}
    ]
    result = validate_rankings(rankings, candidates)
    assert result[0]['scores']['experience'] == 100  # Clamped
    assert result[0]['scores']['skills'] == 0  # Clamped
    assert result[0]['match_score'] == 100  # Clamped
    print("✓ Out-of-range scores clamped")

    # Missing summary should default
    rankings = [
        {'candidate_id': 'c1', 'match_score': 50, 'scores': {}}
    ]
    result = validate_rankings(rankings, candidates)
    assert len(result[0]['summary']) >= 1
    print(f"✓ Missing summary defaulted: {result[0]['summary']}")


def test_generate_summary_fallback():
    """Test fallback summary generation."""
    print("\n=== Test 4: Generate summary fallback ===")

    candidate = MOCK_CANDIDATES[0]
    scores = {dim: 80 for dim in DIMENSIONS}

    summary = generate_summary_fallback(candidate, scores)

    assert len(summary) == 3
    assert '5 years' in summary[0]
    print(f"✓ Summary generated: {summary}")

    # Empty candidate
    empty_candidate = {'id': 'empty', 'name': 'Empty'}
    summary = generate_summary_fallback(empty_candidate, scores)
    assert len(summary) == 3
    assert 'See full profile' in summary[0]
    print(f"✓ Empty candidate summary: {summary}")

    # String JSON fields (as stored in DB)
    import json
    candidate_with_json = {
        'id': 'json',
        'experience_years': 3,
        'skills': json.dumps(['Python', 'Java']),
        'projects': json.dumps([{'name': 'Proj1'}]),
        'education': json.dumps([{'degree': 'BS CS'}])
    }
    summary = generate_summary_fallback(candidate_with_json, scores)
    assert len(summary) == 3
    assert '3 years' in summary[0]
    print(f"✓ JSON string fields handled: {summary}")


def test_edge_cases():
    """Test edge cases."""
    print("\n=== Test 5: Edge cases ===")

    # Empty candidate list for validation
    result = validate_rankings([], [])
    assert result == []
    print("✓ Empty rankings handled")

    # Zero score calculation
    scores = {dim: 0 for dim in DIMENSIONS}
    weights = {dim: 20 for dim in DIMENSIONS}
    result = calculate_match_score(scores, weights)
    assert result == 0
    print("✓ Zero scores handled")

    # All 100 score calculation
    scores = {dim: 100 for dim in DIMENSIONS}
    result = calculate_match_score(scores, weights)
    assert result == 100
    print("✓ Perfect scores handled")


if __name__ == '__main__':
    print("Testing Comparative Scoring Logic (Story 4-5)")
    print("=" * 50)

    test_calculate_match_score()
    test_validate_weights()
    test_validate_rankings()
    test_generate_summary_fallback()
    test_edge_cases()

    print("\n" + "=" * 50)
    print("✓ All tests passed!")
