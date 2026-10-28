import { spawn } from "node:child_process";
import fs from "node:fs";
import http from "node:http";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const host = "127.0.0.1";
const port = 8765;
const url = `http://${host}:${port}/`;
const outputDir = path.join(root, "tmp", "qa");
fs.mkdirSync(outputDir, { recursive: true });

const chromeCandidates = [
  process.env.CHROME_PATH,
  "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe",
  "/usr/bin/google-chrome",
  "/usr/bin/chromium",
].filter(Boolean);
const chromePath = chromeCandidates.find((candidate) => fs.existsSync(candidate));
if (!chromePath) {
  throw new Error("Chrome or Edge was not found. Set CHROME_PATH and retry.");
}

const sleep = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

function httpGet(targetUrl) {
  return new Promise((resolve, reject) => {
    const request = http.get(targetUrl, (response) => {
      let body = "";
      response.setEncoding("utf8");
      response.on("data", (chunk) => {
        body += chunk;
      });
      response.on("end", () => {
        resolve({ statusCode: response.statusCode, body });
      });
    });
    request.setTimeout(2_000, () => request.destroy(new Error("HTTP request timed out")));
    request.on("error", reject);
  });
}

async function waitForUrl(targetUrl, attempts = 80) {
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    try {
      const response = await httpGet(targetUrl);
      if (response.statusCode >= 200 && response.statusCode < 300) return response;
    } catch {
      // Retry while the local process starts.
    }
    await sleep(100);
  }
  throw new Error(`Timed out waiting for ${targetUrl}`);
}

class CdpClient {
  constructor(socket) {
    this.socket = socket;
    this.nextId = 1;
    this.pending = new Map();
    this.events = new Map();
    socket.addEventListener("message", (event) => {
      const message = JSON.parse(event.data);
      if (message.id && this.pending.has(message.id)) {
        const { resolve, reject } = this.pending.get(message.id);
        this.pending.delete(message.id);
        if (message.error) reject(new Error(message.error.message));
        else resolve(message.result);
        return;
      }
      const handlers = this.events.get(message.method) || [];
      handlers.forEach((handler) => handler(message.params));
    });
  }

  send(method, params = {}) {
    const id = this.nextId++;
    return new Promise((resolve, reject) => {
      this.pending.set(id, { resolve, reject });
      this.socket.send(JSON.stringify({ id, method, params }));
      setTimeout(() => {
        if (!this.pending.has(id)) return;
        this.pending.delete(id);
        reject(new Error(`CDP timeout: ${method}`));
      }, 10_000);
    });
  }

  on(method, handler) {
    const handlers = this.events.get(method) || [];
    handlers.push(handler);
    this.events.set(method, handlers);
  }
}

const server = spawn(
  "python",
  ["-m", "http.server", String(port), "--bind", host],
  { cwd: root, stdio: "ignore", windowsHide: true }
);

const profileDir = fs.mkdtempSync(path.join(os.tmpdir(), "ds-tutorial-chrome-"));
const chrome = spawn(
  chromePath,
  [
    "--headless=new",
    "--disable-gpu",
    "--disable-extensions",
    "--disable-background-networking",
    "--no-first-run",
    "--no-default-browser-check",
    "--remote-debugging-port=9223",
    `--user-data-dir=${profileDir}`,
    url,
  ],
  { stdio: "ignore", windowsHide: true }
);

