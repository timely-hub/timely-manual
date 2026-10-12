// Keep the user guide section visible and its page-level TOC closed.
function initializeUserGuideNav() {
  if (!/\/user\/getting-started\//.test(window.location.pathname)) return;

  // Scope right-hand TOC styling to user guide pages only.
  document.body.classList.add("timely-user-guide");

  const userGuide = document.getElementById("__nav_3");
  if (userGuide) {
    userGuide.checked = true;
    const submenu = userGuide.parentElement.querySelector(":scope > nav.md-nav");
    if (submenu) submenu.setAttribute("aria-expanded", "true");
  }

  // Start closed once, then keep the user's choice across pages in this tab.
  const timelyAi = document.getElementById("__nav_3_2");
  if (timelyAi) {
    const stateKey = "timely:user-guide:ai-expanded:" +
      window.location.pathname.split("/user/getting-started/")[0];
    let expanded = false;
    try {
      expanded = window.sessionStorage.getItem(stateKey) === "true";
    } catch (_) {
      // Storage may be unavailable; keep the native checkbox toggle usable.
    }
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
        } catch (_) {
          // A blocked storage API must not prevent opening or closing the menu.
        }
        syncTimelyAi();
      });
      timelyAi.dataset.navSyncAttached = "true";
    }
  }

  // Keep the current page's in-page heading list out of the primary sidebar.
  const pageToc = document.getElementById("__toc");
  if (pageToc) {
    pageToc.checked = false;
    const submenu = pageToc.parentElement.querySelector(":scope > nav.md-nav");
    if (submenu) submenu.setAttribute("aria-expanded", "false");
  }
}

document.addEventListener("DOMContentLoaded", initializeUserGuideNav);
// Browsers may restore checkbox state when returning to a cached page.
window.addEventListener("pageshow", initializeUserGuideNav);
