from __future__ import annotations

import panel as pn

from toscana_gui.paths import REPO_ROOT

APP_TITLE = "ToScaNA GUI"
LOGO_PATH = REPO_ROOT / "assets" / "institut-laue-langevin.png"

SCROLL_PRESERVE_JS = r"""
(() => {
  if (window.__toscana_scroll_fix_installed) return;
  window.__toscana_scroll_fix_installed = true;

  let lastScrollY = window.scrollY || 0;
  let lastInteractionAt = 0;
  let lockUntil = 0;
  let wrappedScrollApis = false;

  const scrollToMethodAnchor = () => {
    const anchor = document.getElementById("toscana-bg-method-anchor");
    if (!anchor) return false;
    const rect = anchor.getBoundingClientRect();
    if (!rect) return false;
    const top = (window.scrollY || 0) + rect.top;
    const target = Math.max(0, top - 90);
    window.scrollTo(0, target);
    return true;
  };

  const rememberScroll = () => {
    lastScrollY = window.scrollY || 0;
    lastInteractionAt = Date.now();
    lockUntil = lastInteractionAt + 1200;
  };

  const shouldBlockScrollToTop = (targetY) => {
    const now = Date.now();
    if (now > lockUntil) return false;
    if (lastScrollY <= 100) return false;
    if (targetY == null) return false;
    return Number(targetY) <= 30;
  };

  const wrapScrollApisOnce = () => {
    if (wrappedScrollApis) return;
    wrappedScrollApis = true;

    try {
      const originalScrollTo = window.scrollTo ? window.scrollTo.bind(window) : null;
      if (originalScrollTo) {
        window.scrollTo = function(x, y) {
          if (shouldBlockScrollToTop(y)) {
            return originalScrollTo(x, lastScrollY);
          }
          return originalScrollTo(x, y);
        };
      }
    } catch (e) {}

    try {
      const originalIntoView = Element.prototype.scrollIntoView;
      if (originalIntoView) {
        Element.prototype.scrollIntoView = function() {
          if (shouldBlockScrollToTop(0)) return;
          return originalIntoView.apply(this, arguments);
        };
      }
    } catch (e) {}
  };

  const restoreIfJumped = () => {
    const now = Date.now();
    if (now - lastInteractionAt > 12000) return;

    const currentY = window.scrollY || 0;
    if (lastScrollY <= 100) return;
    if (currentY >= 30) return;

    // If the page height collapsed (browser clamps scrollY to 0), at least keep
    // the "Background Subtraction Method" area visible.
    if (currentY <= 2) {
      if (scrollToMethodAnchor()) return;
    }

    const maxScrollY = Math.max(
      0,
      (document.documentElement && document.documentElement.scrollHeight ? document.documentElement.scrollHeight : 0) - (window.innerHeight || 0)
    );
    if (lastScrollY > maxScrollY + 40) return;

    window.scrollTo(0, lastScrollY);
  };

  const scheduleRestore = () => {
    setTimeout(restoreIfJumped, 0);
    setTimeout(restoreIfJumped, 60);
    setTimeout(restoreIfJumped, 220);
    setTimeout(restoreIfJumped, 600);
    setTimeout(restoreIfJumped, 1200);
    setTimeout(restoreIfJumped, 1800);
    setTimeout(restoreIfJumped, 2600);
    setTimeout(restoreIfJumped, 3600);
    setTimeout(restoreIfJumped, 5000);
    setTimeout(restoreIfJumped, 8000);
    setTimeout(restoreIfJumped, 11000);
  };

  const normalizeButtons = () => {
    const buttons = document.querySelectorAll(".bk-root button, .pn-wrapper button");
    for (const btn of buttons) {
      const t = (btn.getAttribute("type") || "").toLowerCase();
      if (!t || t === "submit") btn.setAttribute("type", "button");
    }
  };

  document.addEventListener("pointerdown", rememberScroll, true);
  document.addEventListener("touchstart", rememberScroll, true);
  document.addEventListener("wheel", rememberScroll, {capture: true, passive: true});
  window.addEventListener("scroll", () => {
    lastScrollY = window.scrollY || 0;
  }, {passive: true});

  // Guard against accidental form submits inside Panel/Bokeh templates.
  document.addEventListener("click", (ev) => {
    wrapScrollApisOnce();
    rememberScroll();
    const btn = ev.target && ev.target.closest ? ev.target.closest("button") : null;
    if (btn) {
      const t = (btn.getAttribute("type") || "").toLowerCase();
      const inPanelRoot = btn.closest && (btn.closest(".bk-root") || btn.closest(".pn-wrapper"));
      if (inPanelRoot && (!t || t === "submit")) ev.preventDefault();
    }
    scheduleRestore();
  }, true);

  document.addEventListener("change", () => {
    wrapScrollApisOnce();
    rememberScroll();
    scheduleRestore();
  }, true);

  document.addEventListener("submit", (ev) => {
    const root = ev.target && ev.target.closest ? (ev.target.closest(".bk-root") || ev.target.closest(".pn-wrapper")) : null;
    if (root) {
      ev.preventDefault();
      scheduleRestore();
    }
  }, true);

  normalizeButtons();
  const observer = new MutationObserver(() => {
    normalizeButtons();
    scheduleRestore();
  });
  observer.observe(document.documentElement, {subtree: true, childList: true});
})();
"""

