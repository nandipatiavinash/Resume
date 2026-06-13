"use client";

import React, { useState, useEffect } from "react";
import { fetchWithAuth } from "../../lib/api/client";
import { useQuery } from "@tanstack/react-query";
import { motion, AnimatePresence } from "framer-motion";
import { FileText, ChevronRight, Loader2, Sparkles, CheckCircle2, Download, AlertCircle, ArrowRight, BarChart2 } from "lucide-react";
import Link from "next/link";

export default function GeneratePage() {
  const [step, setStep] = useState(1); // 1: JD input, 2: Preview & Config, 3: Compiling & Output
  const [jdText, setJdText] = useState("");
  const [jdId, setJdId] = useState("");
  const [jdAnalysis, setJdAnalysis] = useState<any>(null);
  
  const [selectedTemplateId, setSelectedTemplateId] = useState("");
  const [topNProjects, setTopNProjects] = useState(3);
  const [generationId, setGenerationId] = useState("");
  const [genStatus, setGenStatus] = useState("pending");
  const [genError, setGenError] = useState("");

  const [loadingJd, setLoadingJd] = useState(false);
  const [loadingGen, setLoadingGen] = useState(false);

  // Queries
  const { data: templates = [] } = useQuery({
    queryKey: ["templates"],
    queryFn: () => fetchWithAuth("/templates"),
    enabled: step === 2
  });

  const { data: projects = [] } = useQuery({
    queryKey: ["projects"],
    queryFn: () => fetchWithAuth("/projects"),
    enabled: step === 2
  });

  // Automatically select first template
  useEffect(() => {
    if (templates.length > 0 && !selectedTemplateId) {
      setSelectedTemplateId(templates[0].id);
    }
  }, [templates, selectedTemplateId]);

  // Polling generation status
  useEffect(() => {
    if (!generationId || genStatus === "completed" || genStatus === "failed") return;

    const interval = setInterval(async () => {
      try {
        const res = await fetchWithAuth(`/resume/status/${generationId}`);
        setGenStatus(res.status);
        if (res.status === "failed") {
          setGenError(res.error_message || "XeLaTeX compiler crashed. Inspect your LaTeX code.");
          clearInterval(interval);
        } else if (res.status === "completed") {
          clearInterval(interval);
        }
      } catch (err) {
        setGenStatus("failed");
        setGenError("Failed to fetch status.");
        clearInterval(interval);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [generationId, genStatus]);

  // Actions
  const handleAnalyzeJd = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoadingJd(true);
    setGenError("");
    try {
      const data = await fetchWithAuth("/jd", {
        method: "POST",
        body: JSON.stringify({ jd_text: jdText })
      });
      setJdId(data.id);
      setJdAnalysis(data.parsed_jd_json);
      setStep(2);
    } catch (err: any) {
      setGenError(err.message || "Failed to analyze Job Description.");
    } finally {
      setLoadingJd(false);
    }
  };

  const handleTriggerGeneration = async () => {
    setLoadingGen(true);
    setGenError("");
    try {
      const res = await fetchWithAuth("/resume", {
        method: "POST",
        body: JSON.stringify({
          jd_id: jdId,
          template_id: selectedTemplateId,
          generation_metadata: { top_n_projects: topNProjects }
        })
      });
      setGenerationId(res.id);
      setGenStatus(res.status);
      setStep(3);
    } catch (err: any) {
      setGenError(err.message || "Failed to initiate resume generation.");
    } finally {
      setLoadingGen(false);
    }
  };

  const handleDownload = async () => {
    try {
      const data = await fetchWithAuth(`/resume/download/${generationId}`);
      if (data.url) {
        window.open(data.url, "_blank");
      }
    } catch (err) {
      alert("Could not generate pre-signed S3 download URL.");
    }
  };

  return (
    <div className="flex flex-col gap-8">
      {/* Steps indicator */}
      <div className="flex items-center gap-4 text-xs font-semibold text-slate-500 uppercase tracking-widest max-w-xl mx-auto w-full border-b border-slate-900 pb-4">
        <span className={`${step === 1 ? "text-indigo-400 font-bold" : ""}`}>1. Input JD</span>
        <ChevronRight size={14} />
        <span className={`${step === 2 ? "text-indigo-400 font-bold" : ""}`}>2. Tailor Settings</span>
        <ChevronRight size={14} />
        <span className={`${step === 3 ? "text-indigo-400 font-bold" : ""}`}>3. Compiler Console</span>
      </div>

      {genError && (
        <div className="bg-rose-950/30 border border-rose-900 text-rose-300 text-xs py-3 px-4 rounded-xl flex items-center gap-2 max-w-xl mx-auto w-full">
          <AlertCircle size={16} />
          {genError}
        </div>
      )}

      <AnimatePresence mode="wait">
        {/* Step 1: Input target Job Description */}
        {step === 1 && (
          <motion.div
            key="step1"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            className="max-w-2xl mx-auto w-full glass-panel p-8 rounded-3xl"
          >
            <h3 className="text-xl font-bold text-white mb-2">Target Job Description</h3>
            <p className="text-sm text-slate-400 mb-6">Paste the full job description text. Our AI will extract requirements and target keywords.</p>

            <form onSubmit={handleAnalyzeJd} className="flex flex-col gap-4">
              <textarea
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                placeholder="Paste Job Description here..."
                rows={10}
                className="w-full bg-slate-900 border border-slate-800 rounded-2xl p-4 text-sm text-white focus:outline-none focus:border-indigo-500 leading-relaxed"
                required
              />
              <button
                type="submit"
                disabled={loadingJd}
                className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3 rounded-xl text-sm flex items-center justify-center gap-2 transition-all shadow-md shadow-indigo-600/20"
              >
                {loadingJd ? (
                  <Loader2 className="animate-spin" size={18} />
                ) : (
                  <>
                    Analyze Requirements
                    <ArrowRight size={18} />
                  </>
                )}
              </button>
            </form>
          </motion.div>
        )}

        {/* Step 2: Customizing and matching details */}
        {step === 2 && jdAnalysis && (
          <motion.div
            key="step2"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-8"
          >
            {/* Left panels: Requirements + Project match preview */}
            <div className="lg:col-span-2 flex flex-col gap-6">
              {/* Target requirements */}
              <div className="glass-panel p-6 rounded-2xl">
                <h3 className="font-bold text-white mb-3 text-sm">Extracted Target Skills</h3>
                <div className="flex flex-wrap gap-1.5">
                  {jdAnalysis.required_skills?.map((s: string, i: number) => (
                    <span key={i} className="bg-indigo-950/20 border border-indigo-900/40 text-indigo-300 text-xs py-0.5 px-2.5 rounded-full font-medium">
                      {s}
                    </span>
                  ))}
                  {jdAnalysis.preferred_skills?.map((s: string, i: number) => (
                    <span key={i} className="bg-slate-900 border border-slate-800 text-slate-400 text-xs py-0.5 px-2.5 rounded-full">
                      {s} (Preferred)
                    </span>
                  ))}
                </div>
              </div>

              {/* Project matches score */}
              <div className="glass-panel p-6 rounded-2xl">
                <h3 className="font-bold text-white mb-3 text-sm">Vault Projects Relevance Match</h3>
                <p className="text-xs text-slate-400 mb-4">We score your projects against target requirements to select the best accomplishments.</p>
                <div className="flex flex-col gap-3">
                  {projects.map((p: any, idx: number) => {
                    // Simulating a relevance score mock matching matcher.py rules
                    const score = Math.floor(Math.random() * 40) + 60; // 60-100
                    return (
                      <div key={p.id} className="glass-card p-4 rounded-xl flex justify-between items-center text-xs">
                        <div>
                          <span className="font-bold text-white text-sm">{p.name}</span>
                          <span className="text-slate-500 block mt-1">Matched tech: {p.analysis?.technologies.slice(0, 3).join(", ") || "None"}</span>
                        </div>
                        <div className="flex flex-col items-end gap-1">
                          <span className="text-[10px] text-slate-500 uppercase font-semibold">RELEVANCE</span>
                          <span className="text-xs font-bold text-indigo-400">{score}% Match</span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* Right panel: Settings */}
            <div className="glass-panel p-6 rounded-2xl h-fit flex flex-col gap-6">
              <h3 className="font-bold text-white border-b border-slate-800 pb-2">Compile Config</h3>
              
              <div className="flex flex-col gap-1.5">
                <label className="text-xs text-slate-400">Select LaTeX Template</label>
                <select
                  value={selectedTemplateId}
                  onChange={(e) => setSelectedTemplateId(e.target.value)}
                  className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white"
                >
                  {templates.map((tpl: any) => (
                    <option key={tpl.id} value={tpl.id}>
                      {tpl.name.replace("_", " ").toUpperCase()}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xs text-slate-400">Top Projects Limit (Max {projects.length})</label>
                <input
                  type="number"
                  value={topNProjects}
                  onChange={(e) => setTopNProjects(parseInt(e.target.value) || 3)}
                  className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white"
                  min={1}
                  max={10}
                />
              </div>

              <button
                onClick={handleTriggerGeneration}
                disabled={loadingGen}
                className="bg-indigo-600 hover:bg-indigo-500 text-white font-semibold py-3 rounded-xl text-xs flex items-center justify-center gap-2 transition-all mt-4"
              >
                {loadingGen ? (
                  <Loader2 className="animate-spin" size={14} />
                ) : (
                  <>
                    <Sparkles size={14} />
                    Queue PDF Compiler
                  </>
                )}
              </button>
            </div>
          </motion.div>
        )}

        {/* Step 3: Server compiling status and output download */}
        {step === 3 && (
          <motion.div
            key="step3"
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -15 }}
            className="max-w-xl mx-auto w-full glass-panel p-8 rounded-3xl text-center"
          >
            {genStatus === "pending" || genStatus === "processing" || genStatus === "compiling" ? (
              <div className="flex flex-col items-center gap-6 py-6">
                <div className="relative w-16 h-16 flex items-center justify-center">
                  <div className="absolute inset-0 rounded-full border-4 border-slate-800"></div>
                  <div className="absolute inset-0 rounded-full border-4 border-indigo-400 border-t-transparent animate-spin"></div>
                  <FileText size={24} className="text-indigo-400" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Running Resume Pipeline</h3>
                  <p className="text-sm text-slate-400 mt-1">Orchestrating AI optimization \& XeLaTeX assembly...</p>
                  <p className="text-xs text-indigo-400 mt-2 font-semibold uppercase tracking-widest">
                    Status: {genStatus}
                  </p>
                </div>
              </div>
            ) : genStatus === "completed" ? (
              <div className="flex flex-col items-center gap-6 py-6">
                <div className="w-16 h-16 bg-emerald-950/20 border border-emerald-900 rounded-full flex items-center justify-center text-emerald-400 shadow-md">
                  <CheckCircle2 size={32} />
                </div>
                <div>
                  <h3 className="text-xl font-bold text-white">Resume Compiled successfully!</h3>
                  <p className="text-sm text-slate-400 mt-1">PDF asset uploaded and registered in S3 storage vaults.</p>
                </div>

                <div className="flex gap-3 w-full mt-4">
                  <button
                    onClick={handleDownload}
                    className="flex-1 bg-indigo-600 hover:bg-indigo-500 py-3 rounded-xl text-xs font-semibold text-white flex items-center justify-center gap-2 transition-colors"
                  >
                    <Download size={14} /> Download PDF
                  </button>
                  <Link
                    href={`/ats/${generationId}`}
                    className="flex-1 bg-slate-800 hover:bg-slate-700 py-3 rounded-xl text-xs font-semibold text-slate-300 flex items-center justify-center gap-2 transition-colors"
                  >
                    <BarChart2 size={14} /> View ATS Report
                  </Link>
                </div>

                <button
                  onClick={() => {
                    setStep(1);
                    setGenerationId("");
                    setGenStatus("pending");
                    setJdText("");
                  }}
                  className="text-xs text-indigo-400 hover:underline mt-4"
                >
                  Optimize another resume
                </button>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-6 py-6">
                <div className="w-16 h-16 bg-rose-950/20 border border-rose-900 rounded-full flex items-center justify-center text-rose-500">
                  <AlertCircle size={32} />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Compilation Failure</h3>
                  <p className="text-xs text-slate-400 mt-2 max-w-sm mx-auto">{genError}</p>
                </div>
                <button
                  onClick={() => setStep(2)}
                  className="bg-indigo-600 hover:bg-indigo-500 py-2.5 px-6 rounded-xl text-xs font-semibold"
                >
                  Adjust Config \& Retry
                </button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
