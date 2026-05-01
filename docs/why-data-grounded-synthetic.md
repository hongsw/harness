# Why Data-Grounded Synthetic Personas?

## TL;DR

본 포크가 **합성**(`real`이 아닌) 한국 페르소나를 의도적으로 사용하는 이유:

1. 생성된 에이전트가 *직군에 대해 이야기*하는 게 아니라 *그 사람처럼 말하게* 한다
2. 추천·평가 시스템(예: [`hongsw/clawfit`](https://github.com/hongsw/clawfit))의 **eval substrate** — 추상 axis 대신 grounded 사용자 모집단에 대해 추천 정확도를 측정 가능하게 한다
3. 라이선스·프라이버시·재현성을 모두 만족 (CC BY 4.0 + uuid attribution + 결정론적 시드)

용어 정직성: "실제 한국인이 응답한 데이터"가 아니라 "**합성 LLM 생성, 인구통계 분포는 실제 한국 반영**"이다. "real Korean personas" 표현 대신 "**data-grounded synthetic Korean personas**"를 사용한다.

---

## 문제 — 직군 프롬프트의 한계

LLM에게 "시니어 백엔드 개발자처럼 답해줘"라고 하면 일어나는 일:

- 모델은 학습 분포의 **평균적 시니어 백엔드 개발자**를 끌어낸다
- 결과는 *누구의* 시니어 백엔드 개발자인지 모호한 추상 — SF 스타트업의 35세 시니어인지, 서울의 45세 부장인지 알 수 없음
- 5명의 다른 직군을 시켜도 **모두 비슷한 톤**이 나온다 (LLM이 "전문가"를 생성하는 단일 분포가 있음)

이 문제는 두 단계로 발현된다:

1. **개발 단계**: 에이전트 팀이 추상적이라 시뮬레이션 신뢰도가 낮음 — "한국 fintech 컴플라이언스 매니저"라고 시켜도 한국 컴플라이언스 컨텍스트가 반영되지 않음
2. **리뷰 단계**: PR을 리뷰할 때 "이 변경을 *진짜 한국 fintech 컴플라이언스 매니저*가 보면 어떤 지적을 할까?"를 시뮬레이션하려면 grounded 페르소나가 필요

---

## 해법 — Out-of-Distribution 진정성 주입

[NVIDIA Nemotron-Personas-Korea](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea) (100만 행, CC BY 4.0)는 한국 통계청 분포를 반영한 합성 페르소나 데이터셋이다. 각 카드:

- **인구통계**: 성별 / 연령 / 결혼·가족 상태 / 학력 / 전공 / 직업 / 지역 (시·구) / 주거 형태 / 병역 상태
- **7가지 페르소나 텍스트**: summary / professional / sports / arts / travel / culinary / family
- **컨텍스트**: 문화적 배경 / 스킬·전문성 / 취미·관심 / 커리어 목표

이 카드를 에이전트 정의에 주입하면 모델은 다음을 받는다:

- 자기가 모르는 출신지·주거형태·세대 단서
- 자기 학습 분포에 없는 1인칭 화법 패턴
- 산업·직군에 특화된 어휘 (예: 결제 PG/VAN, 핫픽스, RCA, 멱등성)

결과: 모델이 **혼자 만들어내지 못할 특이성**을 가진 에이전트가 생성된다. 5명을 만들면 5개의 식별 가능한 목소리가 나온다 ([실제 산출물 참조](../examples/korean-persona/backend-developer/comparison.md)).

---

## 왜 "real"이 아니라 "data-grounded synthetic"인가

용어 정직성은 본 포크의 신뢰성과 직결된다.

| 표현 | 정확한가 | 사용 |
|---|---|---|
| "real Korean personas" | ❌ 실제 한국인 응답이 아님 (LLM 합성) | **회피** |
| "actual Korean people" | ❌ 실존 인물과 매칭되지 않음 | **회피** |
| "data-grounded synthetic Korean personas" | ✅ 합성 + 인구통계는 실제 분포 | **사용** |
| "통계적으로 한국적" / "out-of-distribution 진정성" | ✅ 가치 주장에 적합 | **사용** |

본 포크의 README, 스킬 정의, 코멘트, 발표 자료 모두 후자를 사용한다. 마케팅 임팩트는 약간 줄지만 다음을 얻는다:

- "합성 데이터를 진짜라고 광고했다"는 비판 사전 차단
- 라이선스·프라이버시 인식 명확
- 다른 합성 데이터셋(영어, 일본어 등)으로 확장 시 동일 톤 재사용 가능

---

## clawfit과의 연결 — Real Persona as Eval Substrate

본 포크의 가장 야심찬 주장: **추천 엔진의 가치는 *어떤 사용자 모집단*에 대해 정확한가에 달렸다. 평가 모집단이 추상 axis면 추천도 추상에 머문다.**

[`hongsw/clawfit`](https://github.com/hongsw/clawfit)은 AI 에이전트 도구·LLM·하드웨어 추천 엔진이다. 현재 사용자 프로필은 다음 axis로 정의된다:

- `hardware`, `network`, `governance_need`, `team_size`, `primary_role`, `primary_task`, `pricing_tier`, `data_sensitivity`, `optimal_maturity`

이 axis는 *추상적이다*. "primary_role: developer"는 SF 스타트업 풀스택과 한국 SI 백엔드를 같은 axis로 묶는다. 추천이 두 사용자에게 같이 정확하기는 어렵다.

본 포크의 `korean-persona-search` / `korean-role-profile` 산출물은 axis를 **데이터-grounded 사용자 카드**로 대체할 수 있다. 4개 직결 통합 지점:

### 1. clawfit 프로필 스키마에 `cultural_context` 축 도입
한국 fintech 컴플라이언스 매니저와 SF 스타트업 PM이 같은 axis로 평가되지 않게. `cultural_context: ["ko-KR", "en-US", ...]`.

### 2. 페르소나 → clawfit eval 입력 직접 export
신규 스크립트 `scripts/export-personas-to-clawfit.py` (예정). 페르소나 카드 N개를 clawfit 추천 시뮬레이션 입력으로 사용 → 추상 axis 대신 grounded 모집단에 대해 추천 정확도 측정.

### 3. clawfit 레지스트리에 `cultural_authenticity` 평가 항목 추가
도구가 특정 문화·지역 사용자에게 진정성 있게 작동하는가. weak/medium/strong. 본 포크는 strong (data-grounded). 다른 도구도 평가받게 함으로써 axis 자체가 가치를 가짐.

### 4. `harness-korean` 자체를 clawfit L3 레지스트리 항목으로 등록
한국 사용자가 clawfit 추천을 받을 때 본 포크가 우선순위 진입.

상세 로드맵: [`/Users/hongmartin/.claude/plans/validated-soaring-key.md`](../../../.claude/plans/validated-soaring-key.md) (로컬 plan 파일)

---

## 무엇이 진실로 검증해야 하는가

본 포크의 thesis가 옳은지는 **외부 신호**로 측정한다:

- 1개월: `examples/` 박제에 외부 사용자 1명 이상의 공개 피드백
- 3개월: clawfit `cultural_context` 축이 v0.4 후보로 진입
- 6개월: 외부 사용자가 본 포크 산출물을 자기 프로젝트에 복사해 쓴 사례 1건 이상
- 12개월: 한국 LLM 평가 / fintech / SaaS 프로젝트 1곳 이상에서 dogfood

내부 코드 검증(pytest 통과, CI 녹색)은 *동작하는가*만 본다. 외부 신호가 *가치 있는가*를 본다.

---

## 한계·주의

1. **합성의 한계**: NVIDIA가 한국 분포 반영을 주장하지만 실제 응답이 아님. 의료·법률·심리 영역에서 임상적 결정의 근거로 사용해선 안 됨
2. **데이터셋 deprecation 위험**: NVIDIA 단일 출처. 사라지면 본 포크 핵심이 무너짐. v2 시점에 fallback (한국 통계청 분포 + LLM) 설계 필요
3. **"직군다움" 의미적 정합 검증의 함정**: 통계 집계는 분포만 보장, 의미는 못 본다. 향후 가상 한국 HR 매니저 sub-agent로 보완 예정
4. **두 프로젝트 한 인격**: harness와 clawfit 모두 hongsw 운영. 통합은 빠르지만 "자기 추천" 인상을 피하려면 외부 dogfood 신호가 선행되어야 함

---

## 박제 기여 체크리스트

`examples/korean-persona/` PR을 보낼 때:

- [ ] 디렉토리 구조 준수: `{name}/comparison.md` + `run-a-baseline/` + `run-b-grounded/persona.json`
- [ ] `persona.json`에 `_attribution: "NVIDIA Nemotron-Personas-Korea (CC BY 4.0)"` 자동 삽입 확인
- [ ] 페르소나 uuid를 `comparison.md` 또는 `README.md`에 명시
- [ ] "real Korean" / "actual Korean" 표현 미사용 — "data-grounded synthetic" 톤
- [ ] 시나리오 설명에 입력 프롬프트, 사용 데이터셋(합성 fixture / 실제 캐시), 한 줄 결론 포함
- [ ] (선택) `comparison.md`에 정량 표 + 정성 인용 2~3건

## 관련 문서

- [Quickstart](quickstart-korean-persona.md) — 설치·재시작·첫 실행
- [Examples](../examples/korean-persona/README.md) — 박제된 산출물 모음
- `skills/korean-persona-harness/SKILL.md` — 메타 오케스트레이터 워크플로우
- `skills/korean-persona-search/SKILL.md` — 검색·다양성 샘플링 스킬
