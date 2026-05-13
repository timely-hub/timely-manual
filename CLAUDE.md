# timely-manual

Timely AI 서비스 **사용설명서** 사이트 (MkDocs Material 기반).

## 배포

- **호스팅**: GitHub Pages (저장소: `timely-hub/timely-manual`)
- **소스 모드**: Pages Settings → Source = **"GitHub Actions"**
- **공개 URL**: https://timely-hub.github.io/timely-manual/
- **빌드**: `.github/workflows/deploy.yml` 가 `master` 푸시마다 `mkdocs build` → Pages 업로드.
- 변경 후 `master` 푸시 = 보통 30–60초 내 라이브 반영.

## 디렉토리 구조

```
timely-manual/
├── docs/                            # 콘텐츠 (편집 대상)
│   ├── index.md                     # 홈 (랜딩)
│   ├── admin/                       # 어드민 트랙
│   │   ├── getting-started/         # 시작하기 (스페이스/유저/템플릿/크레딧)
│   │   └── reference/               # 기능 더보기
│   ├── user/                        # 유저 트랙
│   │   ├── getting-started/
│   │   └── reference/
│   ├── hallucination.md             # 참고: 할루시네이션 줄이기
│   └── assets/
│       ├── css/brand.css            # 브랜드 토큰 매핑
│       ├── img/favicon.{svg,ico}    # 브랜드 마크
│       └── images/<page-slug>/      # 페이지별 이미지 (imgNN.png 형식)
├── mkdocs.yml                       # 테마·nav 설정
├── requirements.txt                 # mkdocs-material 핀
├── .github/workflows/deploy.yml     # CI 배포 워크플로
├── scripts/
│   └── convert-notion.py            # Notion export → docs 변환 (1회용, 참고용 보존)
├── README.md                        # 로컬 미리보기 안내
└── CLAUDE.md                        # 이 파일
```

## 브랜드 디자인 시스템

- 단일 진실 원천: **`timely-gpt-integration/apps/frontend/app/themes/tokens.css`**
- 토큰을 mkdocs-material의 CSS 변수에 매핑한 파일이 `docs/assets/css/brand.css`.
- **새 hex 값을 brand.css에 직접 넣지 말 것** — 항상 tokens.css의 변수를 참조.
- Primary: `#5e0aff`. 폰트: Pretendard (mkdocs.yml에서 지정).

## 콘텐츠 작업

- MkDocs Material Markdown 문법:
  - 콜아웃: `!!! note "제목"` / `!!! tip` / `!!! warning` / `!!! danger` / `!!! info` / `!!! success`
  - 토글 (펼침/접힘): `??? question "질문"`
  - 표·코드블록·이미지: 표준 Markdown
- 페이지 추가 시 **`mkdocs.yml`의 `nav:` 트리에 등록**해야 사이드바에 나옴.
- 이미지는 `docs/assets/images/<page-slug>/`에 두고 상대경로 `../../assets/images/...`로 참조.
- 한국어 UI 기본. mkdocs.yml의 `language: ko` 유지.

## 로컬 미리보기

```bash
# 첫 실행만
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# 매번
.venv/bin/mkdocs serve   # → http://127.0.0.1:8000  (파일 저장하면 자동 리로드)

# 정적 빌드
.venv/bin/mkdocs build --site-dir _site
```

## 커밋 / 푸시

- 기본 브랜치: `master` (PR 베이스도 동일).
- `master` 푸시 = 곧 프로덕션. 큰 변경은 별도 브랜치에서 작업하고 PR로 머지 권장.

## 변환 스크립트 (`scripts/convert-notion.py`)

원본 Notion export는 변환 후 제거했음. 추후 원본을 다시 받아와 재변환할 일이 생기면:

1. Notion export(zip)를 `existing-guide/` 폴더에 풀고
2. `python3 scripts/convert-notion.py` 실행
3. **주의**: `docs/` 안의 변환된 MD는 **덮어쓰기 됨**. 직접 편집한 페이지가 있다면 먼저 백업.

스크립트가 처리하는 것:
- 폴더/파일명 슬러그화 (한글 → 영문 slug)
- 이미지 파일명 정리 (Notion-jamo 인코딩 → `imgNN.png`)
- `<aside>` 콜아웃 → MkDocs admonition (emoji → 종류)
- FAQ 토글 `- 질문\n    본문` → `??? question "..."`
- Notion 페이지 간 링크 (해시 ID) → 새 슬러그 경로
