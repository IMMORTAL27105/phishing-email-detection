/*************************************************
 * Phishing Detection – Hover Tooltip Version
 * Gmail-safe, backend-connected, stable UI
 *************************************************/

const BACKEND_URL = "http://127.0.0.1:8000/analyze-email";
const riskCache = new Map();
let tooltipLocked = false;
let lastResult = null;

console.log("✅ Phish Hover Extension Loaded");

/* ---------------------------------------------
   TOOLTIP CREATION
--------------------------------------------- */

let tooltip = null;

function createTooltip() {
  tooltip = document.createElement("div");
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
}

createTooltip();

function showTooltip(x, y, html, lock = false) {
  tooltip.innerHTML = html;
  tooltip.style.left = x + 50 + "px";
  tooltip.style.top = y + 50 + "px";
  tooltip.style.display = "block";

  tooltipLocked = lock;
}

function hideTooltip() {
  if (tooltipLocked) return;
  tooltip.style.display = "none";
}

/* ---------------------------------------------
   BACKEND COMMUNICATION
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
      riskCache.set(key, result);
      callback(result);
    })
    .catch(err => {
      console.error("❌ Backend error:", err);
      callback({ level: "unknown", confidence: "N/A" });
    });
}

/* ---------------------------------------------
   HOVER HANDLER
--------------------------------------------- */

function attachHover(row) {
  if (row.dataset.phishHover === "true") return;
  row.dataset.phishHover = "true";

  row.addEventListener("mouseenter", (e) => {
    const emailData = {
      subject: row.querySelector("span.bog")?.innerText || "",
      sender: row.querySelector("span.yP")?.innerText || "",
      body: row.querySelector("span.y2")?.innerText || "",
      links: []
    };

    analyzeEmail(emailData, (result) => {
      let icon = "🟢";
      let title = "Looks Safe";

      if (result.level === "warning") {
        icon = "🟡";
        title = "Be Cautious";
      } else if (result.level === "danger") {
        icon = "🔴";
        title = "Potential Phishing";
      }

      showTooltip(
        e.clientX,
        e.clientY,
        `
        <b>${icon} ${title}</b><br/>
        <b>Confidence:</b> ${result.confidence}<br/><br/>
        <b>Why?</b><br/>
        ${Object.entries(result.signals)
          .map(([k, v]) => v.length ? `• ${v.join(", ")}` : "")
          .join("<br/>")}
        `
      );
    });
  });

  row.addEventListener("mouseleave", hideTooltip);
}

/* ---------------------------------------------
   OBSERVE GMAIL INBOX
--------------------------------------------- */

function observeInbox() {
  const inbox = document.querySelector("div[role='main']");
  if (!inbox) return;

  const observer = new MutationObserver(() => {
    document.querySelectorAll("tr.zA").forEach(attachHover);
  });

  observer.observe(inbox, { childList: true, subtree: true });

  console.log("👀 Hover observer attached");
}

/* ---------------------------------------------
   INIT
--------------------------------------------- */

function init() {
  const wait = setInterval(() => {
    const rows = document.querySelectorAll("tr.zA");
    if (rows.length > 0) {
      clearInterval(wait);
      rows.forEach(attachHover);
      observeInbox();
    }
  }, 1000);
}

init();