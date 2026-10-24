/* WishCode V0.4: Pinyin-font-safe narrow-screen spacing for embedded DSH Web UI.
 * Runs only via upstream WebPageScripts.presentation in the authenticated
 * app WebView. Does not touch prompts, sessions, credentials or tool dispatch.
 */
(() => {
  if (window.top !== window || !document.documentElement) return;
  if (document.getElementById('wishcode-mobile-v04')) return;
  const style = document.createElement('style');
  style.id = 'wishcode-mobile-v04';
  style.textContent = [
    '@media screen and (max-width: 760px) {',
    '  html, body {',
    '    width: 100%; max-width: 100%; overflow-x: auto; box-sizing: border-box;',
    '  }',
    '  /* Our Free Model v2.5.9: its sticky nav covers content on narrow screens. */',
    '  .ofm_root .ofm_nav {',
    '    position: relative !important; top: auto !important; z-index: auto !important;',
    '    width: 100%; max-width: 100%; min-width: 0;',
    '  }',
    '  .ofm_root .ofm_navbrand {',
    '    white-space: normal !important; min-width: 0; overflow-wrap: break-word;',
    '  }',
    '  .ofm_root .ofm_tabs {',
    '    display: flex !important; flex-wrap: nowrap !important;',
    '    overflow-x: auto !important; overflow-y: hidden !important;',
    '    max-width: 100%; min-width: 0; overscroll-behavior-x: contain;',
    '    -webkit-overflow-scrolling: touch;',
    '  }',
    '  .ofm_root .ofm_tab {',
    '    white-space: nowrap !important; flex: 0 0 auto; min-height: 44px;',
    '  }',
    '  /* The sliding indicator is not scroll-aware: use tab background instead. */',
    '  .ofm_root .ofm_tabglider { display: none !important; }',
    '  .ofm_root .ofm_tab[data-on="true"] {',
    '    background: var(--dsw-alias-bg-layer-3, rgba(120,140,180,.15));',
    '  }',
    '  /* 0.2.1-rc.2 model picker is portaled under body, NOT the composer. */',
    '  body [class*="_7KE1Ra_menu"][role="group"] {',
    '    box-sizing: border-box; min-width: 0 !important;',
    '    max-width: min(94vw, 420px) !important;',
    '    max-height: min(48dvh, 420px) !important;',
    '    overflow: hidden !important;',
    '  }',
    '  body [class*="_7KE1Ra_menu"][role="group"] [class*="_7KE1Ra_groups"][role="menu"] {',
    '    min-height: 0 !important; max-height: 34dvh !important;',
    '    overflow-y: auto !important; overscroll-behavior: contain;',
    '    -webkit-overflow-scrolling: touch;',
    '  }',
    '  body [class*="_7KE1Ra_menu"][role="group"] [role="menuitemradio"] {',
    '    min-height: 44px; height: auto !important;',
    '    line-height: 1.65 !important; white-space: normal !important;',
    '    overflow-wrap: break-word;',
    '  }',
    '  /* Contextual artifact entry only near an actual rendered localhost link. */',
    '  .wishcode-local-artifact {',
    '    display: flex; flex-wrap: wrap; align-items: center;',
    '    gap: 8px; padding: 8px 10px; margin: 10px 0;',
    '    border: 1px solid var(--dsh-border-default, #d8dee9);',
    '    border-radius: 12px; max-width: 100%; box-sizing: border-box;',
    '  }',
    '  .wishcode-local-artifact-label {',
    '    font-size: 13px; line-height: 1.8; overflow-wrap: break-word;',
    '    flex: 1 1 120px; min-width: 0;',
    '  }',
    '  a.wishcode-local-artifact-open {',
    '    display: inline-flex; align-items: center; justify-content: center;',
    '    min-height: 44px; padding: 6px 12px; box-sizing: border-box;',
    '    border: 1px solid currentColor; border-radius: 10px;',
    '    line-height: 1.8; text-decoration: none; white-space: normal;',
    '  }',
    '  [data-mobile-nav="frame"], [data-sidebar-right-panel] {',
    '    box-sizing: border-box; max-width: 100vw; min-width: 0 !important;',
    '  }',
    '  [data-mobile-nav="frame"] :is(main, section, article, form, header, footer),',
    '  [data-sidebar-right-panel] :is(main, section, article, form) {',
    '    box-sizing: border-box; min-width: 0; max-width: 100%;',
    '  }',
    '  /* Keep ColorOS pinyin ruby/diacritics inside line boxes. */',
    '  [data-mobile-nav="frame"] :is(h1,h2,h3,p,li,label,button,[role="button"],[role="tab"]),',
    '  [role="dialog"] :is(h1,h2,h3,p,li,label,button,[role="button"]),',
    '  [aria-modal="true"] :is(h1,h2,h3,p,li,label,button,[role="button"]) {',
    '    line-height: 1.9 !important; overflow-wrap: break-word;',
    '    white-space: normal; min-width: 0; max-width: 100%;',
    '  }',
    '  :is([role="dialog"], [aria-modal="true"], dialog[open]) {',
    '    box-sizing: border-box; max-width: min(94vw, 620px) !important;',
    '    min-width: 0 !important; max-height: 85dvh !important;',
    '    overflow-y: auto; overflow-x: auto; overscroll-behavior: contain;',
    '  }',
    '  :is([role="dialog"], [aria-modal="true"], dialog[open])',
    '    :is(input, textarea, select, button) {',
    '    box-sizing: border-box; max-width: 100%; min-width: 0;',
    '  }',
    '  [data-composer-input], [class*="_composerSeat"] {',
    '    box-sizing: border-box; max-width: 100%; min-width: 0;',
    '  }',
    '  /* Avoid clipped text in settings rows and plugin-install confirmations. */',
    '  :is([role="dialog"], [aria-modal="true"], dialog[open]) :is(button,[role="button"]) {',
    '    min-height: 48px; height: auto !important;',
    '    white-space: normal !important; overflow-wrap: break-word;',
    '  }',
    '  :is([role="dialog"], [aria-modal="true"], dialog[open]) :is(input,textarea,select) {',
    '    max-width: 100%; min-width: 0; flex-shrink: 1;',
    '  }',
    '  [data-mobile-nav="frame"] :is(pre,table),',
    '  :is([role="dialog"], [aria-modal="true"]) :is(pre,table) {',
    '    max-width: 100%; overflow-x: auto;',
    '  }',
    '  [data-mobile-nav="frame"] img, [role="dialog"] img {',
    '    max-width: 100%; height: auto;',
    '  }',
    '}'
  ].join('\n');
  (document.head || document.documentElement).appendChild(style);

  // A link appearing in a conversation is a candidate, not proof that the model
  // created files or that the service is alive. The native preview independently
  // validates the current chat port, then fetches the page upon user action.
  function previewCandidate(raw) {
    if (typeof raw !== 'string' || raw.length > 2048 || raw !== raw.trim()
        || raw.includes('\\')) return null;
    try {
      const u = new URL(raw);
      if (u.protocol !== 'http:' ||
          (u.hostname !== '127.0.0.1' && u.hostname !== 'localhost') ||
          !u.port || +u.port < 1024 || +u.port > 65535 ||
          +u.port === 3081 || +u.port === 3090 ||
          u.username || u.password || u.search || u.hash) return null;
      return u.href;
    } catch (ignored) {
      return null;
    }
  }

  const decorated = new WeakSet();
  function decorate(link) {
    if (decorated.has(link)) return;
    decorated.add(link);
    if (!link.closest('[data-chat-flow]') ||
        link.closest('pre, code, [contenteditable="true"], [role="dialog"], [aria-modal="true"]') ||
        link.classList.contains('wishcode-local-artifact-open')) return;
    const href = previewCandidate(link.getAttribute('href') || '');
    if (!href) return;
    const parent = link.closest('p, li') || link.parentElement;
    if (!parent || parent.closest('.wishcode-local-artifact') ||
        parent.closest('[data-composer-card]')) return;
    // Text nodes are deliberately used instead of HTML/innerHTML, so no model
    // content is executable and no authentication values are ever copied.
    const box = document.createElement('div');
    box.className = 'wishcode-local-artifact';
    const label = document.createElement('span');
    label.className = 'wishcode-local-artifact-label';
    label.textContent = '本地网页链接 · 尚未验证服务';
    const button = document.createElement('a');
    button.className = 'wishcode-local-artifact-open';
    button.href = href;
    button.target = '_self';
    button.rel = 'noreferrer';
    button.textContent = '预览网页';
    box.append(label, button);
    parent.insertAdjacentElement('afterend', box);
  }

  function scanLinks(root) {
    if (!root || root.nodeType !== 1) return;
    if (root.matches('a[href]')) decorate(root);
    if (root.querySelectorAll) {
      // React usually inserts a <p> inside an existing flow container; its
      // [data-chat-flow] ancestor then lies outside this mutation subtree.
      const scope = root.closest('[data-chat-flow]');
      root.querySelectorAll(scope ? 'a[href]' : '[data-chat-flow] a[href]').forEach(decorate);
    }
  }
  function connectPreviewCards() {
    scanLinks(document.documentElement);
    const observer = new MutationObserver(records => {
      for (const record of records) {
        for (const node of record.addedNodes) scanLinks(node);
      }
    });
    observer.observe(document.documentElement, { childList: true, subtree: true });
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', connectPreviewCards, { once: true });
  } else {
    connectPreviewCards();
  }
})();
