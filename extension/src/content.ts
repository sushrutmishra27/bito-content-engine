// Content script - injected on all pages

function createCaptureButton(): void {
  // Avoid duplicate buttons
  if (document.getElementById("bito-capture-btn")) return;

  const button = document.createElement("button");
  button.id = "bito-capture-btn";
  button.title = "Capture with Bito";
  button.innerHTML = `
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2L2 7L12 12L22 7L12 2Z" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M2 17L12 22L22 17" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
      <path d="M2 12L12 17L22 12" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
  `;

  button.addEventListener("click", () => {
    // Notify background to set badge - user should click the extension icon
    chrome.runtime.sendMessage({ action: "captureRequested" });
    // Brief visual feedback
    button.style.background = "#22c55e";
    setTimeout(() => {
      button.style.background = "#2563eb";
    }, 800);
  });

  document.body.appendChild(button);
}

// Selectors for elements to REMOVE before extraction (nav, sidebar, footer, etc.)
const NOISE_SELECTORS = [
  "nav",
  "header",
  "footer",
  "aside",
  "[role='navigation']",
  "[role='banner']",
  "[role='contentinfo']",
  "[role='complementary']",
  "[aria-label='Trending']",
  "[data-testid='sidebarColumn']",
  "[data-testid='primaryColumn'] > div:first-child", // Twitter top bar
  ".sidebar",
  ".nav",
  ".navigation",
  ".menu",
  ".footer",
  ".header",
  "#sidebar",
  "#nav",
  "#footer",
  "#header",
  ".trending",
  ".recommendations",
  "script",
  "style",
  "noscript",
  "iframe",
];

// Selectors for the MAIN content area (tried in order of specificity)
const CONTENT_SELECTORS = [
  "article",
  "[role='article']",
  "[data-testid='tweetText']",
  ".post-content",
  ".article-content",
  ".entry-content",
  ".post-body",
  "main",
  "[role='main']",
  "#content",
  ".content",
];

function extractPageContent(): {
  title: string;
  url: string;
  content: string;
} {
  const title = document.title;
  const url = location.href;

  // Strategy 1: Try to find the main content element
  for (const selector of CONTENT_SELECTORS) {
    const elements = document.querySelectorAll(selector);
    if (elements.length > 0) {
      // Collect text from all matching elements (e.g., multiple tweet texts)
      const texts: string[] = [];
      elements.forEach((el) => {
        const text = (el as HTMLElement).innerText?.trim();
        if (text && text.length > 20) {
          texts.push(text);
        }
      });
      const combined = texts.join("\n\n");
      if (combined.length > 50) {
        return { title, url, content: combined.substring(0, 50000) };
      }
    }
  }

  // Strategy 2: Clone the body and strip noise elements
  const clone = document.body.cloneNode(true) as HTMLElement;
  for (const selector of NOISE_SELECTORS) {
    clone.querySelectorAll(selector).forEach((el) => el.remove());
  }

  let content = clone.innerText || "";

  // Clean up: remove excessive whitespace/newlines
  content = content
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .join("\n");

  // Trim to 50000 chars
  if (content.length > 50000) {
    content = content.substring(0, 50000);
  }

  return { title, url, content };
}

// Listen for messages from background/popup
chrome.runtime.onMessage.addListener(
  (
    message: { action: string },
    _sender: chrome.runtime.MessageSender,
    sendResponse: (response: unknown) => void
  ) => {
    if (message.action === "extractContent") {
      const data = extractPageContent();
      sendResponse(data);
    }
  }
);

// Inject the capture button when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", createCaptureButton);
} else {
  createCaptureButton();
}
