# ParfumAI — Motor Testleri
# Copyright (c) 2026 Ahmet Rıfai Kuyucu
# Tüm Hakları Saklıdır — All Rights Reserved.

import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from legacy.scoring import ScoringEngine
from perfume_engine import PerfumeMatchingEngine


def test_scoring_engine_returns_required_keys():
    answers = {1: 0, 4: 1, 6: 2, 7: 1, 11: 3, 12: 0}
    result = ScoringEngine().process_answers(answers)
    assert 'top_pct' in result
    assert 'middle_pct' in result
    assert 'base_pct' in result
    assert 'top_dominant' in result
    assert 'middle_dominant' in result
    assert 'base_dominant' in result
    assert 'profile_type' in result
    assert 'nota_detay' in result


def test_scoring_percentages_sum_to_100():
    for q_vals in [(0, 0, 0, 0, 0, 0), (2, 1, 0, 2, 1, 0), (3, 3, 3, 3, 3, 3)]:
        answers = dict(enumerate(q_vals, 1))
        result = ScoringEngine().process_answers(answers)
        total = result['top_pct'] + result['middle_pct'] + result['base_pct']
        assert abs(total - 100) < 1, f"Percentages should sum to ~100, got {total}"


def test_matching_engine_returns_three_seasons():
    engine = PerfumeMatchingEngine()
    profile = {
        'top_pct': 40, 'middle_pct': 30, 'base_pct': 30,
        'top_dominant': 'citrus', 'middle_dominant': 'floral', 'base_dominant': 'musk',
        'profile_type': 'Yaz-Kehribar', 'nota_detay': {}
    }
    result = engine.find_matches(profile, 'unisex')
    assert 'yaz' in result
    assert 'kis' in result
    assert 'dört_mevsim' in result
    assert len(result['yaz']) == 3
    assert len(result['kis']) == 3
    assert len(result['dört_mevsim']) == 3


def test_gender_filtering_excludes_opposite():
    engine = PerfumeMatchingEngine()
    profile = {
        'top_pct': 33, 'middle_pct': 33, 'base_pct': 34,
        'top_dominant': 'citrus', 'middle_dominant': 'floral', 'base_dominant': 'musk',
        'profile_type': 'Karma', 'nota_detay': {}
    }
    result = engine.find_matches(profile, 'kadin')
    for season in ['yaz', 'kis', 'dört_mevsim']:
        for p in result[season]:
            assert p['gender'] in ('kadin', 'unisex'), f"{p['name']} is {p['gender']}, expected kadın/unisex"


def test_different_answers_different_results():
    engine = PerfumeMatchingEngine()
    base_profile = {
        'top_pct': 33, 'middle_pct': 33, 'base_pct': 34,
        'top_dominant': 'citrus', 'middle_dominant': 'floral', 'base_dominant': 'musk',
        'profile_type': 'Karma', 'nota_detay': {}
    }
    alt_profile = {
        'top_pct': 50, 'middle_pct': 25, 'base_pct': 25,
        'top_dominant': 'aqua', 'middle_dominant': 'spice_mid', 'base_dominant': 'oud',
        'profile_type': 'Farklı', 'nota_detay': {}
    }
    base_result = engine.find_matches(base_profile, 'unisex')
    alt_result = engine.find_matches(alt_profile, 'unisex')
    base_names = {p['name'] for season in base_result.values() if isinstance(season, list) for p in season}
    alt_names = {p['name'] for season in alt_result.values() if isinstance(season, list) for p in season}
    assert base_names != alt_names, "Different profiles should yield different perfume sets"


if __name__ == '__main__':
    test_scoring_engine_returns_required_keys()
    test_scoring_percentages_sum_to_100()
    test_matching_engine_returns_three_seasons()
    test_gender_filtering_excludes_opposite()
    test_different_answers_different_results()
    print(f"All {5} tests passed!")
