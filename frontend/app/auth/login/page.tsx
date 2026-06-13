"use client";

import React, { useState } from "react";
import { useStore } from "../../../store/useStore";
import { fetchWithAuth } from "../../../lib/api/client";
import Link from "next/link";
import { ArrowRight, Lock, Mail, Loader2, Sparkles } from "lucide-react";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const loginAction = useStore((state) => state.login);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const data = await fetchWithAuth("/auth/login", {
        method: "POST",
        body: JSON.stringify({ email, password }),
        skipAuth: true
      });
      
      // Fetch user profile info
      const userProfile = await fetchWithAuth("/profile", {
        headers: { "Authorization": `Bearer ${data.access_token}` }
      }).catch(() => {
        // Fallback profile check
        // Extract payload user_id
        const base64Url = data.access_token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const payload = JSON.parse(window.atob(base64));
        return { id: payload.sub, email, is_active: true, is_admin: false };
      });
      
      loginAction(userProfile, data.access_token, data.refresh_token);
      window.location.href = "/dashboard";
    } catch (err: any) {
      setError(err.message || "Failed to log in. Check credentials.");
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    try {
      const data = await fetchWithAuth("/auth/google-oauth", { skipAuth: true });
      if (data.url) {
        window.location.href = data.url;
      }
    } catch (err) {
      setError("Could not generate Google Login link.");
    }
  };

  return (
    <div className="flex justify-center items-center py-12">
      <div className="glass-panel w-full max-w-md p-8 rounded-3xl shadow-xl">
        <div className="text-center mb-6">
          <div className="w-12 h-12 bg-indigo-950/40 border border-indigo-900 rounded-2xl flex items-center justify-center text-indigo-400 mx-auto mb-3">
            <Sparkles size={24} />
          </div>
          <h2 className="text-2xl font-bold">Welcome Back</h2>
          <p className="text-sm text-slate-400 mt-1">Access your resume intelligence vault</p>
        </div>

        {error && (
          <div className="bg-rose-950/30 border border-rose-900 text-rose-300 text-xs py-3 px-4 rounded-xl mb-4">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-400 font-medium">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-3.5 text-slate-500" size={18} />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl py-3 pl-10 pr-4 text-sm text-white focus:outline-none focus:border-indigo-500"
                required
              />
            </div>
          </div>

          <div className="flex flex-col gap-1">
            <label className="text-xs text-slate-400 font-medium">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-3.5 text-slate-500" size={18} />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full bg-slate-900/60 border border-slate-800 rounded-xl py-3 pl-10 pr-4 text-sm text-white focus:outline-none focus:border-indigo-500"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-3 rounded-xl flex items-center justify-center gap-2 mt-2 transition-all shadow-md shadow-indigo-600/25 disabled:bg-indigo-850"
          >
            {loading ? (
              <Loader2 className="animate-spin" size={18} />
            ) : (
              <>
                Sign In
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        <div className="relative my-6 text-center">
          <hr className="border-slate-800" />
          <span className="bg-[#0b0f19] px-3 text-xs text-slate-500 absolute -top-2 left-1/2 -translate-x-1/2">
            or continue with
          </span>
        </div>

        <button
          onClick={handleGoogleLogin}
          className="w-full glass-card hover:bg-slate-800/20 py-3 rounded-xl text-sm font-medium flex items-center justify-center gap-2 transition-colors mb-6"
        >
          <svg className="h-4 w-4" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12.24 10.285V14.4h6.887c-.648 2.41-2.519 4.114-5.111 4.114a5.64 5.64 0 01-5.637-5.643 5.64 5.64 0 015.637-5.644c1.558 0 2.91.564 3.96 1.5l3.245-3.246C19.296 3.633 16.035 2.228 12.24 2.228c-5.4 0-9.775 4.378-9.775 9.773s4.375 9.774 9.775 9.774c5.787 0 9.626-4.062 9.626-9.79 0-.665-.057-1.3-.167-1.7H12.24z" />
          </svg>
          Google OAuth
        </button>

        <p className="text-center text-xs text-slate-400">
          Don't have an account?{" "}
          <Link href="/auth/signup" className="text-indigo-400 hover:underline">
            Register free
          </Link>
        </p>
      </div>
    </div>
  );
}
