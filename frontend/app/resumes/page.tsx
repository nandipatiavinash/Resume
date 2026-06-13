"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchWithAuth } from "../../lib/api/client";
import { motion } from "framer-motion";
import { FileText, Download, BarChart2, Calendar, Sparkles, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import Link from "next/link";

export default function ResumesPage() {
  const { data: resumes = [], isLoading } = useQuery({
    queryKey: ["resumes"],
    queryFn: () => fetchWithAuth("/resume"),
  });

  const handleDownload = async (id: string) => {
    try {
      const data = await fetchWithAuth(`/resume/download/${id}`);
      if (data.url) {
        window.open(data.url, "_blank");
      }
    } catch (err) {
      alert("Could not retrieve pre-signed download link.");
    }
  };

  return (
    <div className="flex flex-col gap-8">
      {/* Header */}
      <div>
        <h2 className="text-2xl md:text-3xl font-extrabold text-white">Resumes History</h2>
        <p className="text-sm text-slate-400 mt-1">Access all your AI-tailored resumes and PDF assets.</p>
      </div>

      {isLoading ? (
        <div className="flex justify-center items-center py-24">
          <Loader2 className="animate-spin text-indigo-400" size={32} />
        </div>
      ) : resumes.length === 0 ? (
        <div className="glass-card p-12 text-center rounded-2xl max-w-xl mx-auto w-full">
          <FileText className="mx-auto text-slate-600 mb-3" size={36} />
          <p className="text-sm text-slate-400">No optimized resumes compiled yet.</p>
          <Link href="/generate" className="mt-4 bg-indigo-600 hover:bg-indigo-500 py-2 px-6 rounded-xl text-xs font-semibold inline-block text-white">
            Create First Optimized Resume
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {resumes.map((res: any) => {
            const dateStr = new Date(res.created_at).toLocaleDateString("en-US", {
              year: "numeric",
              month: "short",
              day: "numeric"
            });
            return (
              <motion.div
                key={res.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                className="glass-panel p-6 rounded-2xl flex flex-col gap-4 relative overflow-hidden"
              >
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-3">
                    <div className="p-3 bg-indigo-950/40 border border-indigo-900/40 rounded-xl text-indigo-400">
                      <FileText size={20} />
                    </div>
                    <div>
                      <h4 className="font-bold text-white text-sm">Tailored Resume PDF</h4>
                      <div className="flex items-center gap-1.5 text-xs text-slate-500 mt-1">
                        <Calendar size={12} />
                        <span>{dateStr}</span>
                      </div>
                    </div>
                  </div>
                  
                  {/* Status pills */}
                  <span className={`text-[10px] font-bold uppercase tracking-wider py-1 px-2.5 rounded-full ${
                    res.status === "completed" ? "bg-emerald-950/20 text-emerald-400 border border-emerald-950" :
                    res.status === "failed" ? "bg-rose-950/20 text-rose-400 border border-rose-950" :
                    "bg-indigo-950/20 text-indigo-400 border border-indigo-950 animate-pulse"
                  }`}>
                    {res.status}
                  </span>
                </div>

                {res.status === "completed" && (
                  <div className="flex gap-2 mt-2 w-full">
                    <button
                      onClick={() => handleDownload(res.id)}
                      className="flex-1 bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 border border-indigo-900/30 font-semibold text-xs py-2 px-3 rounded-xl flex items-center justify-center gap-1.5 transition-colors"
                    >
                      <Download size={12} /> Download PDF
                    </button>
                    <Link
                      href={`/ats/${res.id}`}
                      className="flex-1 bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 font-semibold text-xs py-2 px-3 rounded-xl flex items-center justify-center gap-1.5 transition-colors"
                    >
                      <BarChart2 size={12} /> ATS Report
                    </Link>
                  </div>
                )}

                {res.status === "failed" && (
                  <div className="text-xs text-rose-400 bg-rose-950/10 border border-rose-900/30 p-3 rounded-xl mt-2 flex items-center gap-1.5">
                    <AlertCircle size={14} />
                    <span>Compile error: {res.error_message?.substring(0, 80) || "LaTeX syntax crashed"}...</span>
                  </div>
                )}
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
