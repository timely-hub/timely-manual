// 인쇄(= PDF로 저장) 시 접혀 있는 토글(details/FAQ)을 모두 펼쳐
// 내용이 PDF에서 빠지지 않도록 합니다. 인쇄가 끝나면 원래대로 되돌립니다.
window.addEventListener("beforeprint", function () {
  document.querySelectorAll("details:not([open])").forEach(function (d) {
    d.setAttribute("data-print-was-closed", "1");
    d.setAttribute("open", "");
  });
});
window.addEventListener("afterprint", function () {
  document.querySelectorAll('details[data-print-was-closed="1"]').forEach(function (d) {
    d.removeAttribute("open");
    d.removeAttribute("data-print-was-closed");
  });
});
