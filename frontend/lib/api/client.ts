import { useStore } from "../../store/useStore";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface FetchOptions extends RequestInit {
  skipAuth?: boolean;
}

export async function fetchWithAuth(endpoint: string, options: FetchOptions = {}): Promise<any> {
  const { token, refreshToken, login, logout } = useStore.getState();
  
  const headers = new Headers(options.headers || {});
  if (!options.skipAuth && token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  
  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  const url = `${API_BASE}${endpoint}`;
  let response = await fetch(url, { ...options, headers });

  // Handle Token Expiration (401 Unauthorized)
  if (response.status === 401 && !options.skipAuth && refreshToken) {
    try {
      // Attempt silent refresh
      const refreshRes = await fetch(`${API_BASE}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (refreshRes.ok) {
        const refreshData = await refreshRes.json();
        
        // Save new credentials in Zustand
        const currentUser = useStore.getState().user;
        if (currentUser) {
          login(currentUser, refreshData.access_token, refreshData.refresh_token);
        }

        // Retry original request with new token
        headers.set("Authorization", `Bearer ${refreshData.access_token}`);
        response = await fetch(url, { ...options, headers });
      } else {
        // Refresh token failed -> force logout
        logout();
        if (typeof window !== "undefined") {
          window.location.href = "/auth/login";
        }
        throw new Error("Session expired. Please log in again.");
      }
    } catch (e) {
      logout();
      throw e;
    }
  }

  if (response.status === 204) {
    return null;
  }

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.detail || "Something went wrong");
  }
  return data;
}
