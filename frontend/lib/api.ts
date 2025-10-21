const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";




interface RequestOptions {
method?: string;
headers?: Record <string, string>;
body?: FormData | string;

}

class ApiService {
  private async request(endpoint: string, options: RequestOptions = {}) {
    const url = `${API_BASE_URL}${endpoint}`;

    try {
      const response = await fetch(url, {
        headers: {
          "Content-Type": "application/json",
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      return await response.json();
    } catch {
      throw new Error("Something went wrong");
    }
  }

  async uploadFile(file: File, sessionId: string) {
    const formData = new FormData();
    formData.append("file", file);
    formData.append("session_id", sessionId);

    return this.request("/upload", {
      method: "POST",
      headers: {},
      body: formData,
    });
  }

  async queryDocuments(query: string, sessionId: string, k: number = 3) {
    const formData = new FormData();
    formData.append("query", query);
    formData.append("session_id", sessionId);
    formData.append("k", k.toString());

    return this.request("/query", {
      method: "POST",
      headers: {},
      body: formData,
    });
  }

  async ping() {
    return this.request("/ping", {
      method: "POST",
      headers: {},
    });
  }

}

export const apiService = new ApiService();
