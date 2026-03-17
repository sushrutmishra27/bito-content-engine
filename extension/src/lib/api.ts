const DEFAULT_API_URL = "https://bito-content-engine-production.up.railway.app";

export interface InspirationPayload {
  title: string;
  url: string;
  content_markdown: string;
  note: string;
  category: string;
}

export interface ApiResponse {
  success: boolean;
  message?: string;
  error?: string;
}

async function getApiUrl(): Promise<string> {
  return new Promise((resolve) => {
    chrome.storage.sync.get({ apiUrl: DEFAULT_API_URL }, (result) => {
      resolve(result.apiUrl);
    });
  });
}

export async function sendInspiration(
  data: InspirationPayload
): Promise<ApiResponse> {
  const apiUrl = await getApiUrl();
  const endpoint = `${apiUrl}/api/inspirations`;

  const response = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(`API error (${response.status}): ${errorText}`);
  }

  return response.json();
}
