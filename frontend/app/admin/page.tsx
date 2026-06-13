"use client";

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchWithAuth } from "../../lib/api/client";
import { motion } from "framer-motion";
import { Settings, BarChart3, Users, Crown, ShieldCheck, Loader2 } from "lucide-react";

export default function AdminPage() {
  const queryClient = useQueryClient();
  const [targetUserId, setTargetUserId] = useState("");
  const [overrideTier, setOverrideTier] = useState("pro");
  const [msg, setMsg] = useState("");

  // Queries
  const { data: analytics, isLoading: loadingAnalytics } = useQuery({
    queryKey: ["admin-analytics"],
    queryFn: () => fetchWithAuth("/admin/analytics")
  });

  const { data: users = [], isLoading: loadingUsers } = useQuery({
    queryKey: ["admin-users"],
    queryFn: () => fetchWithAuth("/admin/users")
  });

  // Mutations
  const overrideMutation = useMutation({
    mutationFn: ({ userId, tier }: { userId: string; tier: string }) =>
      fetchWithAuth(`/admin/users/${userId}/subscription`, {
        method: "PUT",
        body: JSON.stringify({ tier, status: "active" })
      }),
    onSuccess: (data) => {
      setMsg(data.message || "Updated user subscription successfully.");
      queryClient.invalidateQueries({ queryKey: ["admin-users"] });
      queryClient.invalidateQueries({ queryKey: ["admin-analytics"] });
    }
  });

  const handleOverrideSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setMsg("");
    if (targetUserId) {
      overrideMutation.mutate({ userId: targetUserId, tier: overrideTier });
    }
  };

  if (loadingAnalytics || loadingUsers) {
    return (
      <div className="flex justify-center items-center py-24">
        <Loader2 className="animate-spin text-indigo-400" size={40} />
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl md:text-3xl font-extrabold text-white flex items-center gap-2">
          <ShieldCheck size={28} className="text-rose-500" />
          Admin Console Panel
        </h2>
        <p className="text-sm text-slate-400 mt-1">Platform operations overview, usage metrics, and subscription overrides.</p>
      </div>

      {msg && (
        <div className="bg-indigo-950/30 border border-indigo-900 text-indigo-300 text-xs py-3 px-4 rounded-xl max-w-xl">
          {msg}
        </div>
      )}

      {/* Grid: Analytics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-panel p-6 rounded-2xl flex items-center gap-4">
          <div className="p-4 bg-slate-900 rounded-xl text-indigo-400">
            <Users size={24} />
          </div>
          <div>
            <span className="text-xs text-slate-400 block font-medium">Total Registered Users</span>
            <span className="text-2xl font-bold text-white mt-1 block">{analytics?.total_users}</span>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl flex items-center gap-4">
          <div className="p-4 bg-slate-900 rounded-xl text-purple-400">
            <BarChart3 size={24} />
          </div>
          <div>
            <span className="text-xs text-slate-400 block font-medium">Total Resumes Compiled</span>
            <span className="text-2xl font-bold text-white mt-1 block">{analytics?.total_resumes_generated}</span>
          </div>
        </div>

        <div className="glass-panel p-6 rounded-2xl flex items-center gap-4">
          <div className="p-4 bg-slate-900 rounded-xl text-amber-500">
            <Crown size={24} />
          </div>
          <div>
            <span className="text-xs text-slate-400 block font-medium">Active Pro Tier Subscriptions</span>
            <span className="text-2xl font-bold text-white mt-1 block">{analytics?.active_pro_users}</span>
          </div>
        </div>
      </div>

      {/* Grid: Table & Override Tool */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left: Users table list */}
        <div className="lg:col-span-2 glass-panel p-6 rounded-2xl flex flex-col gap-4">
          <h3 className="font-bold text-white text-sm border-b border-slate-800 pb-2">User Directory</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left text-slate-300">
              <thead className="text-[10px] text-slate-500 uppercase tracking-widest border-b border-slate-800">
                <tr>
                  <th className="py-3 px-2">Email</th>
                  <th className="py-3 px-2">Role</th>
                  <th className="py-3 px-2">Subscription Tier</th>
                  <th className="py-3 px-2">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/40">
                {users.map((u: any) => (
                  <tr key={u.id} className="hover:bg-slate-900/30">
                    <td className="py-3.5 px-2 text-white font-medium">{u.email}</td>
                    <td className="py-3.5 px-2">{u.is_admin ? "Admin" : "User"}</td>
                    <td className="py-3.5 px-2 uppercase font-semibold text-indigo-400">{u.subscription?.tier || "free"}</td>
                    <td className="py-3.5 px-2 uppercase">{u.subscription?.status || "active"}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right: Manual Subscription Override Form */}
        <div className="glass-panel p-6 rounded-2xl h-fit flex flex-col gap-4">
          <h3 className="font-bold text-white text-sm border-b border-slate-800 pb-2">Manual Subscription Override</h3>
          <form onSubmit={handleOverrideSubmit} className="flex flex-col gap-4">
            <div className="flex flex-col gap-1">
              <label className="text-xs text-slate-400">Select User Account</label>
              <select
                value={targetUserId}
                onChange={(e) => setTargetUserId(e.target.value)}
                className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white"
                required
              >
                <option value="">-- Choose User --</option>
                {users.map((u: any) => (
                  <option key={u.id} value={u.id}>
                    {u.email} ({u.subscription?.tier || "free"})
                  </option>
                ))}
              </select>
            </div>

            <div className="flex flex-col gap-1">
              <label className="text-xs text-slate-400">Change Tier To</label>
              <select
                value={overrideTier}
                onChange={(e) => setOverrideTier(e.target.value)}
                className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white"
              >
                <option value="free">Free Starter</option>
                <option value="pro">Pro Unlimited</option>
              </select>
            </div>

            <button
              type="submit"
              disabled={overrideMutation.isPending}
              className="bg-indigo-600 hover:bg-indigo-500 py-3 rounded-xl text-xs font-semibold text-white w-full transition-colors mt-2"
            >
              {overrideMutation.isPending ? "Updating..." : "Override Tier Status"}
            </button>
          </form>
        </div>

      </div>
    </div>
  );
}