let socket;
try {
  await waitForUrl(url);
  await waitForUrl("http://127.0.0.1:9223/json/version");
  const targetsResponse = await httpGet("http://127.0.0.1:9223/json/list");
  const targets = JSON.parse(targetsResponse.body);
  const target = targets.find((item) => item.type === "page");
  if (!target) throw new Error("No Chrome page target found.");

  socket = new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve, reject) => {
    socket.addEventListener("open", resolve, { once: true });
    socket.addEventListener("error", reject, { once: true });
  });

  const cdp = new CdpClient(socket);
  const browserErrors = [];
  cdp.on("Runtime.exceptionThrown", (event) => browserErrors.push(event.exceptionDetails.text));
  cdp.on("Log.entryAdded", (event) => {
    if (event.entry.level === "error") browserErrors.push(event.entry.text);
  });
  await cdp.send("Page.enable");
  await cdp.send("Runtime.enable");
  await cdp.send("Log.enable");

  const results = [];
  const pages = [
    { name: "tutorial", pathname: "", kind: "tutorial" },
    { name: "customer-churn", pathname: "cases/customer-churn/", kind: "notebook" },
    { name: "house-price", pathname: "cases/house-price/", kind: "notebook" },
    { name: "demand-forecast", pathname: "cases/demand-forecast/", kind: "notebook" },
  ];
  const viewports = [
    { name: "desktop", width: 1440, height: 1000, mobile: false },
    { name: "tablet", width: 768, height: 900, mobile: true },
    { name: "mobile", width: 390, height: 844, mobile: true },
  ];

  for (const page of pages) {
    const pageUrl = new URL(page.pathname, url).toString();
    for (const viewport of viewports) {
      await cdp.send("Emulation.setDeviceMetricsOverride", {
        width: viewport.width,
        height: viewport.height,
        deviceScaleFactor: 1,
        mobile: viewport.mobile,
      });
      await cdp.send("Page.navigate", { url: pageUrl });
      await sleep(750);

      const evaluation = await cdp.send("Runtime.evaluate", {
        returnByValue: true,
        awaitPromise: true,
        expression: `(() => {
          const missingMetrics = [...document.querySelectorAll("[data-result]")]
            .filter((node) => !node.textContent.trim() || node.textContent.trim() === "—")
            .map((node) => node.dataset.result);
          const brokenImages = [...document.images]
            .filter((image) => !image.complete || image.naturalWidth === 0)
            .map((image) => image.getAttribute("src"));
          const missingAnchors = [...document.querySelectorAll('a[href^="#"]')]
            .filter((anchor) => anchor.hash && !document.querySelector(anchor.hash))
            .map((anchor) => anchor.getAttribute("href"));
          const ids = [...document.querySelectorAll("[id]")].map((node) => node.id);
          const duplicateIds = [...new Set(ids.filter((id, index) => ids.indexOf(id) !== index))];
          const imageLayouts = [...document.images].map((image) => {
            const rect = image.getBoundingClientRect();
            return {
              alt: image.alt,
              width: Math.round(rect.width),
              height: Math.round(rect.height),
            };
          });
          const diagramWidths = [...document.querySelectorAll(".diagram-figure img")]
            .map((image) => Math.round(image.getBoundingClientRect().width));
          const modelCallout = document.querySelector("#modeling .callout-no-icon");
          const modelCalloutRect = modelCallout?.getBoundingClientRect();
          const modelCalloutContentRect = modelCallout?.firstElementChild?.getBoundingClientRect();
          const menu = document.querySelector("#menu-button");
          return {
            title: document.title,
            lang: document.documentElement.lang,
            scrollWidth: document.documentElement.scrollWidth,
            clientWidth: document.documentElement.clientWidth,
            missingMetrics,
            brokenImages,
            missingAnchors,
            duplicateIds,
            imageLayouts,
            diagramWidths,
            modelCalloutWidth: Math.round(modelCalloutRect?.width || 0),
            modelCalloutContentInset: Math.round(
              (modelCalloutContentRect?.left || 0) - (modelCalloutRect?.left || 0),
            ),
            sectionCount: document.querySelectorAll("main section[id]").length,
            h1Count: document.querySelectorAll("h1").length,
            notebookCells: document.querySelectorAll(".notebook-document .cell").length,
            artifactCount: document.querySelectorAll("[data-artifact]").length,
            exerciseCount: document.querySelectorAll(".exercise").length,
            diagramCount: document.querySelectorAll(".figure-panel img").length,
            menuVisible: Boolean(menu) && getComputedStyle(menu).display !== "none",
          };
        })()`,
      });
      const metrics = evaluation.result.value;
      const label = `${page.name}/${viewport.name}`;

      if (metrics.lang !== "en") {
        throw new Error(`${label}: expected English page language`);
      }
      if (metrics.scrollWidth > metrics.clientWidth + 1) {
        throw new Error(`${label}: horizontal overflow (${metrics.scrollWidth}px > ${metrics.clientWidth}px)`);
      }
      if (metrics.missingMetrics.length) {
        throw new Error(`${label}: unresolved metrics: ${metrics.missingMetrics.join(", ")}`);
      }
      if (metrics.brokenImages.length) {
        throw new Error(`${label}: broken images: ${metrics.brokenImages.join(", ")}`);
      }
      if (metrics.missingAnchors.length) {
        throw new Error(`${label}: missing anchors: ${metrics.missingAnchors.join(", ")}`);
      }
      if (metrics.duplicateIds.length) {
        throw new Error(`${label}: duplicate ids: ${metrics.duplicateIds.join(", ")}`);
      }
      if (metrics.h1Count !== 1) {
        throw new Error(`${label}: expected exactly one h1, found ${metrics.h1Count}`);
      }
      if (page.kind === "tutorial" && metrics.sectionCount !== 9) {
        throw new Error(`${label}: expected 9 tutorial sections, found ${metrics.sectionCount}`);
      }
      if (
        page.kind === "tutorial" &&
        (metrics.artifactCount !== 6 || metrics.exerciseCount !== 6 || metrics.diagramCount < 8)
      ) {
        throw new Error(`${label}: incomplete teaching structure`);
      }
      if (
        page.kind === "tutorial" &&
        (metrics.diagramWidths.length !== 5 || metrics.diagramWidths.some((width) => width < 740))
      ) {
        throw new Error(`${label}: explanatory diagrams are below the readable width`);
      }
      const minimumCalloutWidth = viewport.name === "mobile" ? 280 : 500;
      if (
        page.kind === "tutorial" &&
        (metrics.modelCalloutWidth < minimumCalloutWidth || metrics.modelCalloutContentInset > 30)
      ) {
        throw new Error(`${label}: model callout layout is broken`);
      }
      if (page.kind === "notebook" && metrics.notebookCells < 5) {
        throw new Error(`${label}: notebook content did not render`);
      }
      if (page.kind === "notebook") {
        const minimumChartWidth = viewport.name === "mobile" ? 280 : viewport.name === "tablet" ? 600 : 700;
        const narrowImages = metrics.imageLayouts.filter((image) => image.width < minimumChartWidth);
        if (!metrics.imageLayouts.length || narrowImages.length) {
          throw new Error(
            `${label}: notebook visualizations are too narrow: ${JSON.stringify(narrowImages)}`,
          );
        }
      }

      if (page.kind === "tutorial" && viewport.name === "mobile") {
        const menuCheck = await cdp.send("Runtime.evaluate", {
          returnByValue: true,
          awaitPromise: true,
          expression: `(async () => {
            const button = document.querySelector("#menu-button");
            button.click();
            await new Promise((resolve) => setTimeout(resolve, 280));
            const opened = document.body.classList.contains("nav-open");
            const sidebarLeft = document.querySelector("#course-nav").getBoundingClientRect().left;
            button.click();
            await new Promise((resolve) => setTimeout(resolve, 280));
            return {
              opened,
              closed: !document.body.classList.contains("nav-open"),
              sidebarReachable: sidebarLeft >= -1 && sidebarLeft < window.innerWidth,
            };
          })()`,
        });
        const menuMetrics = menuCheck.result.value;
        if (!menuMetrics.opened || !menuMetrics.closed || !menuMetrics.sidebarReachable) {
          throw new Error(
            `Mobile navigation did not open and close correctly: ${JSON.stringify(menuMetrics)}`,
          );
        }
      }

      if (page.kind === "tutorial" && viewport.name === "desktop") {
        const artifactCheck = await cdp.send("Runtime.evaluate", {
          returnByValue: true,
          expression: `(() => {
            const box = document.querySelector("[data-artifact]");
            box.click();
            const state = document.querySelector("#artifact-progress-count").textContent;
            localStorage.removeItem("ds-workflow-artifacts-v1");
            box.click();
            return state;
          })()`,
        });
        if (!/1 of 6 complete/.test(artifactCheck.result.value)) {
          throw new Error("Artifact progress did not update.");
        }
      }

      const screenshot = await cdp.send("Page.captureScreenshot", {
        format: "png",
        captureBeyondViewport: false,
      });
      const screenshotPath = path.join(outputDir, `${page.name}-${viewport.name}.png`);
      fs.writeFileSync(screenshotPath, Buffer.from(screenshot.data, "base64"));
      results.push({ page: page.name, viewport, metrics, screenshotPath });
    }
  }

  if (browserErrors.length) {
    throw new Error(`Browser errors: ${browserErrors.join(" | ")}`);
  }
  console.log(JSON.stringify(results, null, 2));
} finally {
  socket?.close();
  chrome.kill();
  server.kill();
}
