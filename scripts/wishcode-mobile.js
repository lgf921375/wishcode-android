/* WishCode V0.4: scoped narrow-screen resilience for the embedded DSH Web UI.
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
    '    width: 100%; max-width: 100%; overflow-x: clip; box-sizing: border-box;',
    '  }',
    '  [data-mobile-nav="frame"], [data-sidebar-right-panel] {',
    '    box-sizing: border-box; max-width: 100vw; min-width: 0 !important;',
    '  }',
    '  [data-mobile-nav="frame"] :is(main, section, article, form, header, footer),',
    '  [data-sidebar-right-panel] :is(main, section, article, form) {',
    '    box-sizing: border-box; min-width: 0; max-width: 100%;',
    '  }',
    '  [data-mobile-nav="frame"] :is(h1,h2,h3,p,li,label),',
    '  [role="dialog"] :is(h1,h2,h3,p,li,label),',
    '  [aria-modal="true"] :is(h1,h2,h3,p,li,label) {',
    '    overflow-wrap: anywhere;',
    '  }',
    '  :is([role="dialog"], [aria-modal="true"], dialog[open]) {',
    '    box-sizing: border-box; max-width: min(94vw, 620px) !important;',
    '    max-height: 88dvh !important; overflow-y: auto; overscroll-behavior: contain;',
    '  }',
    '  :is([role="dialog"], [aria-modal="true"], dialog[open])',
    '    :is(input, textarea, select, button) {',
    '    box-sizing: border-box; max-width: 100%; min-width: 0;',
    '  }',
    '  [data-composer-input], [class*="_composerSeat"] {',
    '    box-sizing: border-box; max-width: 100%; min-width: 0;',
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
})();
