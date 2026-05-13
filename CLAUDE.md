# timely-manual

Timely AI 서비스 **사용설명서** 사이트 (MkDocs Material 기반).

## 👤 작업자(사용자) 컨텍스트 — 먼저 읽을 것

> **이 저장소를 다루는 작업자는 일반적으로 개발자가 아닙니다.**
> 콘텐츠 담당자가 자연어로 지시를 주는 환경이라고 가정하고 행동하세요.

### 작업자 환경

- **OS**: 윈도우가 기본 (저장소 소유자는 맥). 스크립트·안내는 **윈도우를 우선** 가정.
- **사전 설치**: Claude Desktop 설치 시 Python·Node가 함께 설치됨 → `python` 명령은 PATH에 있다고 가정 가능.
- **편집기**: VS Code 가정 (README에 권장 명시). 메모장으로도 편집은 가능하지만 권장 X.
- **셸**: 윈도우 작업자는 보통 명령 프롬프트(cmd)를 안 씀. **GUI(더블 클릭)**로 동작하는 흐름이 가장 안전.

### 의사소통 원칙

- **한국어, 짧고 친근한 톤.** 전문용어(빌드, CI, 캐시, localStorage 등)를 써야 하면 **한 문장 안에 풀어서** 함께 설명.
- **작업자에게 CLI 명령을 시키지 말 것.** `mkdocs build`, `npm install`, `git push` 같은 명령을 작업자가 직접 칠 거라고 기대하지 말고 **Claude 본인이 실행**해서 결과만 보고.
- **선택지가 있는 결정은 AskUserQuestion으로.** "A안 / B안 / C안" 형태가 가장 잘 통함.
- 작업자가 모호하게 말하면 (예: "이상해", "안 보여") **추측 말고 라이브 화면을 직접 확인**한 뒤 무엇이 보이는지 보고하고 질문.

### 화면 vs 글자 — 검증 방법 구분

작업자는 **렌더링된 화면을 보고** 보고합니다. 소스 코드 기준이 아닙니다.
보고 받은 내용에 따라 검증 수단을 적절히 골라야 함:

| 작업자의 보고 유형 | 검증 방법 |
|---|---|
| "버튼이 안 눌려요", "글자가 까매요", "정렬이 이상해요", "공간이 너무 비어요" | 👁 **렌더링된 화면 확인** — Launch preview 패널(자동 미리보기), `_site/` 빌드 산출물, `curl` 라이브 URL, 또는 스크린샷 도구 |
| "오타가 있어요", "문장이 어색해요", "링크가 잘못된 페이지로 가요", "이 페이지 추가/삭제해요" | 📝 **소스 MD 확인** — `docs/**.md` 직접 읽기 |
| "이 변경 반영됐어요?" | 🌐 **라이브 사이트 확인** — `curl -sI https://timely-hub.github.io/timely-manual/<path>/` 등. 푸시 후 GitHub Actions 빌드(약 30–60초) 종료 전엔 반영 X |
| 디자인 변경 후 "여전히 그대로네" | 🤔 **localStorage / 브라우저 캐시** 의심. 시크릿 창 권유 또는 캐시 키 제거 안내 |

**작업 흐름 권장**: 디자인·레이아웃·콜아웃 같은 시각 변경은 **빌드해서 본 뒤** 보고하는 게 좋음. Claude가 직접 `_site/` 안의 HTML을 확인하거나 라이브 URL을 받아 검증하면 작업자의 왕복 시간이 줄어듦.

### 결과 공유 패턴

- **🚨 배포(push) 정책 — 반드시 지킬 것**
  작업이 완료되고 실제 배포를 하기 전에는 **작업자에게 "운영에 배포할까요?"라고 먼저 물어보고, 긍정의 대답이 왔을 때만 `git push`를 실행한다.** 로컬에서 `git commit` 까지는 무방하지만, `master`에 push 하는 순간 30~60초 내 라이브 사이트에 반영되므로 신중하게.
