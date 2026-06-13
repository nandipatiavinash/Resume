import { create } from "zustand";

interface UserProfile {
  id: string;
  email: string;
  is_active: boolean;
  is_admin: boolean;
}

interface AuthState {
  user: UserProfile | null;
  token: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  login: (user: UserProfile, token: string, refreshToken: string) => void;
  logout: () => void;
}

export const useStore = create<AuthState>((set) => {
  // Safe check for localStorage on SSR
  const getLocalStorage = (key: string) => {
    if (typeof window !== "undefined") {
      return localStorage.getItem(key);
    }
    return null;
  };

  const initialUser = getLocalStorage("user");
  const initialToken = getLocalStorage("token");
  const initialRefresh = getLocalStorage("refresh_token");

  return {
    user: initialUser ? JSON.parse(initialUser) : null,
    token: initialToken,
    refreshToken: initialRefresh,
    isAuthenticated: !!initialToken,
    login: (user, token, refreshToken) => {
      if (typeof window !== "undefined") {
        localStorage.setItem("user", JSON.stringify(user));
        localStorage.setItem("token", token);
        localStorage.setItem("refresh_token", refreshToken);
      }
      set({ user, token, refreshToken, isAuthenticated: true });
    },
    logout: () => {
      if (typeof window !== "undefined") {
        localStorage.removeItem("user");
        localStorage.removeItem("token");
        localStorage.removeItem("refresh_token");
      }
      set({ user: null, token: null, refreshToken: null, isAuthenticated: false });
    },
  };
});
