// 가이드(어드민·유저) 좌측 사이드바를 펼쳐두고, 우측 목차 스타일을 적용하며,
// 현재 페이지의 본문 목차(TOC)는 좌측 사이드바에서 접어 둡니다.
function initializeGuideNav() {
  const path = window.location.pathname;
  const isUser = /\/user\/getting-started\//.test(path);
  const isAdmin = /\/admin\//.test(path);
  if (!isUser && !isAdmin) return;

  // 우측 목차 리듬 스타일(공용)
  document.body.classList.add("timely-guide");

  // 활성 가이드의 최상위 섹션 펼치기 (유저=__nav_3, 어드민=__nav_2)
  const guideId = isUser ? "__nav_3" : "__nav_2";
  const guide = document.getElementById(guideId);
  if (guide) {
    guide.checked = true;
    const submenu = guide.parentElement.querySelector(":scope > nav.md-nav");
    if (submenu) submenu.setAttribute("aria-expanded", "true");
  }

  if (isUser) {
    // 유저 가이드: '타임리 AI' 하위 그룹은 열림/닫힘 상태를 탭 내에서 기억
    const timelyAi = document.getElementById("__nav_3_2");
    if (timelyAi) {
      const stateKey = "timely:user-guide:ai-expanded:" +
        window.location.pathname.split("/user/getting-started/")[0];
      let expanded = false;
      try {
        expanded = window.sessionStorage.getItem(stateKey) === "true";
      } catch (_) {}
      timelyAi.checked = expanded;
      const syncTimelyAi = function () {
        const submenu = timelyAi.parentElement.querySelector(":scope > nav.md-nav");
        if (submenu) submenu.setAttribute("aria-expanded", String(timelyAi.checked));
      };
      syncTimelyAi();
      if (timelyAi.dataset.navSyncAttached !== "true") {
        timelyAi.addEventListener("change", function () {
          try {
            window.sessionStorage.setItem(stateKey, String(timelyAi.checked));
          } catch (_) {}
          syncTimelyAi();
        });
        timelyAi.dataset.navSyncAttached = "true";
      }
    }
  } else if (isAdmin) {
    // 어드민 가이드: '시작하기' 하위 그룹은 기본 펼침
    const start = document.getElementById("__nav_2_1");
    if (start) {
      start.checked = true;
      const submenu = start.parentElement.querySelector(":scope > nav.md-nav");
      if (submenu) submenu.setAttribute("aria-expanded", "true");
    }
  }

  // 현재 페이지의 본문 목차는 좌측 사이드바에서 접어 둠
  const pageToc = document.getElementById("__toc");
  if (pageToc) {
    pageToc.checked = false;
    const submenu = pageToc.parentElement.querySelector(":scope > nav.md-nav");
    if (submenu) submenu.setAttribute("aria-expanded", "false");
  }
}

document.addEventListener("DOMContentLoaded", initializeGuideNav);
window.addEventListener("pageshow", initializeGuideNav);