- 로컬 미리보기(`preview.sh`/`preview.bat`)로 충분히 확인할 수 있게 셋업돼 있음. 푸시 전에 작업자가 로컬에서 검수할 시간을 주는 것이 기본.
- 로컬에서만 빌드해 두고 작업자에게 "확인해 보세요"라고 끝내지 말 것. 작업자는 별도로 빌드 명령을 칠 수 없다고 가정 — `preview.sh`/`preview.bat`만 더블 클릭하면 된다고 안내.
- 큰 변경(여러 페이지 동시 수정, 구조 개편)은 todo 리스트로 단계 보이고 진행 상황 갱신.

---

## 배포

- **호스팅**: GitHub Pages (저장소: `timely-hub/timely-manual`)
- **소스 모드**: Pages Settings → Source = **"GitHub Actions"**
- **공개 URL**: https://timely-hub.github.io/timely-manual/
- **빌드**: `.github/workflows/deploy.yml` 가 `master` 푸시마다 `mkdocs build` → Pages 업로드.
- 변경 후 `master` 푸시 = 보통 30–60초 내 라이브 반영.
- 푸시 후 워크플로 상태는 `gh run list --repo timely-hub/timely-manual --workflow=deploy.yml --limit 1`로 확인. Claude가 직접 보고할 것.

## 디렉토리 구조

```
timely-manual/
├── docs/                            # 콘텐츠 (편집 대상)
│   ├── index.md                     # 홈 (랜딩 — 어드민/유저 CTA + 입문 가이드 카드)
│   ├── admin/                       # 어드민 트랙
│   │   ├── getting-started/         # 시작하기 (스페이스/유저/템플릿/크레딧)
│   │   └── reference/               # 기능 더보기
│   ├── user/                        # 유저 트랙
│   │   ├── getting-started/
│   │   └── reference/
│   ├── tutorials.md                 # 영상 튜토리얼 (YouTube)
│   ├── faq.md                       # 자주 묻는 질문
│   ├── hallucination.md             # 참고: 할루시네이션 줄이기
│   ├── app.md                       # 모바일 앱 (QR / 스토어)
│   ├── contact.md                   # 직접 문의 (카카오/전화/홈페이지)
│   ├── privacy.md                   # 데이터·개인정보 정책
│   └── assets/
│       ├── css/brand.css            # 브랜드 토큰 매핑
│       ├── img/favicon.{svg,ico}    # 브랜드 마크
│       └── images/<page-slug>/      # 페이지별 이미지 (imgNN.png 형식)
├── mkdocs.yml                       # 테마·nav 설정
├── requirements.txt                 # mkdocs-material 핀
├── .github/workflows/deploy.yml     # CI 배포 워크플로
├── scripts/
│   ├── convert-notion.py            # Notion export → docs 변환 (재사용 가능)
│   ├── cleanup-docs.py              # 콜아웃 타이틀 / 이미지 alt 잡음 정리 (재사용)
│   └── compact-empty-admonitions.py # 빈 본문 콜아웃 → 컴팩트 blockquote 변환 (재사용)
├── preview.sh                       # macOS/Linux 로컬 미리보기 (셸)
├── preview.bat                      # Windows 로컬 미리보기 (더블 클릭)
├── README.md                        # 로컬 미리보기·편집 안내 (작업자용)
└── CLAUDE.md                        # 이 파일 (Claude 세션용)
```

## 브랜드 디자인 시스템

- 단일 진실 원천: **`timely-gpt-integration/apps/frontend/app/themes/tokens.css`**
- 토큰을 mkdocs-material의 CSS 변수에 매핑한 파일이 `docs/assets/css/brand.css`.
- **새 hex 값을 brand.css에 직접 넣지 말 것** — 항상 tokens.css의 변수를 참조.
- Primary: `#5e0aff`. 폰트: Pretendard (mkdocs.yml에서 지정).
- **라이트 모드 전용.** 다크(slate)는 의도적으로 뺐음 — 본 서비스가 라이트 톤이라 통일. 다크 필요해지면 mkdocs.yml의 palette에 slate 추가 + brand.css에 `[data-md-color-scheme="slate"]` 블록 복구.

## 콘텐츠 작업

### Markdown 문법 — 자주 쓰는 것

