# Quickstart — Korean Persona Injection

`korean-persona-search`, `korean-voice-adapter`, `korean-persona-harness` 3개 스킬을 **Claude Code**·**Codex CLI**에 설치하고 첫 실행까지 검증한다. 두 런타임의 스킬 포맷은 동일하며 설치 경로만 다르다.

일반 `harness` 스킬의 빠른 시작은 [`quickstart.md`](./quickstart.md) 참조.

## 1. 설치

네 가지 경로 중 하나를 선택한다. 일반 사용자는 ㄱ(Claude Code) 또는 ㄷ(스크립트), Codex 사용자는 ㄴ.

### ㄱ. Claude Code — 플러그인 마켓플레이스 (권장)

Claude Code 세션에서:

```
/plugin marketplace add hongsw/harness
/plugin install harness@harness
```

> 본가 머지 후에는 `hongsw/harness` 대신 `revfactory/harness`로 바꿔 쓰면 된다. 두 마켓플레이스의 `name`(둘 다 `harness-marketplace`)과 플러그인 `name`(둘 다 `harness`)이 동일하므로 동시에 추가하면 그림자 충돌이 난다 — 한쪽만 유지할 것.

설치 후 **3번(재시작)**으로 이동.

### ㄴ. Codex CLI — `skill-installer`로 GitHub 직접 설치

```bash
python3 ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo hongsw/harness \
  --ref main \
  --path skills/korean-persona-search \
  --path skills/korean-voice-adapter \
  --path skills/korean-persona-harness
```

설치 위치: `${CODEX_HOME:-~/.codex}/skills/`. 설치 후 **3번(재시작)**.

### ㄷ. 한 줄 스크립트 (양 런타임 동시 가능)

리포 클론 후:

```bash
# Claude Code (현재 프로젝트)
./scripts/install-korean-persona.sh --target claude-code

# Codex (전역)
./scripts/install-korean-persona.sh --target codex

# 둘 다
./scripts/install-korean-persona.sh --target both

# Codex로 GitHub에서 직접 (포크에서)
./scripts/install-korean-persona.sh --target codex --from-github hongsw/harness

# 미리보기
./scripts/install-korean-persona.sh --target both --dry-run
```

전체 옵션은 `./scripts/install-korean-persona.sh --help` 참조. 설치 후 **3번(재시작)**.

### ㄹ. 수동 복사 (참고용)

```bash
# Claude Code (프로젝트 단위)
mkdir -p .claude/skills
cp -r skills/korean-persona-search skills/korean-voice-adapter skills/korean-persona-harness .claude/skills/

# Codex (전역)
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
cp -r skills/korean-persona-search skills/korean-voice-adapter skills/korean-persona-harness "${CODEX_HOME:-$HOME/.codex}/skills/"
```

## 2. 의존성 + 데이터셋 캐시 (최초 1회)

```bash
# Python 패키지
pip install huggingface_hub pyarrow
# 또는: uv pip install huggingface_hub pyarrow

# 데이터셋 캐시 (수 GB)
python3 skills/korean-persona-search/scripts/download.py
# 빠른 테스트용으론 일부 shard만:
python3 skills/korean-persona-search/scripts/download.py --shards 1
```

캐시 경로 기본값: `~/.cache/korean-persona-search/`. 환경변수 `KOREAN_PERSONA_CACHE_DIR`로 변경 가능.

## 3. 재시작

스킬은 **세션 시작 시**에만 등록되므로 설치 직후 새 세션이 필요하다.

| 런타임 | 방법 |
|---|---|
| Claude Code | 현재 세션 종료 (`/exit` 또는 창 닫기) → `claude` 재실행. 같은 디렉토리에서 새 세션 시작 시 설치된 스킬이 자동 로드됨 |
| Codex CLI | 안내 메시지 그대로 — `Restart Codex to pick up new skills.` Codex 종료 후 재실행 |

설치 확인 (재시작 후):

- Claude Code: `/plugin list` — `harness` 항목 확인
- Codex: `ls ${CODEX_HOME:-~/.codex}/skills/` — 3개 디렉토리 확인

## 4. 첫 실행 검증

새 세션에서 다음 중 하나를 입력하면 `korean-persona-harness` 스킬이 트리거되어야 한다.

**한국어 트리거 (모두 동작):**

```
한국어 페르소나로 5인 푸드테크 팀 만들어줘 — PO, 디자이너, 백엔드 개발자, CS 리드, 마케터
```
```
한국 SaaS 회사 영업팀 4인 페르소나 만들어줘
```
```
한국인 캐릭터로 UX 인터뷰 가상 패널 6명 구성해줘
```

**English 트리거** (description에 영어 키워드를 병기한 경우 — 별도 PR로 진행 중):

```
Make a Korean persona team for a food-tech startup (PO, designer, backend, CS, marketer).
```

기대 동작:

1. 시나리오 분석가가 역할 N개 식별 → `_workspace/korean-persona-harness/01_scenario.md` 생성
2. 퍼소나 큐레이터가 `korean-persona-search` 호출 → `02_personas.json`
3. 화법 어댑터가 한국 voice 입힘 → `03_voiced.json`
4. 정의 빌더가 에이전트 `.md` 작성 → `04_agents/*.md`
5. 다양성 QA 통과 후 `.claude/agents/` (Claude Code) 또는 `${CODEX_HOME:-~/.codex}/agents/` (Codex)에 복사

각 에이전트 정의 하단에 **출처 attribution (uuid + CC BY 4.0)**이 자동 삽입된다.

## 5. 트러블슈팅

| 증상 | 원인 | 해결 |
|---|---|---|
| 트리거해도 일반 `harness`가 동작 | 한국어 키워드가 약함 | "**한국어 페르소나**" / "**한국인 캐릭터**" 처럼 명시적으로 |
| `ModuleNotFoundError: huggingface_hub` | 의존성 미설치 | `pip install huggingface_hub pyarrow` |
| 검색 결과 0건 | 필터가 너무 좁음 (예: "30대 여성, 제주, 의사 5명") | 큐레이터가 자동으로 조건 완화 권장. 직접 호출 시 `--age-min`/`--age-max` 등을 늘릴 것 |
| 데이터셋 캐시를 찾을 수 없음 | 다운로드 미수행 | 2번 단계 실행 |
| 두 마켓플레이스 동시 추가 후 그림자 충돌 | `name`이 동일 | `/plugin marketplace remove`로 한쪽 제거 후 다시 시도 |
| Codex 설치 후에도 스킬이 안 보임 | 재시작 안 함 | Codex 종료 → 재실행 |

## 라이선스 / 출처

데이터셋: [nvidia/Nemotron-Personas-Korea](https://huggingface.co/datasets/nvidia/Nemotron-Personas-Korea) (CC BY 4.0). 생성된 모든 에이전트 정의 하단에 attribution 자동 삽입.
