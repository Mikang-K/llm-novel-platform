# LLM Novel Platform — 개발·학습 로드맵

> 최종 업데이트: 2026-10-20  
> 목적: Linux·Docker 기반으로 실제 배포·운영 가능한 LLM 소설 작성 플랫폼을 구현하면서 백엔드, 네트워크, 데이터베이스, 인프라, LLMOps를 학습한다.

## 0. 운영 원칙

- **구현 우선:** 작동하는 최소 기능을 먼저 만들고, 개념은 막히거나 설계 결정을 내려야 할 때 깊게 학습한다.
- **하나의 프로젝트를 점진적으로 고도화:** 일회성 예제보다 기존 코드에 기능을 누적한다.
- **완료 기준은 동작 검증:** 파일 작성이나 패키지 설치만으로 완료 처리하지 않는다.
- **작은 단위의 Git 커밋:** 코드, 설정 예제, 테스트를 버전 관리한다. `.env`, 비밀번호, 모델 가중치, 생성 데이터는 별도 관리한다.
- **코딩테스트는 별도 학습 트랙:** 알고리즘 문제 해결력과 서비스 설계·구현력을 구분해 훈련한다.
- **과도한 선행 설계 지양:** 필요해질 때 Router/Service/Repository, 큐, Kubernetes 등을 도입한다.

## 1. 최종 서비스 목표

사용자가 소설 프로젝트를 만들고, 등장인물·세계관·장·장면을 관리하며, LLM을 통해 초안을 생성·수정하는 웹 서비스.

### 사용자 기능 목표

1. 소설 프로젝트 생성·조회·수정·삭제
2. 챕터·장면 작성 및 버전 관리
3. 등장인물·세계관·설정집(Lore) 관리
4. 프롬프트·이전 문맥·설정을 반영한 LLM 텍스트 생성
5. 생성 작업 상태 확인, 실패 처리, 재시도
6. 생성 결과 편집·저장 및 이력 조회
7. 사용자 인증·권한 관리(후속 단계)

### 목표 아키텍처(점진적 도입)

```text
Browser / Frontend
        |
   HTTPS / Reverse Proxy
        |
     FastAPI ---------------- PostgreSQL
        |                          |
    Job Queue / Redis         소설·설정·이력
        |
     LLM Worker
        |
  Model Provider API / vLLM
        |
       GPU

Linux + Docker Compose → 모니터링/CI/CD → 필요 시 Kubernetes
```

> 로컬 개발 초기에는 FastAPI를 WSL에서 실행하고 PostgreSQL만 Docker에서 실행한다. 이후 백엔드도 컨테이너화한다. 로컬 GPU 및 모델 크기 제약에 따라 초기에는 외부 LLM API 또는 소형 모델을 선택한다.

## 2. 전체 페이즈 요약

| Phase | 주제 | 구현 결과물 / 완료 기준 | 상태 |
|---|---|---|---|
| 0 | 프로젝트 초기화 | WSL, uv, Python, GitHub SSH 연결 | **완료** |
| 1 | FastAPI / HTTP | `/health`, `/novels` 생성·조회, 오류·검증 처리 | **완료 (메모리 기반)** |
| 2 | Docker 기초 | Docker Engine 연결, 이미지·컨테이너 실행 및 상태 확인 | **완료 (기초)** |
| 3 | PostgreSQL 영속성 | Docker DB, SQLAlchemy, 생성·조회 DB 저장, 재시작 후 데이터 유지 | **진행 중** |
| 4 | API 구조화 / DB 관리 | Router·Service·Repository 분리, Alembic, CRUD 및 테스트 | 예정 |
| 5 | 소설 도메인 확장 | Novel·Chapter·Scene·Character·World Setting 모델과 API | 예정 |
| 6 | 첫 LLM 연동 | 프롬프트 구성, 모델 호출, 생성 결과 DB 저장 | 예정 |
| 7 | 비동기 생성 | Redis·Queue·Worker, Job 상태·실패·재시도 | 예정 |
| 8 | Docker Compose 통합 | 백엔드·DB·Redis·Worker 실행환경 통합 | 예정 |
| 9 | Linux 서버 배포 | Reverse Proxy, HTTPS, 설정·비밀값, 운영 로그, 백업 | 예정 |
| 10 | LLMOps 고도화 | 모델 서빙(vLLM 등), GPU, 프롬프트 버전·평가·추적·메트릭 | 예정 |
| 11 | 운영 자동화 | CI/CD, 자동 테스트, 관측성, 장애 대응 | 예정 |
| 12 | Kubernetes 확장 | Pod·Service·Ingress·PVC·GPU 리소스, 배포·복구 | 선택/후속 |

**페이즈는 학습·구현 단위이며 반드시 엄격한 순서일 필요는 없다.** 예를 들어 간단한 자동 테스트는 Phase 4부터 도입하고 이후 계속 확장한다.

## 3. 지금까지 실제로 확인한 진행 내역

### Phase 0 — 완료

