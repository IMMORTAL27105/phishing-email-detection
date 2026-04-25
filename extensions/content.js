/*************************************************
 * Phishing Detection – Stable Hover Version
 *************************************************/

const BACKEND_URL = "http://127.0.0.1:8000/analyze-email";
const riskCache = new Map();
let tooltipLocked = false;

console.log("✅ Phish Hover Extension Loaded");

/* ---------------------------------------------
  TOOLTIP
--------------------------------------------- */

let tooltip = document.createElement("div");

tooltip.style.position = "fixed";
tooltip.style.zIndex = "9999";
tooltip.style.padding = "8px 10px";
tooltip.style.borderRadius = "6px";
tooltip.style.fontSize = "12px";
tooltip.style.background = "#1f2937";
tooltip.style.color = "#ffffff";
tooltip.style.boxShadow = "0 4px 12px rgba(0,0,0,0.3)";
tooltip.style.display = "none";
tooltip.style.maxWidth = "220px";
tooltip.style.lineHeight = "1.4";

document.body.appendChild(tooltip);

function showTooltip(x, y, html) {
  tooltip.innerHTML = html;
  tooltip.style.left = x + 40 + "px";
  tooltip.style.top = y + 40 + "px";
  tooltip.style.display = "block";
}

function hideTooltip() {
  tooltip.style.display = "none";
}

/* ---------------------------------------------
  BACKEND CALL
--------------------------------------------- */

function analyzeEmail(emailData, callback) {
  const key = `${emailData.sender}::${emailData.subject}`;

  if (riskCache.has(key)) {
    callback(riskCache.get(key));
    return;
  }

  fetch(BACKEND_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(emailData)
  })
    .then(res => res.json())
    .then(result => {
      console.log("=== MODULE 3 OUTPUT ===", result);
      riskCache.set(key, result);
      callback(result);
    })
    .catch(err => {
      console.warn("⚠️ Backend not running → using demo mode");

      // 🔥 DEMO FALLBACK (IMPORTANT FOR PPT)
      const fakeResult = {
        level: "danger",
        confidence: 0.82,
        signals: {
          content: ["Urgent language detected"],
          sender: ["Free email provider"],
          links: ["Contains external link"]
        }
      };

      callback(fakeResult);
    });
}

/* ---------------------------------------------
  HOVER HANDLER
--------------------------------------------- */

function attachHover(row) {
  if (row.dataset.phishHover === "true") return;
  row.dataset.phishHover = "true";

  row.addEventListener("mouseenter", (e) => {

    const bodyElement = row.querySelector("span.y2");
    const links = [];

    if (bodyElement) {
      const anchorTags = bodyElement.querySelectorAll("a");
      anchorTags.forEach(a => {
        if (a.href) links.push(a.href);
      });
    }

    const emailData = {
      subject: row.querySelector("span.bog")?.innerText || "",
      sender: row.querySelector("span.yP")?.innerText || "",
      body: bodyElement?.innerText || "",
      links: links
    };

    console.log("=== MODULE 1 OUTPUT ===", emailData);

    analyzeEmail(emailData, (result) => {

      const signals = result.signals || { content: [], sender: [], links: [] };

      let icon = "🟢";
      let title = "Safe";

      if (result.level === "warning") {
        icon = "🟡";
        title = "Caution";
      } else if (result.level === "danger") {
        icon = "🔴";
        title = "Phishing";
      }

      showTooltip(
        e.clientX,
        e.clientY,
        `
        <b>${icon} ${title}</b><br/>
        Confidence: ${result.confidence}<br/><br/>

        <div style="width:100%; background:#444; height:6px; border-radius:4px;">
          <div style="
            width:${result.confidence * 100}%;
            background:${result.level === "danger" ? "red" : result.level === "warning" ? "orange" : "green"};
            height:6px;
            border-radius:4px;">
          </div>
        </div>

        <br/>
        ${Object.values(signals)
          .flat()
          .map(s => `• ${s}`)
          .join("<br/>")}
        `
      );
    });
  });

  row.addEventListener("mouseleave", hideTooltip);
}

/* ---------------------------------------------
  OBSERVER
--------------------------------------------- */

function observeInbox() {
  const inbox = document.querySelector("div[role='main']");
  if (!inbox) return;

  const observer = new MutationObserver(() => {
    document.querySelectorAll("tr.zA").forEach(attachHover);
  });

  observer.observe(inbox, { childList: true, subtree: true });

  console.log("👀 Observer running");
}

/* ---------------------------------------------
  INIT
--------------------------------------------- */

function init() {
  const interval = setInterval(() => {
    const rows = document.querySelectorAll("tr.zA");
    if (rows.length > 0) {
      clearInterval(interval);
      rows.forEach(attachHover);
      observeInbox();
    }
  }, 1000);
}

init();