BUTTON_CSS = """
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

html, body, .bk-root, .bk, .pn-wrapper, .pn-loading {
  font-family: 'IBM Plex Sans', sans-serif;
}

h1, h2, h3, h4, h5, h6, .markdown, .bk-btn, .bk-input {
  font-family: 'IBM Plex Sans', sans-serif;
}

.bk-btn {
  min-height: 56px;
  font-size: 1.05rem;
  font-weight: 600;
  border-radius: 10px;
}

.toscana-toast-stack {
  position: fixed;
  right: 24px;
  top: 24px;
  width: min(360px, calc(100vw - 48px));
  z-index: 1000;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.toscana-toast {
  width: 100%;
  color: #ffffff;
  border-radius: 12px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.18);
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.18);
}

.toscana-toast--success { background: rgba(21, 84, 63, 0.96); }
.toscana-toast--info { background: rgba(11, 111, 164, 0.96); }
.toscana-toast--warning { background: rgba(161, 98, 7, 0.96); }
.toscana-toast--error { background: rgba(153, 27, 27, 0.96); }

.toscana-toast__row {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  padding: 12px 12px 10px 14px;
}

.toscana-toast__body {
  flex: 1 1 auto;
  font-size: 0.98rem;
  line-height: 1.4;
  overflow-wrap: anywhere;
}

.toscana-toast__close.bk-btn {
  min-height: 32px;
  height: 32px;
  width: 32px;
  padding: 0;
  border-radius: 10px;
  font-size: 1.1rem;
  line-height: 1;
  background: rgba(255, 255, 255, 0.16);
  color: #ffffff;
  border: 1px solid rgba(255,255,255,0.22);
}

.toscana-toast__close.bk-btn:hover {
  background: rgba(255, 255, 255, 0.22);
}

.toscana-toast__bar {
  height: 4px;
  background: rgba(255, 255, 255, 0.92);
  transform-origin: left center;
  animation: toscana-toast-progress 8s linear forwards;
}

.toscana-toast--persistent .toscana-toast__bar {
  display: none;
}

@keyframes toscana-toast-progress {
  from { transform: scaleX(1); }
  to { transform: scaleX(0); }
}

.toscana-hovercard {
  position: relative;
  display: inline-flex;
  align-items: center;
}

.toscana-hovercard__icon {
  width: 34px;
  height: 34px;
  border-radius: 10px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  background: rgba(0,0,0,0.06);
  border: 1px solid rgba(0,0,0,0.10);
  cursor: default;
  user-select: none;
}

.toscana-hovercard__panel {
  position: absolute;
  top: 42px;
  width: min(520px, calc(100vw - 120px));
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid rgba(0,0,0,0.10);
  box-shadow: 0 18px 44px rgba(0,0,0,0.14);
  color: rgba(0,0,0,0.86);
  display: none;
  z-index: 1001;
}

.toscana-hovercard--open-right .toscana-hovercard__panel {
  left: 0;
  right: auto;
}

.toscana-hovercard--open-left .toscana-hovercard__panel {
  right: 0;
  left: auto;
}

.toscana-hovercard:hover .toscana-hovercard__panel {
  display: block;
}

.toscana-hovercard__panel code {
  overflow-wrap: anywhere;
}

.toscana-overflow-visible {
  overflow: visible !important;
}

.toscana-overflow-visible > div {
  overflow: visible !important;
}

.toscana-overflow-visible .bk-card,
.toscana-overflow-visible .bk-card-body {
  overflow: visible !important;
}
"""

def _install_scroll_preserver() -> None:
    try:
        pn.state.execute(SCROLL_PRESERVE_JS)
    except Exception:
        return


def configure_panel() -> None:
    pn.extension("plotly", raw_css=[BUTTON_CSS], notifications=True)
    if pn.state.notifications is not None:
        pn.state.notifications.position = "top-right"
        pn.state.notifications.max_notifications = 2
    pn.state.onload(_install_scroll_preserver)
