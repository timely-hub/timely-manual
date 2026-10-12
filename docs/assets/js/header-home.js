// 상단 제목("타임리AI 사용설명서") 텍스트를 눌러도 로고와 똑같이 홈으로 이동하게 함.
// (mkdocs-material 기본값은 로고 아이콘만 링크, 제목 텍스트는 일반 <div> 라서 클릭해도 반응 없음)
function enableHeaderTitleHome() {
  var title = document.querySelector(".md-header__title");
  var logo = document.querySelector("a.md-header__button.md-logo, a.md-logo");
  if (!title || !logo || title.dataset.homeLinkAttached === "true") return;

  title.style.cursor = "pointer";
  title.addEventListener("click", function (e) {
    if (e.target.closest("a")) return; // 내부에 실제 링크가 있으면 그대로 둠
    var href = logo.getAttribute("href");
    if (href) window.location.href = href;
  });
  title.dataset.homeLinkAttached = "true";
}

document.addEventListener("DOMContentLoaded", enableHeaderTitleHome);
window.addEventListener("pageshow", enableHeaderTitleHome);
