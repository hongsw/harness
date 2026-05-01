# Examples — Korean Persona Injection

이 디렉토리는 `korean-persona-harness` 스킬이 실제로 생성한 산출물의 박제 샘플이다. 사용자가 본 포크를 설치하기 전·후에 **결과물 품질을 직접 확인**할 수 있도록 한다.

## 왜 examples를 둔가

본 포크의 thesis는 *"data-grounded synthetic 페르소나로 grounded된 하네스가 단순 직군명 프롬프트보다 풍부한 에이전트 정의를 만든다"*이다 ([상세](../../docs/why-data-grounded-synthetic.md)). 이 주장의 진실 여부는 산출물을 보면 가장 빨리 판단할 수 있다.

각 시나리오는 다음을 박제한다:
- **Run A (baseline)** — 기존 `harness` 스킬 단독 산출물 (직군명만 사용)
- **Run B (grounded)** — `korean-persona-harness` 산출물 (Nemotron-Personas-Korea 카드 주입)
- **comparison.md** — 정량(라인·어휘 수) + 정성(1인칭 발화·인구통계 단서·출처) 비교

## 데이터 출처 / 라이선스

페르소나 카드는 [NVIDIA Nemotron-Personas-Korea](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea) (CC BY 4.0)에서 검색·샘플링된 **합성-but-grounded** 카드다. 합성 LLM 생성물이며 실제 한국인 응답이 아니지만 인구통계 분포는 실제 한국 사회를 반영하도록 설계되어 있다 ("data-grounded synthetic"). 모든 산출물 파일 하단·페르소나 JSON에 uuid + CC BY 4.0 attribution이 자동 삽입된다.

## 현재 박제된 시나리오

| 시나리오 | 역할 수 | 데이터 출처 | 마지막 업데이트 |
|---|---|---|---|
| [`backend-developer/`](backend-developer/) | 1 (백엔드 개발자) | 합성 5행 fixture (`KOREAN_PERSONA_CACHE_DIR`) | 2026-04-27 |

> 추가 시나리오(푸드테크 5인, B2B SaaS 영업팀 4인, fintech 컴플라이언스 4인, 한국 의료 IT 5인)는 실제 데이터셋 다운로드 후 박제 예정. 외부 사용자의 dogfood 산출물도 PR로 환영한다.

## 시나리오 추가 방법 (기여)

1. 본 포크 설치: `docs/quickstart-korean-persona.md` 참조
2. 데이터셋 캐시 다운로드: `python3 skills/korean-persona-search/scripts/download.py`
3. `korean-persona-harness` 스킬 트리거 후 `_workspace/korean-persona-harness/` 산출물 확인
4. `examples/korean-persona/{scenario-name}/` 하위에 다음 구조로 복사:
   ```
   {scenario-name}/
   ├── README.md           # 시나리오 요약, 입력 프롬프트, 비교 결론 한 줄
   ├── comparison.md       # 정량·정성 비교 표
   ├── run-a-baseline/     # harness 단독 산출물
   │   └── *.md
   └── run-b-grounded/     # korean-persona-harness 산출물
       ├── persona.json    # 페르소나 카드 (uuid + CC BY 4.0)
       └── *.md            # 에이전트 정의
   ```
5. PR 보낼 때 attribution 누락이 없는지 확인 ([Reviewer checklist](../../docs/why-data-grounded-synthetic.md#박제-기여-체크리스트))

## 관련 문서

- [본 포크 thesis](../../docs/why-data-grounded-synthetic.md) — 왜 data-grounded synthetic 페르소나가 eval substrate로 가치 있는가
- [Quickstart](../../docs/quickstart-korean-persona.md) — 설치·재시작·첫 실행
- [`korean-persona-harness` SKILL.md](../../skills/korean-persona-harness/SKILL.md) — 메타 오케스트레이터 워크플로우
