"""
korean-persona-search 통합 테스트

실제 Nemotron-Personas-Korea 데이터셋(수 GB) 없이도 동작하도록, 합성
5행 Parquet fixture를 만들어 KOREAN_PERSONA_CACHE_DIR로 주입한 뒤
search.py를 서브프로세스로 실행하고 JSON 출력을 검증한다.

CI/로컬 모두에서 `pip install pyarrow pytest` 만으로 실행 가능.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

pa = pytest.importorskip("pyarrow")
pq = pytest.importorskip("pyarrow.parquet")

REPO_ROOT = Path(__file__).resolve().parents[1]
SEARCH_SCRIPT = (
    REPO_ROOT / "skills" / "korean-persona-search" / "scripts" / "search.py"
)


def _row(
    *,
    uuid: str,
    sex: str,
    age: int,
    occupation: str,
    province: str,
    district: str,
    bachelors_field: str = "공학",
    education_level: str = "대학교 졸업",
    summary: str = "",
    professional: str = "",
    sports: str = "",
    arts: str = "",
    travel: str = "",
    culinary: str = "",
    family: str = "",
    skills: str = "",
    hobbies: str = "",
) -> dict:
    return {
        "uuid": uuid,
        "sex": sex,
        "age": age,
        "marital_status": "배우자있음",
        "military_status": "복무필" if sex == "남자" else "비대상",
        "family_type": "1인 가구",
        "housing_type": "아파트",
        "education_level": education_level,
        "bachelors_field": bachelors_field,
        "occupation": occupation,
        "district": district,
        "province": province,
        "cultural_background": f"{province} 출신.",
        "skills_and_expertise": skills,
        "hobbies_and_interests": hobbies,
        "career_goals_and_ambitions": "성장 추구.",
        "summary_persona": summary,
        "professional_persona": professional,
        "sports_persona": sports,
        "arts_persona": arts,
        "travel_persona": travel,
        "culinary_persona": culinary,
        "family_persona": family,
    }


@pytest.fixture(scope="module")
def synthetic_cache(tmp_path_factory):
    """합성 5행 데이터셋 — province/sex/age/occupation/persona 텍스트가 다양함."""
    cache = tmp_path_factory.mktemp("kpcache")
    rows = [
        _row(
            uuid="u1-seoul-dev",
            sex="남자", age=30,
            occupation="응용 소프트웨어 개발자",
            province="서울", district="서울-강남구",
            professional="Python, Go, Kubernetes 경험 5년. 핀테크 백엔드.",
            arts="재즈를 좋아한다.",
            skills="Python, Go", hobbies="등산",
        ),
        _row(
            uuid="u2-seoul-designer",
            sex="여자", age=28,
            occupation="시각 디자이너",
            province="서울", district="서울-마포구",
            bachelors_field="미술",
            professional="브랜드 아이덴티티 디자인. Figma 숙련.",
            arts="현대 미술 관심.",
            skills="Figma, Illustrator", hobbies="갤러리 투어",
        ),
        _row(
            uuid="u3-busan-doctor",
            sex="남자", age=45,
            occupation="내과 의사",
            province="부산", district="부산-해운대구",
            bachelors_field="의학",
            professional="대학병원 내과 전문의 15년.",
            sports="러닝, 골프.",
            skills="진료, 임상연구", hobbies="러닝",
        ),
        _row(
            uuid="u4-gyeonggi-pm",
            sex="여자", age=35,
            occupation="프로덕트 매니저",
            province="경기", district="경기-성남시",
            bachelors_field="경영",
            professional="B2B SaaS PM. 데이터 기반 의사결정.",
            travel="동남아 자주 감.",
            skills="JIRA, Notion", hobbies="여행",
        ),
        _row(
            uuid="u5-jeju-self",
            sex="남자", age=60,
            occupation="자영업자(게스트하우스 운영)",
            province="제주", district="제주-제주시",
            bachelors_field="자영업",
            education_level="고등학교 졸업",
            summary="제주에서 게스트하우스를 운영하는 60대 자영업자.",
            culinary="흑돼지 요리에 능숙.",
            skills="요식업, 운영", hobbies="낚시",
        ),
    ]
    table = pa.Table.from_pylist(rows)
    pq.write_table(table, str(cache / "shard-00000.parquet"))
    return cache


def _run(synthetic_cache: Path, *args: str) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    env["KOREAN_PERSONA_CACHE_DIR"] = str(synthetic_cache)
    return subprocess.run(
        [sys.executable, str(SEARCH_SCRIPT), *args],
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


# ------------------------- 8 케이스 -------------------------


def test_province_filter(synthetic_cache):
    """1) --province 단일 필터"""
    r = _run(synthetic_cache, "--province", "서울", "--n", "5")
    assert r.returncode == 0, r.stderr
    cards = json.loads(r.stdout)
    assert len(cards) == 2
    assert {c["demographics"]["province"] for c in cards} == {"서울"}


def test_age_range(synthetic_cache):
    """2) --age-min / --age-max 범위"""
    r = _run(synthetic_cache, "--age-min", "28", "--age-max", "38", "--n", "5")
    assert r.returncode == 0, r.stderr
    cards = json.loads(r.stdout)
    ages = [c["demographics"]["age"] for c in cards]
    assert ages
    assert all(28 <= a <= 38 for a in ages)


def test_occupation_contains(synthetic_cache):
    """3) --occupation-contains 부분일치"""
    r = _run(synthetic_cache, "--occupation-contains", "개발", "--n", "5")
    assert r.returncode == 0, r.stderr
    cards = json.loads(r.stdout)
    assert len(cards) == 1
    assert "개발" in cards[0]["demographics"]["occupation"]


def test_keywords_or_across_persona_text(synthetic_cache):
    """4) --keywords (콤마 구분) — persona 텍스트 다중 컬럼에 OR 매칭"""
    # 'Kubernetes'는 u1.professional, '흑돼지'는 u5.culinary
    r = _run(synthetic_cache, "--keywords", "Kubernetes,흑돼지", "--n", "5")
    assert r.returncode == 0, r.stderr
    cards = json.loads(r.stdout)
    uuids = {c["uuid"] for c in cards}
    assert {"u1-seoul-dev", "u5-jeju-self"} <= uuids


def test_diversity_sex_balance(synthetic_cache):
    """5) --diversity sex — 두 성별이 모두 표본에 포함"""
    r = _run(synthetic_cache, "--diversity", "sex", "--n", "4", "--seed", "0")
    assert r.returncode == 0, r.stderr
    cards = json.loads(r.stdout)
    assert {c["demographics"]["sex"] for c in cards} == {"남자", "여자"}


def test_persona_types_selective(synthetic_cache):
    """6) --persona-types 선택 출력만 포함"""
    r = _run(
        synthetic_cache,
        "--occupation-contains", "개발",
        "--persona-types", "professional,arts",
        "--n", "1",
    )
    assert r.returncode == 0, r.stderr
    cards = json.loads(r.stdout)
    assert cards
    personas = cards[0]["personas"]
    assert set(personas.keys()) == {"professional", "arts"}
    assert "summary" not in personas
    assert "Kubernetes" in personas["professional"]


def test_empty_result_graceful(synthetic_cache):
    """7) 매칭 0건 — exit 0, stdout '[]', stderr 안내"""
    r = _run(synthetic_cache, "--province", "강원", "--n", "5")
    assert r.returncode == 0, r.stderr
    assert json.loads(r.stdout) == []
    assert "결과 0건" in r.stderr or "필터를 완화" in r.stderr


def test_missing_cache_directory(tmp_path):
    """8) 캐시 부재 — exit 1 + 다운로드 안내 메시지"""
    env = os.environ.copy()
    env["KOREAN_PERSONA_CACHE_DIR"] = str(tmp_path / "does-not-exist")
    r = subprocess.run(
        [sys.executable, str(SEARCH_SCRIPT), "--n", "1"],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert r.returncode != 0
    assert "캐시 없음" in r.stderr
    assert "download.py" in r.stderr


# ------------------------- attribution / 출력 구조 -------------------------


def test_attribution_present(synthetic_cache):
    """라이선스 attribution이 모든 카드에 자동 삽입되는지 확인 (CC BY 4.0 준수)"""
    r = _run(synthetic_cache, "--n", "3", "--seed", "0")
    assert r.returncode == 0, r.stderr
    cards = json.loads(r.stdout)
    for c in cards:
        assert c["_attribution"] == "NVIDIA Nemotron-Personas-Korea (CC BY 4.0)"


def test_normalized_card_shape(synthetic_cache):
    """카드 필드 구조 — demographics / personas / context / _attribution"""
    r = _run(synthetic_cache, "--n", "1", "--seed", "0")
    cards = json.loads(r.stdout)
    assert len(cards) == 1
    c = cards[0]
    assert set(c.keys()) >= {"uuid", "demographics", "personas", "context", "_attribution"}
    assert "occupation" in c["demographics"]
    assert "skills_and_expertise" in c["context"]
    assert isinstance(c["context"]["skills_and_expertise"], list)
