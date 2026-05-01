# Scenario — 백엔드 개발자 (한국 푸드테크 스타트업)

## 입력 프롬프트

> "한국 푸드테크 스타트업의 신규 배달 앱을 위한 백엔드 개발자 에이전트 정의를 만들어줘"

## 조건

- 동일 프롬프트 1개 역할(백엔드 개발자)
- 합성 5행 데이터셋(`KOREAN_PERSONA_CACHE_DIR`)을 사용하여 실제 `skills/korean-persona-search/scripts/search.py` 호출 후 워크플로우 적용
- 두 스킬을 별도 세션에서 호출하여 산출물 비교

## 결과 요약

| 차원 | Run A (`harness`) | Run B (`korean-persona-harness`) |
|---|---|---|
| 분량 | 35 줄 / 193 단어 | 76 줄 / 646 단어 |
| 1인칭 발화 샘플 | 0 | 3 |
| 산업 전문 어휘 | 추상 (신뢰성·확장성·테스트) | 구체 (PR/머지/핫픽스/RCA/PG/VAN 등 16개) |
| 인구통계 단서 | 없음 | 8 항목 |
| 출처 attribution | 없음 | uuid + CC BY 4.0 |

핵심 차이: **에이전트가 "백엔드 개발자에 *대해* 이야기"하는가, "백엔드 개발자*처럼* 말하는가"**. Run A는 추상 직군 명세서, Run B는 1인칭 화자 캐릭터.

상세 비교: [`comparison.md`](comparison.md)

## 디렉토리 구조

```
backend-developer/
├── README.md                              ← 이 파일 (요약)
├── comparison.md                          ← 정량·정성 비교
├── run-a-baseline/
│   └── backend-developer.md               ← harness 단독 산출물 (35 줄)
└── run-b-grounded/
    ├── persona.json                       ← 검색된 페르소나 카드 (uuid u1)
    └── backend-developer.md               ← korean-persona-harness 산출물 (76 줄)
```

## 페르소나 출처

- **uuid**: u1 (합성 5행 fixture)
- **요약**: 32세 남자 / 서울 강남 / 응용 소프트웨어 개발자 / 백엔드 7년차 / 결제 시스템 담당
- **데이터셋**: NVIDIA [Nemotron-Personas-Korea](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea) (CC BY 4.0)
- **합성-but-grounded**: 인구통계는 실제 한국 분포 반영, 페르소나 텍스트는 LLM 생성

## 재현 방법

본 포크 설치 후:

```bash
# 합성 5행 데이터셋으로 재현 (테스트용)
KOREAN_PERSONA_CACHE_DIR=$(pwd)/tests/fixtures \
  python3 skills/korean-persona-search/scripts/search.py \
  --occupation-contains 개발 --persona-types summary,professional --n 1
```

실제 데이터셋(수 GB) 사용 시 `python3 skills/korean-persona-search/scripts/download.py` 후 동일 명령.
