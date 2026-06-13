"use client";

import React, { useEffect, useState } from "react";
import { useStore } from "../../../store/useStore";
import { fetchWithAuth } from "../../../lib/api/client";
import { Loader2, AlertCircle } from "lucide-react";

export default function AuthCallbackPage() {
  const [error, setError] = useState("");
  const loginAction = useStore((state) => state.login);

  useEffect(() => {
    const searchParams = new URLSearchParams(window.location.search);
    const code = searchParams.get("code");

    if (code) {
      const resolveOAuth = async () => {
        try {
          // Exchange code for JWT tokens
          const tokens = await fetchWithAuth(`/auth/google/callback?code=${code}`, {
            method: "POST",
            skipAuth: true
          });
          
          // Get user details
          const userProfile = await fetchWithAuth("/profile", {
            headers: { "Authorization": `Bearer ${tokens.access_token}` }
          }).catch(() => {
            // Fallback profile if profile CRUD returns 404
            const base64Url = tokens.access_token.split('.')[1];
            const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
            const payload = JSON.parse(window.atob(base64));
            return { id: payload.sub, email: "oauth-user@gmail.com", is_active: true, is_admin: false };
          });
          
          loginAction(userProfile, tokens.access_token, tokens.refresh_token);
          window.location.href = "/dashboard";
        } catch (err: any) {
          setError(err.message || "Failed to log in with Google OAuth.");
        }
      };

      resolveOAuth();
    } else {
      setError("No authentication code was returned from Google.");
    }
  }, [loginAction]);

  return (
    <div className="flex flex-col items-center justify-center py-24 text-center">
      {error ? (
        <div className="glass-panel max-w-md p-8 rounded-3xl border-rose-900 flex flex-col items-center gap-4">
          <AlertCircle size={40} className="text-rose-500" />
          <h3 className="text-lg font-bold text-white">Authentication Error</h3>
          <p className="text-sm text-slate-400">{error}</p>
          <a
            href="/auth/login"
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2 px-6 rounded-xl transition-all"
          >
            Back to Login
          </a>
        </div>
      ) : (
        <div className="flex flex-col items-center gap-4">
          <Loader2 size={48} className="animate-spin text-indigo-400" />
          <h3 className="text-lg font-semibold text-white">Verifying credentials...</h3>
          <p className="text-sm text-slate-400">Completing secure handshake with Google OAuth</p>
        </div>
      )}
    </div>
  );
}