| 용도 | 문법 | 노트 |
|---|---|---|
| 콜아웃 (큰 박스) | `!!! note "제목"` (+ 4-space 들여쓰기 본문) | 종류: note / tip / warning / danger / info / success |
| 토글 (펼침/접힘) | `??? question "질문"` (+ 본문) | FAQ에 적합 |
| 짧은 한 줄 강조 | `> 💡 **메시지**` | 컴팩트한 blockquote — 본문 없는 callout 자리에 사용 |
| 그리드 카드 | `<div class="grid cards" markdown>` … `</div>` | 홈·랜딩 페이지에서 활용 |
| 아이콘 | `:material-account:` | mkdocs-material 아이콘 셋 |
| 표·코드·이미지 | 표준 Markdown |  |

### 페이지 관리 룰

- **새 페이지 추가 시 `mkdocs.yml`의 `nav:` 트리에 반드시 등록**. 등록 안 하면 사이드바에 안 보임.
- 이미지는 `docs/assets/images/<page-slug>/`에 두고 상대경로 `../../assets/images/...`로 참조.
- 한국어 UI 기본. mkdocs.yml의 `language: ko` 유지.
- 페이지 안 깨진 링크는 빌드 시 `WARNING` 또는 `INFO`로 출력 — 푸시 전 로컬 빌드 권장.

### 잡음 정리 스크립트

작업자가 콘텐츠 일괄로 받아오는 경우(Notion export 등) 다음 순서로 돌리면 톤이 빠르게 정돈됨:

```bash
python3 scripts/convert-notion.py            # Notion → docs/ 변환 (있을 때)
python3 scripts/cleanup-docs.py              # 콜아웃 emoji-only 타이틀, 파일명 alt 제거
python3 scripts/compact-empty-admonitions.py # 빈 본문 callout → 컴팩트 blockquote
```

## 로컬 미리보기

저장소 루트에 OS별 진입 스크립트가 있음. 작업자가 직접 띄워서 변경을 즉시 확인할 수 있게 해줌.

| OS | 명령 |
|---|---|
| 윈도우 | `preview.bat` 더블 클릭 (또는 cmd에서 실행) |
| 맥/리눅스 | `./preview.sh` |

스크립트 동작:
1. `.venv` 없으면 자동으로 만들고 `requirements.txt` 설치 (첫 실행 1~2분)
2. 8000번 포트가 비어 있으면 사용, 아니면 8001, 8002… 다음 빈 포트 자동 선택
3. `mkdocs serve` 실행 — `docs/`·`mkdocs.yml` 변경 시 브라우저 자동 새로고침
4. (윈도우만) 브라우저 자동으로 열림

### Claude가 직접 빌드/검증할 때

작업자에게 띄우라고 하지 말고 **Claude가 직접** 실행해 결과를 확인:

```bash
# 정적 빌드 (산출물: _site/)
.venv/bin/mkdocs build --site-dir _site

# 서버 (변경 자동 리로드)
.venv/bin/mkdocs serve
```

`_site/` 안의 HTML/CSS를 직접 읽으면 렌더링 결과 확인 가능. 라이브 사이트 검증은 `curl https://timely-hub.github.io/timely-manual/<path>/`.

## 커밋 / 푸시

- 기본 브랜치: `master` (PR 베이스도 동일).
- `master` 푸시 = 곧 프로덕션.
- **🚨 푸시 전 반드시 작업자 확인.** 위쪽 "결과 공유 패턴"의 배포 정책 참고. 임의로 푸시하지 말 것.
- **푸시 후**: Actions 워크플로 성공 여부 확인 → 라이브 URL 한 번 더 검증 → 작업자에게 보고 (이게 표준 흐름).

## 변환·정리 스크립트 사용

- `scripts/convert-notion.py` — Notion zip export를 받았을 때만 사용. `existing-guide/`에 압축 풀고 실행 → `docs/` 안의 변환된 MD는 **덮어쓰기 됨**. 직접 편집한 페이지가 있다면 먼저 백업.
- `scripts/cleanup-docs.py` — emoji-only 콜아웃 타이틀, 파일명만 들어간 이미지 alt 일괄 정리. 안전.
- `scripts/compact-empty-admonitions.py` — Notion에서 본문 없는 강조 박스를 한 줄짜리 blockquote로 변환. 안전.

모두 멱등(여러 번 돌려도 같은 결과). 안전하지 않은 변경이 필요해지면 새 스크립트로 추가하고 이 목록에도 등록.