- WSL2 Ubuntu 26.04.1 LTS 확인
- 시스템 Python 3.14.4와 프로젝트 Python 3.12.14 분리
- uv 설치, `.python-version`, `.venv`, `pyproject.toml`, `uv.lock` 구성
- PATH, `source`, 가상환경 활성화, 실행 파일 검색 경로 확인
- `.gitignore` 작성 방향 정리 (`.venv`, `.env`, 캐시·로그 제외)
- GitHub 저장소 `Mikang-K/llm-novel-platform`에 SSH 인증 및 `main → origin/main` push 성공

### Phase 1 — 완료 (메모리 기반)

- `GET /health` 구현 및 HTTP 200 확인
- `POST /novels` 구현, Pydantic `NovelCreate` 입력 검증
- `Field(min_length=1, max_length=100)` 적용
- `description: str | None = None` 적용
- `field_validator(mode="before")`로 제목 앞뒤 공백 제거
- 422(JSON 문법/필드 검증), 404(없는 ID), 405(허용되지 않은 메서드) 확인
- `GET /novels/{novel_id}` 구현
- Python 딕셔너리 저장과 서버 재시작 후 데이터 소실 확인
- Uvicorn, 프로세스, PID, TCP listening socket, HTTP 헤더·응답 확인

### Phase 2 — 완료 (기초)

- Docker Desktop + WSL2 통합 및 Docker CLI/Engine 통신 성공
- Unix socket `/var/run/docker.sock`와 접근 권한 문제 확인
- `hello-world` 이미지 pull 및 컨테이너 실행 성공
- `ubuntu:24.04` 컨테이너 실행, PID namespace 확인
- 컨테이너 내부 Bash PID 1 / Docker 호스트 관점 PID 642 확인
- `docker ps`와 `docker ps -a`를 통해 실행/종료 상태 차이 확인
- **미확인:** 컨테이너 파일 유지·삭제 실험, Volume 실습은 생략하고 실제 DB 구성에서 학습하기로 함

### Phase 3 — 진행 중

- PostgreSQL 17을 Docker Compose로 실행하는 구성 제안
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, 포트, named volume, healthcheck 설계
- SQLAlchemy 및 Psycopg 연동 코드 작성 방향 제시
- `ModuleNotFoundError: sqlalchemy` 발생 → 의존성 설치 필요 안내
- `.env` + `python-dotenv` 로딩 방식 및 `URL.create()` 설정 방식 학습
- `os.environ[...]`과 `os.getenv(..., default)`의 차이 확인
- **아직 확인되지 않음:** 컨테이너 healthy 여부, DB 실제 연결 성공, 테이블 생성, `POST /novels` DB 저장, 서버 재시작 후 조회 성공

## 4. 현재 코드 구조 (목표/작업 중 구조)

```text
llm-novel-platform/
├── .gitignore
├── .python-version
├── .env                 # 비밀값, Git 제외
├── .env.example         # 비밀값 없는 설정 템플릿(추가 예정)
├── .venv/               # Git 제외
├── compose.yaml         # PostgreSQL 등
├── pyproject.toml
├── uv.lock
├── README.md
└── src/
    └── llm_novel_platform/
        ├── __init__.py
        ├── main.py        # FastAPI, 라우트
        ├── database.py    # SQLAlchemy 엔진·세션
        └── models.py      # Novel ORM 모델
```

> 위 구조는 대화에서 작성·제안된 작업 구조를 합친 것이며, 실제 파일 존재 여부는 로컬 저장소에서 확인해야 한다.

## 5. 다음 실행 체크리스트 — Phase 3 완료하기

- [ ] `docker compose ps`에서 PostgreSQL 실행·health 확인
- [ ] `.env` 파일과 `.gitignore` 확인; 비밀번호 Git 미추적 확인
- [ ] `uv add sqlalchemy "psycopg[binary]" python-dotenv` 실행/설치 확인
- [ ] `database.py`에서 `.env` 로드 후 `URL.create()`로 연결 설정
- [ ] `models.py`에 `Novel` 테이블 모델 정의
- [ ] 개발 단계에서 테이블 생성 확인 (`create_all`; 이후 Alembic으로 교체)
- [ ] FastAPI 실행 성공 및 DB 연결 오류 없음 확인
- [ ] `POST /novels`로 DB에 저장, 201 반환
- [ ] `GET /novels/{id}`로 같은 데이터 조회
- [ ] Uvicorn 재시작 후 데이터 유지 확인
- [ ] PostgreSQL 컨테이너 재시작 후 데이터 유지 확인
- [ ] 변경 내용 커밋·push (비밀값 제외)

### 바로 실행할 점검 명령

```bash
cd ~/projects/llm-novel-platform
docker compose ps
uv pip show sqlalchemy
uv pip show psycopg
uv pip show python-dotenv
git status --short
git check-ignore .env
```

문제가 있으면 **실제 오류 메시지의 마지막 예외와 발생 파일/줄**부터 확인한다. DB 연결 오류라면 패키지 누락 → 환경변수 → 컨테이너 상태 → 포트 → 인증 순으로 점검한다.

## 6. 후속 페이즈별 구현 상세

