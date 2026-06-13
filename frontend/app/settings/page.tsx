"use client";

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchWithAuth } from "../../lib/api/client";
import { motion } from "framer-motion";
import { Sparkles, Key, CreditCard, CheckCircle2, ShieldAlert, Loader2, Plus, Trash2, Power } from "lucide-react";

export default function SettingsPage() {
  const queryClient = useQueryClient();
  const [provider, setProvider] = useState("openai");
  const [apiKey, setApiKey] = useState("");
  const [apiBase, setApiBase] = useState("");
  const [billingLoading, setBillingLoading] = useState(false);
  const [error, setError] = useState("");

  // Queries
  const { data: configs = [], isLoading } = useQuery({
    queryKey: ["ai-configs"],
    queryFn: () => fetchWithAuth("/ai/configs")
  });

  // Mutations
  const addConfigMutation = useMutation({
    mutationFn: (data: any) => fetchWithAuth("/ai/configs", { method: "POST", body: JSON.stringify(data) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["ai-configs"] });
      setApiKey("");
      setApiBase("");
    },
    onError: (err: any) => {
      setError(err.message || "Failed to save API Configuration.");
    }
  });

  const activateConfigMutation = useMutation({
    mutationFn: (id: string) => fetchWithAuth(`/ai/configs/${id}/activate`, { method: "POST" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["ai-configs"] })
  });

  const deleteConfigMutation = useMutation({
    mutationFn: (id: string) => fetchWithAuth(`/ai/configs/${id}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["ai-configs"] })
  });

  const handleSaveConfig = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (apiKey.trim()) {
      addConfigMutation.mutate({
        provider_name: provider,
        api_key: apiKey,
        api_base: apiBase.trim() || null
      });
    }
  };

  const handleStripeUpgrade = async () => {
    setBillingLoading(true);
    setError("");
    try {
      const res = await fetchWithAuth("/billing/checkout", {
        method: "POST",
        body: JSON.stringify({ plan_type: "pro" })
      });
      if (res.checkout_url) {
        window.location.href = res.checkout_url;
      }
    } catch (err: any) {
      setError(err.message || "Failed to connect to billing server.");
    } finally {
      setBillingLoading(false);
    }
  };

  return (
    <div className="flex flex-col gap-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl md:text-3xl font-extrabold text-white">Settings</h2>
        <p className="text-sm text-slate-400 mt-1">Configure your AI model providers and manage your payment subscription.</p>
      </div>

      {error && (
        <div className="bg-rose-950/30 border border-rose-900 text-rose-300 text-xs py-3 px-4 rounded-xl flex items-center gap-2 max-w-xl">
          <ShieldAlert size={16} />
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Columns: AI Credentials */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="font-bold text-white mb-2 flex items-center gap-2 text-sm">
              <Key size={16} className="text-indigo-400" />
              Register AI API Keys
            </h3>
            <p className="text-xs text-slate-400 mb-6">API credentials are encrypted via Fernet secret keys in our PostgreSQL database before saving, and decrypted in-memory during resume optimization runs.</p>

            <form onSubmit={handleSaveConfig} className="flex flex-col gap-4 max-w-xl">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex flex-col gap-1">
                  <label className="text-xs text-slate-400 font-medium">Model Provider</label>
                  <select
                    value={provider}
                    onChange={(e) => setProvider(e.target.value)}
                    className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white"
                  >
                    <option value="openai">OpenAI (GPT-4o-mini)</option>
                    <option value="claude">Anthropic (Claude 3.5 Sonnet)</option>
                    <option value="gemini">Google (Gemini 1.5 Flash)</option>
                    <option value="deepseek">DeepSeek (DeepSeek Coder)</option>
                    <option value="openrouter">OpenRouter (Any open weights)</option>
                  </select>
                </div>
                
                <div className="flex flex-col gap-1">
                  <label className="text-xs text-slate-400 font-medium">API Base URL (Optional)</label>
                  <input
                    type="url"
                    value={apiBase}
                    onChange={(e) => setApiBase(e.target.value)}
                    placeholder="https://api.yourprovider.com/v1"
                    className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white placeholder-slate-600 focus:outline-none"
                  />
                </div>
              </div>

              <div className="flex flex-col gap-1">
                <label className="text-xs text-slate-400 font-medium">API Key</label>
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="sk-..."
                  className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white focus:outline-none"
                  required
                />
              </div>

              <button
                type="submit"
                disabled={addConfigMutation.isPending}
                className="bg-indigo-600 hover:bg-indigo-500 py-2.5 px-6 rounded-xl text-xs font-semibold text-white w-fit transition-colors"
              >
                {addConfigMutation.isPending ? "Saving..." : "Encrypt \& Save Key"}
              </button>
            </form>
          </div>

          {/* Registered Keys List */}
          <div className="glass-panel p-6 rounded-2xl flex flex-col gap-4">
            <h3 className="font-bold text-white text-sm">Configured Keys</h3>
            {isLoading ? (
              <p className="text-xs text-slate-500">Loading configurations...</p>
            ) : configs.length === 0 ? (
              <p className="text-xs text-slate-400">No AI provider keys configured. Add one above.</p>
            ) : (
              <div className="flex flex-col gap-3">
                {configs.map((c: any) => (
                  <div key={c.id} className="glass-card p-4 rounded-xl flex justify-between items-center text-xs">
                    <div>
                      <span className="font-bold text-white text-sm uppercase">{c.provider_name}</span>
                      {c.api_base && <span className="text-slate-500 block mt-1">Base: {c.api_base}</span>}
                    </div>
                    <div className="flex items-center gap-3">
                      {c.is_active ? (
                        <span className="bg-emerald-950/20 text-emerald-400 border border-emerald-950 text-[10px] py-1 px-2.5 rounded-full font-bold uppercase flex items-center gap-1">
                          <CheckCircle2 size={10} /> Active
                        </span>
                      ) : (
                        <button
                          onClick={() => activateConfigMutation.mutate(c.id)}
                          className="bg-slate-800 hover:bg-slate-700 py-1.5 px-3 rounded-lg text-slate-300 font-semibold"
                        >
                          Activate
                        </button>
                      )}
                      <button
                        onClick={() => deleteConfigMutation.mutate(c.id)}
                        className="text-rose-400 hover:text-rose-300 p-2"
                      >
                        <Trash2 size={14} />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Billing upgrade panel */}
        <div className="glass-panel p-6 rounded-2xl h-fit flex flex-col gap-6 border border-slate-900">
          <h3 className="font-bold text-white mb-2 flex items-center gap-2 text-sm border-b border-slate-800 pb-2">
            <CreditCard size={16} className="text-purple-400" />
            Billing Plan
          </h3>

          <div className="bg-slate-900/60 p-4 rounded-xl border border-slate-800">
            <span className="text-[10px] text-slate-500 uppercase font-bold tracking-widest block">CURRENT SUBSCRIPTION</span>
            <span className="text-lg font-bold text-white mt-1 block">Free Starter Tier</span>
            <span className="text-xs text-slate-400 mt-2 block leading-relaxed">
              Limit: 5 optimized resumes, 5 ATS reports, and 3 cover letters per month.
            </span>
          </div>

          <div className="flex flex-col gap-4">
            <div className="flex items-start gap-2 text-xs text-slate-300">
              <CheckCircle2 size={14} className="text-indigo-400 mt-0.5" />
              <span>Unlimited LaTeX optimizations</span>
            </div>
            <div className="flex items-start gap-2 text-xs text-slate-300">
              <CheckCircle2 size={14} className="text-indigo-400 mt-0.5" />
              <span>Unlimited ATS scanners</span>
            </div>
            <div className="flex items-start gap-2 text-xs text-slate-300">
              <CheckCircle2 size={14} className="text-indigo-400 mt-0.5" />
              <span>Priority Celery compilation</span>
            </div>
          </div>

          <button
            onClick={handleStripeUpgrade}
            disabled={billingLoading}
            className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3 rounded-xl text-xs flex items-center justify-center gap-2 transition-colors mt-2"
          >
            {billingLoading ? (
              <Loader2 className="animate-spin" size={14} />
            ) : (
              <>
                <Sparkles size={14} /> Upgrade to Pro ($29/mo)
              </>
            )}
          </button>
        </div>

      </div>
    </div>
  );
}
