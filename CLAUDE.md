# timely-manual

Timely AI 서비스 **사용설명서** 정적 사이트.

## 배포

- **호스팅**: GitHub Pages (저장소: `timely-hub/timely-manual`)
- **소스**: `Deploy from a branch` → 브랜치 `master`, 경로 `/ (root)`
- **공개 URL**: https://timely-hub.github.io/timely-manual/
- 빌드 도구 없음. `master` 에 푸시된 HTML/CSS가 그대로 서빙됨.
- 루트의 `.nojekyll` 파일로 Jekyll 처리는 건너뜀.

## 디렉토리 구조

```
timely-manual/
├── index.html          # 진입점 (홈)
├── pages/              # 서브 페이지들 (각자 1개의 HTML)
│   ├── getting-started.html
│   └── features.html
├── assets/
│   └── style.css       # 모든 페이지가 공유하는 단일 스타일시트
├── .nojekyll
├── README.md           # 사용자/협업자용 — 로컬 미리보기·Pages 활성화 안내
└── CLAUDE.md           # 이 파일
```

## 컨텐츠 정책

- **현재 페이지들은 골격(placeholder)임.** 실제 사용설명서 내용은 아직 비어 있음.
- 사용자가 추후 **PDF 또는 Notion 링크 형태의 원본 자료**를 제공할 예정. 그 자료를 바탕으로 페이지를 채우게 됨.
- 따라서 지금의 섹션 구성(시작하기 / 기능 / FAQ)은 **확정이 아님** — 원본 자료가 들어오면 목차부터 다시 잡을 수 있음.

## 작업 규칙

- 정적 HTML이므로 빌드 단계 없음. 파일을 편집해 `master` 에 푸시하면 곧 반영됨.
- 페이지 간 링크는 **상대경로**로 작성:
  - `index.html` → `pages/foo.html`: `./pages/foo.html`
  - `pages/foo.html` → `pages/bar.html`: `./bar.html`
  - `pages/foo.html` → 홈: `../index.html`
  - `pages/foo.html` → CSS: `../assets/style.css`
- 새 페이지를 추가할 때는 **헤더·푸터·네비를 기존 페이지에서 복사해 일관성** 유지. 페이지 수가 늘어 중복이 부담스러워지면 그때 JS include 또는 SSG 도입을 검토.
- 한국어 UI 기본. `<html lang="ko">` 유지.

## 로컬 미리보기

```bash
python3 -m http.server 8000   # → http://localhost:8000
# 또는
npx --yes serve .
```

## 커밋 / 푸시

- 기본 브랜치는 `master` (PR 베이스도 동일).
- `master` 푸시 = 곧 프로덕션. 큰 변경은 별도 브랜치에서 작업하고 PR로 머지하는 흐름을 권장.