### Phase 4 — 백엔드 구조화 및 품질
- `schemas/` (입출력 모델), `api/routers/`, `services/`, `repositories/`, `db/` 등으로 역할 분리
- Alembic 마이그레이션 초기화 및 테이블 변경 추적
- 생성/조회/수정/삭제, 예외 처리, 트랜잭션 관리
- pytest 기반 API·DB 테스트, 테스트 DB 분리
- **완료 기준:** CRUD와 자동 테스트 통과, 스키마 변경을 마이그레이션으로 재현

### Phase 5 — 소설 도메인
- Novel, Chapter, Scene, Character, WorldSetting, Lore 데이터 모델 설계
- 소설별 챕터 순서, 설정 참조, 수정 이력 관리
- 최소 프론트엔드 화면 또는 API 문서 기반 사용 흐름 완성
- **완료 기준:** 소설 생성부터 챕터·설정 관리까지 DB에 저장·조회 가능

### Phase 6 — 첫 LLM 생성
- 모델 호출 인터페이스 정의 (API 제공자/로컬 모델 교체 가능)
- 등장인물·세계관·이전 장면을 조합하는 Prompt Builder
- 생성 파라미터와 프롬프트 버전, 토큰 사용량·지연시간 기록
- 생성 결과를 Chapter/Scene 또는 Generation 기록에 저장
- **완료 기준:** 소설 문맥을 반영한 초안 생성·저장·재조회

### Phase 7 — 비동기 작업
- 생성 요청 즉시 Job ID 반환
- Redis 및 Worker 도입, `queued/running/succeeded/failed` 상태
- 재시도·타임아웃·중복 실행·동시성 제한 정책
- `GET /jobs/{id}` 조회, 필요 시 SSE/WebSocket 진행상황 전달
- **완료 기준:** 긴 LLM 요청 중 API가 블로킹되지 않고 실패·재시도 상태 추적 가능

### Phase 8 — 컨테이너 통합
- Backend Dockerfile 작성 및 이미지 빌드
- Compose로 backend, postgres, redis, worker 실행
- 네트워크·서비스 이름 DNS, Volume, healthcheck, 환경변수 분리
- **완료 기준:** 새 개발환경에서 문서대로 실행해 동일한 기능 재현

### Phase 9 — 실제 Linux 배포
- SSH, 방화벽, 도메인, Reverse Proxy, HTTPS/TLS
- 비밀정보 관리, 로그, DB 백업·복구, 서비스 재시작 정책
- **완료 기준:** 외부 접속 가능한 테스트 배포 및 장애·복구 절차 검증

### Phase 10 — LLMOps
- 모델 선택, 서빙 방식(vLLM 등), GPU 사용량·메모리 확인
- 프롬프트/모델 버전 관리, 품질 평가, 생성 추적·비용·성능 측정
- 소형 로컬 모델과 외부 API의 차이 비교
- **완료 기준:** 모델 변경 및 생성 품질·성능을 측정 가능한 형태로 운영

### Phase 11 — 운영 자동화
- GitHub Actions 기반 lint/test/build/deploy 파이프라인
- 메트릭, 로그, tracing, 알림 및 대표 장애 시나리오 검증
- **완료 기준:** 변경 사항 테스트 및 배포 절차 자동화, 기본 장애 감지 가능

### Phase 12 — Kubernetes (선택)
- Compose와 K8s 개념 매핑
- Deployment, Service, Ingress, ConfigMap/Secret, PVC, Job, GPU 자원
- **완료 기준:** 테스트 클러스터에 배포하고 재시작·스케일링·스토리지 검증

## 7. 별도 학습 트랙

- **네트워크/통신:** IP·Port·TCP·DNS·HTTP·TLS·Gateway·Reverse Proxy·Ingress. 매번 실제 요청 경로와 연결해서 학습.
- **Linux:** 프로세스·권한·파일시스템·systemd·로그·네트워크·쉘. 운영 문제를 만날 때 실습.
- **의료 IT:** HIS/EMR/OCS/RIS/PACS, DICOM, HL7/FHIR. 본 프로젝트와 분리된 업무 이해 트랙으로 유지.
- **코딩테스트:** 자료구조·알고리즘·문제 해결 연습. 프로젝트 개발과 별도 루틴.

## 8. 세션을 이어갈 때 사용할 상태 요약

**현재 위치:** Phase 3, PostgreSQL 영속성 구현 중.  
**마지막 학습 내용:** `.env` → `load_dotenv()` → `os.environ`/`os.getenv()` → `URL.create()` → SQLAlchemy Engine의 데이터 흐름.  
**다음 행동:** PostgreSQL 컨테이너와 Python 의존성 확인 → FastAPI DB 연결 오류 해결 → DB 기반 생성·조회 및 재시작 영속성 테스트.  
**진행 스타일:** 설명은 핵심만, 실행·검증 위주로 빠르게 진행. 필요할 때 개념을 다시 깊게 설명.

---

### 진행 기록 템플릿

```markdown
#### YYYY-MM-DD — Phase N
- 구현:
- 검증 결과:
- 발생한 문제/해결:
- 커밋:
- 다음 작업:
```
