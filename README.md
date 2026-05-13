# timely-manual

Timely AI 서비스 사용설명서 정적 사이트.

- 배포: GitHub Pages (브랜치: `master`, 경로: `/`)
- 진입점: [`index.html`](./index.html)

## 로컬에서 미리보기

별도 빌드 도구 없이 정적 HTML이므로 아무 정적 서버나 사용하면 됩니다.

```bash
# Python이 있을 때
python3 -m http.server 8000
# 또는 Node가 있을 때
npx --yes serve .
```

브라우저에서 `http://localhost:8000` 접속.

## GitHub Pages 활성화

1. GitHub 저장소 → **Settings** → **Pages**
2. **Source**: `Deploy from a branch`
3. **Branch**: `master` / `/ (root)` 선택 후 **Save**
4. 1~2분 후 `https://timely-hub.github.io/timely-manual/` 에서 확인

> `.nojekyll` 파일이 포함되어 있어 Jekyll 처리를 건너뜁니다.
