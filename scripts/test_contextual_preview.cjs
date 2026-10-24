"use strict";
// Host-side DOM contract. This is NOT an Android WebView rendering test.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");

const source = fs.readFileSync(path.join(__dirname, "wishcode-mobile.js"), "utf8");

class NodeMock {
  constructor(tag, attrs = {}) {
    this.tag = tag.toLowerCase();
    this.attrs = { ...attrs };
    this.nodeType = 1;
    this.children = [];
    this.parentElement = null;
    this.className = "";
    this.textContent = "";
    this.classList = { contains: token => this.className.split(" ").includes(token) };
  }
  set href(value) { this.attrs.href = value; }
  get href() { return this.attrs.href; }
  getAttribute(name) { return this.attrs[name] ?? null; }
  matches(sel) {
    if (sel === "a[href]") return this.tag === "a" && !!this.attrs.href;
    if (sel === "[data-chat-flow]") return Object.hasOwn(this.attrs, "data-chat-flow");
    return false;
  }
  closest(selector) {
    const parts = selector.split(",").map(x => x.trim());
    let current = this;
    while (current) {
      if (parts.some(part => {
        if (part === "[data-chat-flow]") return current.matches(part);
        if (part === ".wishcode-local-artifact") return current.classList.contains("wishcode-local-artifact");
        if (part === "[data-composer-card]") return Object.hasOwn(current.attrs, "data-composer-card");
        if (part === '[contenteditable="true"]') return current.attrs.contenteditable === "true";
        if (part === '[role="dialog"]') return current.attrs.role === "dialog";
        if (part === '[aria-modal="true"]') return current.attrs["aria-modal"] === "true";
        return current.tag === part;
      })) return current;
      current = current.parentElement;
    }
    return null;
  }
  append(...nodes) {
    for (const child of nodes) {
      child.parentElement = this;
      this.children.push(child);
    }
  }
  querySelectorAll(selector) {
    const matches = [];
    const onlyAnchors = selector === "a[href]";
    assert(onlyAnchors || selector === "[data-chat-flow] a[href]", selector);
    const visit = current => {
      for (const child of current.children) {
        if (child.matches("a[href]") && (onlyAnchors || child.closest("[data-chat-flow]"))) matches.push(child);
        visit(child);
      }
    };
    visit(this);
    return matches;
  }
  insertAdjacentElement(where, element) {
    assert.equal(where, "afterend");
    const parent = this.parentElement;
    assert(parent);
    element.parentElement = parent;
    parent.children.splice(parent.children.indexOf(this) + 1, 0, element);
  }
}

function run(entries) {
  const html = new NodeMock("html");
  const flow = new NodeMock("div", { "data-chat-flow": "turn" });
  html.append(flow);
  const base = [];
  for (const item of entries) {
    const parent = new NodeMock(item.code ? "pre" : "p");
    const link = new NodeMock("a", { href: item.href });
    parent.append(link);
    (item.outside ? html : flow).append(parent);
    base.push(link);
  }
  let observer;
  const doc = {
    documentElement: html,
    head: { appendChild() {} },
    readyState: "complete",
    getElementById() { return null; },
    createElement(tag) { return new NodeMock(tag); }
  };
  const win = {}; win.top = win;
  class Observer {
    constructor(callback) { this.callback = callback; observer = this; }
    observe() {}
  }
  vm.runInNewContext(source, { document: doc, window: win, MutationObserver: Observer, URL, WeakSet });
  return { html, flow, base, observer };
}

const test = run([
  { href: "http://127.0.0.1:4181/" },
  { href: "http://localhost:4222/index.html" },
  { href: "http://localhost:3081/" },
  { href: "https://example.com/" },
  { href: "http://127.0.0.1:4181/?secret=1" },
  { href: "http://user:pass@127.0.0.1:4181/" },
  { href: "http://127.0.0.1:4181/#token" },
  { href: "http://127.0.0.1:4181/", code: true },
  { href: "http://127.0.0.1:4181/", outside: true }
]);
let cards = test.flow.children.filter(x => x.classList.contains("wishcode-local-artifact"));
assert.equal(cards.length, 2);
assert.equal(cards[0].children[0].textContent, "本地网页链接 · 尚未验证服务");
assert.equal(cards[0].children[1].textContent, "预览网页");
assert.equal(cards[0].children[1].href, "http://127.0.0.1:4181/");
assert.equal(cards[0].children[1].target, "_self");
assert.equal(cards[1].children[1].href, "http://localhost:4222/index.html");
assert.equal(test.html.children.filter(x => x.classList.contains("wishcode-local-artifact")).length, 0);

// React may insert a new paragraph under an existing flow node after startup.
const p = new NodeMock("p");
const link = new NodeMock("a", { href: "http://127.0.0.1:5555/play" });
p.append(link);
test.flow.append(p);
test.observer.callback([{ addedNodes: [p] }]);
cards = test.flow.children.filter(x => x.classList.contains("wishcode-local-artifact"));
assert.equal(cards.length, 3);
assert.equal(cards[2].children[1].href, "http://127.0.0.1:5555/play");
test.observer.callback([{ addedNodes: [p] }]);
assert.equal(test.flow.children.filter(x => x.classList.contains("wishcode-local-artifact")).length, 3);
console.log("PASS: 3 contextual preview cards, 7 rejected candidates, idempotent React insertion");
