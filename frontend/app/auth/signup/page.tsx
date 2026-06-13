"use client";

import React, { useState } from "react";
import { fetchWithAuth } from "../../../lib/api/client";
import Link from "next/link";
import { ArrowRight, Lock, Mail, Loader2, Award } from "lucide-react";

export default function SignupPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      await fetchWithAuth("/auth/signup", {
        method: "POST",
        body: JSON.stringify({ email, password }),
        skipAuth: true
      });
      setSuccess(true);
    } catch (err: any) {
      setError(err.message || "Failed to create account. Check inputs.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center py-12">
      <div className="glass-panel w-full max-w-md p-8 rounded-3xl shadow-xl">
        <div className="text-center mb-6">
          <div className="w-12 h-12 bg-indigo-950/40 border border-indigo-900 rounded-2xl flex items-center justify-center text-indigo-400 mx-auto mb-3">
            <Award size={24} />
          </div>
          <h2 className="text-2xl font-bold">Get Started</h2>
          <p className="text-sm text-slate-400 mt-1">Create a free master profile today</p>
        </div>

        {error && (
          <div className="bg-rose-950/30 border border-rose-900 text-rose-300 text-xs py-3 px-4 rounded-xl mb-4">
            {error}
          </div>
        )}

        {success ? (
          <div className="text-center flex flex-col gap-4 py-4">
            <div className="bg-indigo-950/30 border border-indigo-900 text-indigo-300 text-sm py-4 px-5 rounded-2xl">
              Account created successfully! You can now log in.
            </div>
            <Link
              href="/auth/login"
              className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-3 rounded-xl transition-all shadow-md"
            >
              Proceed to Login
            </Link>
          </div>
        ) : (
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
              <label className="text-xs text-slate-400 font-medium">Password (Min 6 chars)</label>
              <div className="relative">
                <Lock className="absolute left-3 top-3.5 text-slate-500" size={18} />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-slate-900/60 border border-slate-800 rounded-xl py-3 pl-10 pr-4 text-sm text-white focus:outline-none focus:border-indigo-500"
                  required
                  minLength={6}
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
                  Register Account
                  <ArrowRight size={18} />
                </>
              )}
            </button>
          </form>
        )}

        <div className="relative my-6 text-center">
          <hr className="border-slate-800" />
          <span className="bg-[#0b0f19] px-3 text-xs text-slate-500 absolute -top-2 left-1/2 -translate-x-1/2">
            or return to
          </span>
        </div>

        <p className="text-center text-xs text-slate-400">
          Already have an account?{" "}
          <Link href="/auth/login" className="text-indigo-400 hover:underline">
            Login here
          </Link>
        </p>
      </div>
    </div>
  );
}
