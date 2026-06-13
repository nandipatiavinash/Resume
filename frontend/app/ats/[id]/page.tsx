"use client";

import React from "react";
import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { fetchWithAuth } from "../../../lib/api/client";
import { motion } from "framer-motion";
import { BarChart2, CheckCircle2, AlertTriangle, ArrowLeft, RefreshCw, Loader2, Sparkles } from "lucide-react";
import Link from "next/link";

export default function ATSReportPage() {
  const params = useParams();
  const id = params.id as string;

  // Query ATS report
  const { data: report, isLoading, isError } = useQuery({
    queryKey: ["ats-report", id],
    queryFn: () => fetchWithAuth(`/ats/reports/${id}`),
    enabled: !!id
  });

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-24">
        <Loader2 className="animate-spin text-indigo-400" size={40} />
      </div>
    );
  }

  if (isError || !report) {
    return (
      <div className="glass-panel max-w-md p-8 rounded-3xl text-center mx-auto mt-12 flex flex-col items-center gap-4">
        <AlertTriangle size={36} className="text-rose-500" />
        <h3 className="text-lg font-bold text-white">ATS Scan Not Found</h3>
        <p className="text-sm text-slate-400">Could not retrieve ATS metrics for this optimization run.</p>
        <Link href="/resumes" className="bg-indigo-600 hover:bg-indigo-500 py-2 px-6 rounded-xl text-xs font-semibold text-white">
          Back to History
        </Link>
      </div>
    );
  }

  const scoreColor = 
    report.score >= 80 ? "text-emerald-400 border-emerald-900 bg-emerald-950/10" :
    report.score >= 60 ? "text-yellow-400 border-yellow-900 bg-yellow-950/10" :
    "text-rose-400 border-rose-900 bg-rose-950/10";

  return (
    <div className="flex flex-col gap-8">
      {/* Back link */}
      <div>
        <Link href="/resumes" className="text-xs text-slate-400 hover:text-white flex items-center gap-1.5 w-fit">
          <ArrowLeft size={14} /> Back to History
        </Link>
      </div>

      {/* Main card */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Overall Dial */}
        <div className={`glass-panel p-8 rounded-3xl text-center flex flex-col items-center justify-center gap-4 border ${scoreColor}`}>
          <BarChart2 size={36} />
          <h3 className="text-lg font-bold text-white">Overall ATS Score</h3>
          
          {/* Score Dial */}
          <div className="relative w-36 h-36 flex items-center justify-center rounded-full border-4 border-slate-800 mt-2">
            <span className="text-5xl font-black">{report.score}</span>
            <span className="text-[10px] text-slate-500 absolute bottom-4">OUT OF 100</span>
          </div>

          <p className="text-xs text-slate-400 max-w-xs mt-2 leading-relaxed">
            {report.score >= 80 
              ? "Excellent! Your resume exhibits high keyword coverage and solid action verbs." 
              : "We recommend adjusting your accomplishments to include more target keywords."}
          </p>
        </div>

        {/* Right Columns: Analysis breakdowns */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          {/* Formats & Action counts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass-panel p-6 rounded-2xl">
              <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Format Score</span>
              <span className="text-2xl font-extrabold text-white block mt-1">{report.format_score} / 100</span>
              <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
                <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${report.format_score}%` }}></div>
              </div>
            </div>

            <div className="glass-panel p-6 rounded-2xl">
              <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Action Verb Density</span>
              <span className="text-2xl font-extrabold text-white block mt-1">{report.action_verb_score} / 100</span>
              <div className="w-full bg-slate-800 h-1.5 rounded-full mt-3 overflow-hidden">
                <div className="bg-purple-500 h-full rounded-full" style={{ width: `${report.action_verb_score}%` }}></div>
              </div>
            </div>
          </div>

          {/* Keywords breakdown */}
          <div className="glass-panel p-6 rounded-2xl flex flex-col gap-4">
            <h3 className="font-bold text-white text-sm border-b border-slate-800 pb-2">Target Keywords Match</h3>
            
            {/* Matched tags */}
            <div>
              <span className="text-[10px] text-emerald-400 font-bold uppercase tracking-wider block mb-2">Matched Keywords ({report.matched_keywords.length})</span>
              <div className="flex flex-wrap gap-1.5">
                {report.matched_keywords.length === 0 ? (
                  <span className="text-xs text-slate-500">None matched.</span>
                ) : (
                  report.matched_keywords.map((kw: string, i: number) => (
                    <span key={i} className="bg-emerald-950/20 border border-emerald-900/40 text-emerald-400 text-xs py-0.5 px-2.5 rounded-full font-medium">
                      {kw}
                    </span>
                  ))
                )}
              </div>
            </div>

            {/* Missing tags */}
            <div className="mt-2">
              <span className="text-[10px] text-rose-400 font-bold uppercase tracking-wider block mb-2">Missing Keywords ({report.missing_keywords.length})</span>
              <div className="flex flex-wrap gap-1.5">
                {report.missing_keywords.length === 0 ? (
                  <span className="text-xs text-slate-500">None missing! Great job.</span>
                ) : (
                  report.missing_keywords.map((kw: string, i: number) => (
                    <span key={i} className="bg-rose-950/20 border border-rose-900/40 text-rose-400 text-xs py-0.5 px-2.5 rounded-full font-medium">
                      {kw}
                    </span>
                  ))
                )}
              </div>
            </div>
          </div>

          {/* Improvement Suggestions */}
          <div className="glass-panel p-6 rounded-2xl flex flex-col gap-3">
            <h3 className="font-bold text-white text-sm border-b border-slate-800 pb-2">Targeted Suggestions</h3>
            <ul className="list-disc pl-5 flex flex-col gap-2">
              {report.suggestions.map((s: string, i: number) => (
                <li key={i} className="text-xs text-slate-300 leading-relaxed">{s}</li>
              ))}
            </ul>
          </div>
        </div>

      </div>
    </div>
  );
}
