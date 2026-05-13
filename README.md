# timely-manual

Timely AI 서비스 **사용설명서** 사이트. 라이브: <https://timely-hub.github.io/timely-manual/>

---

## 🖥 로컬에서 미리보기

수정한 내용을 GitHub에 올리기 전에 내 컴퓨터에서 먼저 확인할 수 있어요.
파일을 저장하면 브라우저가 자동으로 새로고침됩니다.

### 윈도우

저장소 폴더에서 **`preview.bat`** 을 더블 클릭하세요.

처음 실행할 때 한 번만 자동으로 환경 설치가 일어나고(1–2분), 이후엔 즉시 서버가 뜹니다.
브라우저는 자동으로 열려요. 종료는 검은 창에서 `Ctrl + C` 또는 그 창을 닫으면 됩니다.

> Python이 설치돼 있어야 합니다. **Claude Desktop 설치 시 함께 설치되니** 보통 별도 작업은 필요 없어요.
> 안 뜨면 [python.org](https://www.python.org/downloads/)에서 Python 3.10 이상을 받아 설치하세요.

### 맥 / 리눅스

터미널에서:

```bash
./preview.sh
```

처음 실행할 땐 가상환경(`.venv`)을 자동으로 만들고 의존성을 설치합니다.

---

## ✏️ 콘텐츠 편집

- 문서 파일은 모두 `docs/` 폴더 안에 있습니다 (`.md` 파일).
- 일반적인 Markdown 문법을 씁니다. mkdocs-material 추가 문법(콜아웃, 토글, 카드 등)은 `CLAUDE.md`에 정리돼 있어요.
- 새 페이지를 추가했다면 **`mkdocs.yml`** 의 `nav:` 트리에 등록해야 사이드바에 보입니다.
- 이미지는 `docs/assets/images/<페이지-슬러그>/` 에 넣고 `![](../../assets/images/...)` 형태로 참조.

편집기 추천: [Visual Studio Code](https://code.visualstudio.com/) (무료, 한글 OK, Markdown 미리보기 내장).

---

## 🚀 변경사항 반영

`master` 브랜치에 푸시하면 약 30~60초 뒤 라이브 사이트에 자동 반영됩니다.

작업이 완료되고 실제 배포를 하기 전에는 운영에 배포할지 먼저 물어보고 긍정의 대답이 왔을때만,
배포 푸시를 실행 합니다.

```bash
git add .
git commit -m "메시지"
git push
```

배포 진행 상황: <https://github.com/timely-hub/timely-manual/actions>

---

## 📁 폴더 구조

```
timely-manual/
├── docs/                       # 콘텐츠 (이걸 편집)
│   ├── index.md                # 홈
│   ├── admin/                  # 어드민 가이드
│   ├── user/                   # 유저 가이드
│   ├── faq.md
│   ├── tutorials.md, app.md, contact.md, privacy.md
│   └── assets/                 # 이미지·CSS
├── mkdocs.yml                  # 사이드바·테마 설정
├── preview.bat / preview.sh    # 로컬 미리보기
├── README.md / CLAUDE.md       # 안내 문서
└── scripts/                    # Notion 임포트·정리 스크립트
```
