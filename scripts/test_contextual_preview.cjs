"use strict";
// Regression for the user-requested retirement of the limited localhost preview.
// This tests the mobile script only, not Android WebView or Godot.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(path.join(__dirname, "wishcode-mobile.js"), "utf8");
const injected = [];
const document = {
  documentElement: {},
  head: { appendChild(element) { injected.push(element); } },
  getElementById() { return null; },
  createElement(tag) {
    assert.equal(tag, "style");
    return { id: "", textContent: "" };
  }
};
const window = {};
window.top = window;
vm.runInNewContext(source, {
  window,
  document,
  MutationObserver: class {
    constructor() { throw new Error("preview message scanning must remain disabled"); }
  }
});

assert.equal(injected.length, 1);
assert.match(injected[0].textContent, /max-height: min\(48dvh, 420px\)/);
assert.match(injected[0].textContent, /ofm_root/);
assert.match(injected[0].textContent, /data-plugin-settings/);
assert.match(injected[0].textContent, /data-dsh-plugin-settings/);
assert.match(injected[0].textContent, /@media \(max-width: 560px\)/);
assert.match(injected[0].textContent, /grid-template-columns: minmax\(0, 1fr\)/);
assert.match(injected[0].textContent, /overflow-x: auto/);
assert.match(injected[0].textContent, /line-height: 1\.85/);
assert.doesNotMatch(injected[0].textContent, /font-family:/);
assert.doesNotMatch(source, /wishcode-local-artifact|previewCandidate|connectPreviewCards|MutationObserver/);
assert.doesNotMatch(source, /fetch\(|XMLHttpRequest|localStorage/);
console.log("PASS: plugin settings responsive and ColorOS font preserved; no preview injection or web requests");
