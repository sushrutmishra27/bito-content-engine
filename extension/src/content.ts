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

// Extract page content when requested
function extractPageContent(): {
  title: string;
  url: string;
  content: string;
} {
  const title = document.title;
  const url = location.href;
  let content = document.body.innerText || "";

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
