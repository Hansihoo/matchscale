"""연령 인구 비중 검증 테스트.

CSV의 연령별 비율 합과 서비스가 계산한 연령 구간 비중이 일치하는지 확인합니다.
"""

import os
from typing import Tuple

import pandas as pd

from app.services.stats_service import calculate_probability


def _project_path(*parts: str) -> str:
    """프로젝트 루트 기준 경로 생성.

    Args:
        parts: 경로 조각들

    Returns:
        str: 절대 경로
    """
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.normpath(os.path.join(here, os.pardir))
    return os.path.join(root, *parts)


def _expected_share_from_csv(gender: str, age_range: Tuple[int, int]) -> float:
    """CSV의 '비율' 합으로 기대 연령 구간 비중(확률)을 계산합니다.

    Args:
        gender: "남성" 또는 "여성"
        age_range: (min_age, max_age) 포함 구간

    Returns:
        float: 확률(0~1)
    """
    csv_name = "male_population_by_age_korea.csv" if gender == "남성" else "female_population_by_age_korea.csv"
    csv_path = _project_path("data", csv_name)
    df = pd.read_csv(csv_path)
    # 컬럼 추론
    col_age = df.columns[0]
    col_ratio = df.columns[2]
    a_min, a_max = age_range
    total = 0.0
    for _, row in df.iterrows():
        age_raw = str(row.get(col_age, "")).strip()
        if not age_raw or "총" in age_raw:
            continue
        try:
            age = int(str(age_raw).replace("세", "").strip())
        except Exception:
            continue
        if a_min <= age <= a_max:
            r_raw = str(row.get(col_ratio, "0")).strip().replace("%", "")
            try:
                total += float(r_raw)
            except Exception:
                continue
    return max(0.0, min(1.0, total / 100.0))


def _get_age_step_probability(result: dict) -> float:
    """결과에서 '나이' 단계의 확률을 가져옵니다."""
    details = result.get("calculation_details", {}).get("condition_details", [])
    for d in details:
        if d.get("condition") == "나이":
            return float(d.get("probability", 0.0))
    return 0.0


def test_age_range_share_male_25_34_matches_csv_sum():
    """남성 25-34세 연령 비중이 CSV '비율' 합과 일치."""
    gender = "남성"
    age_range = (25, 34)
    expected = _expected_share_from_csv(gender, age_range)
    result = calculate_probability({"gender": gender, "age_range": list(age_range)})
    age_prob = _get_age_step_probability(result)
    assert abs(age_prob - expected) < 1e-4


def test_age_range_share_female_25_34_matches_csv_sum():
    """여성 25-34세 연령 비중이 CSV '비율' 합과 일치."""
    gender = "여성"
    age_range = (25, 34)
    expected = _expected_share_from_csv(gender, age_range)
    result = calculate_probability({"gender": gender, "age_range": list(age_range)})
    age_prob = _get_age_step_probability(result)
    assert abs(age_prob - expected) < 1e-4


def test_single_age_band_share_male_28_matches_csv_sum_25_29():
    """남성 age=28은 25-29 구간 비중과 동일하게 계산되어야 함."""
    gender = "남성"
    expected = _expected_share_from_csv(gender, (25, 29))
    result = calculate_probability({"gender": gender, "age": 28})
    age_prob = _get_age_step_probability(result)
    assert abs(age_prob - expected) < 1e-4


