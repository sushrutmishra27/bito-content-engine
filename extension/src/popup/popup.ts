import { sendInspiration, InspirationPayload } from "../lib/api";

const pageTitleInput = document.getElementById("page-title") as HTMLInputElement;
const pageUrlInput = document.getElementById("page-url") as HTMLInputElement;
const noteTextarea = document.getElementById("note") as HTMLTextAreaElement;
const categorySelect = document.getElementById("category") as HTMLSelectElement;
const captureBtn = document.getElementById("capture-btn") as HTMLButtonElement;
const btnText = document.getElementById("btn-text") as HTMLSpanElement;
const btnSpinner = document.getElementById("btn-spinner") as HTMLSpanElement;
const formSection = document.getElementById("form-section") as HTMLDivElement;
const successSection = document.getElementById("success-section") as HTMLDivElement;
const errorSection = document.getElementById("error-section") as HTMLDivElement;
const errorMessage = document.getElementById("error-message") as HTMLParagraphElement;
const captureAnotherBtn = document.getElementById("capture-another") as HTMLButtonElement;
const retryBtn = document.getElementById("retry-btn") as HTMLButtonElement;

let extractedContent = "";

// Auto-fill page title and URL from active tab
async function loadPageInfo(): Promise<void> {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (tab) {
      pageTitleInput.value = tab.title || "";
      pageUrlInput.value = tab.url || "";
    }
  } catch (err) {
    console.error("Failed to get tab info:", err);
  }
}

// Extract content from the active tab's content script
async function extractContent(): Promise<string> {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage(
      { action: "getPageContent" },
      (response: { content?: string; error?: string } | undefined) => {
        if (chrome.runtime.lastError) {
          reject(new Error(chrome.runtime.lastError.message));
          return;
        }
        if (response?.error) {
          reject(new Error(response.error));
          return;
        }
        resolve(response?.content || "");
      }
    );
  });
}

function showForm(): void {
  formSection.classList.remove("hidden");
  successSection.classList.add("hidden");
  errorSection.classList.add("hidden");
}

function showSuccess(): void {
  formSection.classList.add("hidden");
  successSection.classList.remove("hidden");
  errorSection.classList.add("hidden");
}

function showError(msg: string): void {
  formSection.classList.add("hidden");
  successSection.classList.add("hidden");
  errorSection.classList.remove("hidden");
  errorMessage.textContent = msg;
}

function setLoading(loading: boolean): void {
  captureBtn.disabled = loading;
  btnText.textContent = loading ? "Capturing..." : "Capture";
  if (loading) {
    btnSpinner.classList.remove("hidden");
  } else {
    btnSpinner.classList.add("hidden");
  }
}

async function handleCapture(): Promise<void> {
  setLoading(true);

  try {
    // Extract page content
    extractedContent = await extractContent();

    const payload: InspirationPayload = {
      title: pageTitleInput.value,
      url: pageUrlInput.value,
      content: extractedContent,
      note: noteTextarea.value,
      category: categorySelect.value,
      capturedAt: new Date().toISOString(),
    };

    await sendInspiration(payload);
    showSuccess();
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error occurred";
    showError(message);
  } finally {
    setLoading(false);
  }
}

// Event listeners
captureBtn.addEventListener("click", handleCapture);

captureAnotherBtn.addEventListener("click", () => {
  noteTextarea.value = "";
  showForm();
  loadPageInfo();
});

retryBtn.addEventListener("click", () => {
  showForm();
});

// Initialize
loadPageInfo();
