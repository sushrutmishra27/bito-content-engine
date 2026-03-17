interface ExtractedContent {
  title: string;
  url: string;
  content: string;
}

interface ExtractRequest {
  action: "extractContent";
}

interface ExtractResponse {
  action: "contentExtracted";
  data: ExtractedContent;
}

type Message = ExtractRequest | ExtractResponse | { action: string; [key: string]: unknown };

chrome.runtime.onMessage.addListener(
  (
    message: Message,
    _sender: chrome.runtime.MessageSender,
    sendResponse: (response: unknown) => void
  ) => {
    if (message.action === "getPageContent") {
      // Get the active tab and request content extraction from content script
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const tab = tabs[0];
        if (!tab?.id) {
          sendResponse({ error: "No active tab found" });
          return;
        }

        chrome.tabs.sendMessage(
          tab.id,
          { action: "extractContent" } as ExtractRequest,
          (response: ExtractedContent | undefined) => {
            if (chrome.runtime.lastError) {
              sendResponse({
                error: chrome.runtime.lastError.message,
              });
              return;
            }
            sendResponse(response);
          }
        );
      });

      // Return true to indicate async response
      return true;
    }

    if (message.action === "captureRequested") {
      // Set badge to prompt user to click the extension icon
      chrome.action.setBadgeText({ text: "!" });
      chrome.action.setBadgeBackgroundColor({ color: "#22c55e" });
      // Clear badge after 3 seconds
      setTimeout(() => {
        chrome.action.setBadgeText({ text: "" });
      }, 3000);
    }
  }
);
