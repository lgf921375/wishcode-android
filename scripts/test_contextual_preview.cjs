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
assert.doesNotMatch(source, /wishcode-local-artifact|previewCandidate|connectPreviewCards|MutationObserver/);
assert.doesNotMatch(source, /fetch\(|XMLHttpRequest|localStorage/);
console.log("PASS: retired preview, preserved ColorOS layout and model menu; no web requests");
