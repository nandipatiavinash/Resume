"use client";

import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchWithAuth } from "../../lib/api/client";
import { motion, AnimatePresence } from "framer-motion";
import { Github, Plus, Trash2, Cpu, CheckCircle2, AlertCircle, Loader2, Link as LinkIcon, ExternalLink } from "lucide-react";

export default function ProjectsPage() {
  const queryClient = useQueryClient();
  const [githubUrl, setGithubUrl] = useState("");
  const [projectName, setProjectName] = useState("");
  const [projectDesc, setProjectDesc] = useState("");
  const [analyzingIds, setAnalyzingIds] = useState<string[]>([]);
  const [error, setError] = useState("");

  // Fetch projects list
  const { data: projects = [], isLoading } = useQuery({
    queryKey: ["projects"],
    queryFn: () => fetchWithAuth("/projects"),
    // Poll project list every 5 seconds if there's an ongoing analysis
    refetchInterval: (query) => {
      const hasOngoingAnalysis = query.state.data?.some(
        (p: any) => p.github_url && !p.analysis && analyzingIds.includes(p.id)
      );
      return hasOngoingAnalysis ? 5000 : false;
    }
  });

  // Mutations
  const createProjectMutation = useMutation({
    mutationFn: (data: any) => fetchWithAuth("/projects", { method: "POST", body: JSON.stringify(data) }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["projects"] });
      setProjectName("");
      setProjectDesc("");
    }
  });

  const deleteProjectMutation = useMutation({
    mutationFn: (id: string) => fetchWithAuth(`/projects/${id}`, { method: "DELETE" }),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["projects"] })
  });

  const analyzeMutation = useMutation({
    mutationFn: (id: string) => fetchWithAuth(`/projects/${id}/analyze`, { method: "POST" }),
    onSuccess: (data, id) => {
      setAnalyzingIds((prev) => [...prev, id]);
      queryClient.invalidateQueries({ queryKey: ["projects"] });
    },
    onError: (err: any) => {
      setError(err.message || "Failed to trigger repo analysis.");
    }
  });

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (projectName) {
      createProjectMutation.mutate({ name: projectName, description: projectDesc });
    }
  };

  const handleGithubImport = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!githubUrl.includes("github.com")) {
      setError("Please input a valid GitHub repository URL.");
      return;
    }

    try {
      // 1. Create a project record first
      const ownerRepo = githubUrl.split("github.com/")[1]?.split("/");
      const repoName = ownerRepo && ownerRepo[1] ? ownerRepo[1] : "Imported Repository";
      
      const newProj = await fetchWithAuth("/projects", {
        method: "POST",
        body: JSON.stringify({
          name: repoName,
          description: "Imported via GitHub URL integration.",
          github_url: githubUrl
        })
      });

      // 2. Trigger analysis
      analyzeMutation.mutate(newProj.id);
      setGithubUrl("");
    } catch (err: any) {
      setError(err.message || "Failed to import repository.");
    }
  };

  return (
    <div className="flex flex-col gap-8">
      {/* Page Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h2 className="text-2xl md:text-3xl font-extrabold text-white">Projects Vault</h2>
          <p className="text-sm text-slate-400 mt-1">Import and analyze your code repositories to automatically extract metrics and action bullets.</p>
        </div>
      </div>

      {error && (
        <div className="bg-rose-950/30 border border-rose-900 text-rose-300 text-xs py-3 px-4 rounded-xl flex items-center gap-2 max-w-xl">
          <AlertCircle size={16} />
          {error}
        </div>
      )}

      {/* Grid: Forms on Left (1 column), Projects List on Right (2 columns) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left column: Add/Import Panel */}
        <div className="flex flex-col gap-6">
          {/* GitHub Importer */}
          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="font-bold text-white mb-2 flex items-center gap-2 text-sm">
              <Github size={16} className="text-indigo-400" />
              Import from GitHub
            </h3>
            <p className="text-xs text-slate-400 mb-4">Provide your repository URL to perform containerized AI analysis of dependencies and config files.</p>
            
            <form onSubmit={handleGithubImport} className="flex flex-col gap-3">
              <input
                type="url"
                value={githubUrl}
                onChange={(e) => setGithubUrl(e.target.value)}
                placeholder="https://github.com/owner/repo"
                className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-indigo-500"
                required
              />
              <button
                type="submit"
                disabled={analyzeMutation.isPending}
                className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2.5 rounded-xl text-xs flex items-center justify-center gap-2 transition-colors"
              >
                {analyzeMutation.isPending ? (
                  <Loader2 className="animate-spin" size={14} />
                ) : (
                  <>Import \& Analyze</>
                )}
              </button>
            </form>
          </div>

          {/* Manual Project Creator */}
          <div className="glass-panel p-6 rounded-2xl">
            <h3 className="font-bold text-white mb-2 flex items-center gap-2 text-sm">
              <Plus size={16} className="text-purple-400" />
              Add Manual Project
            </h3>
            <p className="text-xs text-slate-400 mb-4">Register projects that are not hosted on GitHub to include them in the matching system.</p>

            <form onSubmit={handleManualSubmit} className="flex flex-col gap-3">
              <input
                type="text"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                placeholder="Project Name"
                className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-indigo-500"
                required
              />
              <textarea
                value={projectDesc}
                onChange={(e) => setProjectDesc(e.target.value)}
                placeholder="Project Description"
                rows={3}
                className="bg-slate-900 border border-slate-800 rounded-xl p-3 text-xs text-white focus:outline-none focus:border-indigo-500"
              />
              <button
                type="submit"
                disabled={createProjectMutation.isPending}
                className="bg-purple-600 hover:bg-purple-500 text-white font-medium py-2.5 rounded-xl text-xs transition-colors"
              >
                Save Project
              </button>
            </form>
          </div>
        </div>

        {/* Right column: Vault List */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <h3 className="font-bold text-white">Vault Records ({projects.length})</h3>

          {isLoading ? (
            <div className="flex justify-center items-center py-24">
              <Loader2 className="animate-spin text-indigo-400" size={32} />
            </div>
          ) : projects.length === 0 ? (
            <div className="glass-card p-12 text-center rounded-2xl">
              <Cpu className="mx-auto text-slate-600 mb-3" size={36} />
              <p className="text-sm text-slate-400">Your Projects Vault is empty.</p>
              <p className="text-xs text-slate-500 mt-1">Import a project above to configure optimized LaTeX resume bullets.</p>
            </div>
          ) : (
            <div className="flex flex-col gap-4">
              {projects.map((proj: any) => {
                const isAnalyzing = !proj.analysis && analyzingIds.includes(proj.id);
                return (
                  <motion.div
                    key={proj.id}
                    layout
                    className="glass-card p-5 rounded-2xl flex flex-col gap-4 relative overflow-hidden"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <h4 className="font-bold text-white text-base flex items-center gap-2">
                          {proj.name}
                          {proj.github_url && (
                            <a href={proj.github_url} target="_blank" rel="noopener noreferrer" className="text-slate-500 hover:text-white">
                              <ExternalLink size={14} />
                            </a>
                          )}
                        </h4>
                        <p className="text-xs text-slate-400 mt-1">{proj.description}</p>
                      </div>
                      <button
                        onClick={() => deleteProjectMutation.mutate(proj.id)}
                        className="text-rose-400 hover:text-rose-300 p-2"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>

                    {/* Analysis Status banner */}
                    {proj.github_url && (
                      <div className="border-t border-slate-800/60 pt-4 mt-2">
                        {isAnalyzing ? (
                          <div className="flex items-center gap-2 text-xs text-indigo-400 bg-indigo-950/20 py-2.5 px-4 rounded-xl border border-indigo-900/40">
                            <Loader2 className="animate-spin" size={14} />
                            <span>Repository analysis in progress... polling results.</span>
                          </div>
                        ) : proj.analysis ? (
                          <div className="flex flex-col gap-3">
                            <div className="flex justify-between items-center bg-slate-900/60 p-3 rounded-xl border border-slate-800">
                              <div className="flex flex-col gap-0.5">
                                <span className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold">AI COMPLEXITY</span>
                                <span className="text-xs text-white font-bold">{proj.analysis.complexity_score} / 10</span>
                              </div>
                              <div className="flex flex-col gap-0.5 text-right">
                                <span className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold font-bold">STATUS</span>
                                <span className="text-xs text-emerald-400 font-bold flex items-center gap-1">
                                  <CheckCircle2 size={12} /> Optimized
                                </span>
                              </div>
                            </div>
                            
                            <div>
                              <span className="text-[10px] text-slate-500 uppercase tracking-widest font-semibold block mb-1">Simulated Action Bullets</span>
                              <ul className="list-disc pl-5 flex flex-col gap-1">
                                {proj.analysis.bullets.map((b: string, i: number) => (
                                  <li key={i} className="text-xs text-slate-300 leading-relaxed">{b}</li>
                                ))}
                              </ul>
                            </div>

                            <div className="flex flex-wrap gap-1 mt-1">
                              {proj.analysis.technologies.map((t: string, i: number) => (
                                <span key={i} className="bg-indigo-950/20 border border-indigo-900/40 text-indigo-400 text-[10px] py-0.5 px-2 rounded-full font-semibold">
                                  {t}
                                </span>
                              ))}
                            </div>
                          </div>
                        ) : (
                          <button
                            onClick={() => analyzeMutation.mutate(proj.id)}
                            className="bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 border border-indigo-900/30 py-1.5 px-3 rounded-xl text-xs font-semibold flex items-center gap-1.5 transition-colors"
                          >
                            <Cpu size={12} /> Trigger AI Analysis
                          </button>
                        )}
                      </div>
                    )}
                  </motion.div>
                );
              })}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
