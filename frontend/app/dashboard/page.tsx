"use client";

import React from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchWithAuth } from "../../lib/api/client";
import { useStore } from "../../store/useStore";
import { motion } from "framer-motion";
import { FileText, Cpu, CheckCircle2, ChevronRight, BarChart2, PlusCircle, Sparkles } from "lucide-react";
import Link from "next/link";

export default function DashboardPage() {
  const { user } = useStore();

  // Queries
  const { data: resumes = [], isLoading: loadingResumes } = useQuery({
    queryKey: ["resumes"],
    queryFn: () => fetchWithAuth("/resume"),
  });

  const { data: projects = [], isLoading: loadingProjects } = useQuery({
    queryKey: ["projects"],
    queryFn: () => fetchWithAuth("/projects"),
  });

  const { data: profile, error: profileError } = useQuery({
    queryKey: ["profile"],
    queryFn: () => fetchWithAuth("/profile"),
    retry: false,
  });

  const profileSetup = !!profile && !profileError;

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 10 },
    show: { opacity: 1, y: 0 },
  };

  return (
    <motion.div 
      variants={containerVariants}
      initial="hidden"
      animate="show"
      className="flex flex-col gap-8"
    >
      {/* Top Banner Greeting */}
      <motion.div variants={itemVariants} className="glass-panel p-8 rounded-3xl relative overflow-hidden">
        <div className="absolute right-10 bottom-0 opacity-10 text-indigo-400 pointer-events-none">
          <Sparkles size={200} />
        </div>
        <h2 className="text-2xl md:text-3xl font-extrabold text-white">
          Hello, {profile?.full_name || user?.email.split("@")[0]}
        </h2>
        <p className="text-sm text-slate-400 mt-2 max-w-xl">
          Welcome to your career command center. Optimize your resume for target job descriptions and scan compatibility score instantly.
        </p>
      </motion.div>

      {/* Profile Checklist banner if profile not setup */}
      {!profileSetup && (
        <motion.div variants={itemVariants} className="bg-indigo-950/20 border border-indigo-900/60 p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <h4 className="font-bold text-white text-sm md:text-base">Complete Your Master Profile</h4>
            <p className="text-xs text-slate-400 mt-1">To optimize resumes, you need to populate your contact, education, and experience details first.</p>
          </div>
          <Link href="/profile" className="bg-indigo-600 hover:bg-indigo-500 py-2 px-4 rounded-xl text-xs font-semibold text-center whitespace-nowrap transition-colors">
            Setup Master Profile
          </Link>
        </motion.div>
      )}

      {/* Grid Stats */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="glass-card p-6 rounded-2xl flex items-center gap-4">
          <div className="p-4 bg-indigo-950/40 border border-indigo-900/40 rounded-xl text-indigo-400">
            <FileText size={24} />
          </div>
          <div>
            <span className="text-xs text-slate-400 block font-medium">Optimized Resumes</span>
            <span className="text-2xl font-bold text-white mt-1 block">{loadingResumes ? "..." : resumes.length}</span>
          </div>
        </div>

        <div className="glass-card p-6 rounded-2xl flex items-center gap-4">
          <div className="p-4 bg-purple-950/40 border border-purple-900/40 rounded-xl text-purple-400">
            <Cpu size={24} />
          </div>
          <div>
            <span className="text-xs text-slate-400 block font-medium">Projects Vault</span>
            <span className="text-2xl font-bold text-white mt-1 block">{loadingProjects ? "..." : projects.length}</span>
          </div>
        </div>

        <div className="glass-card p-6 rounded-2xl flex items-center gap-4">
          <div className="p-4 bg-emerald-950/40 border border-emerald-900/40 rounded-xl text-emerald-400">
            <CheckCircle2 size={24} />
          </div>
          <div>
            <span className="text-xs text-slate-400 block font-medium">Account Standing</span>
            <span className="text-base font-bold text-emerald-400 mt-1 block">Active (Free Tier)</span>
          </div>
        </div>
      </motion.div>

      {/* Content split - Recent generations vs Quick Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Recent Resume Runs */}
        <motion.div variants={itemVariants} className="lg:col-span-2 glass-panel p-6 rounded-2xl flex flex-col gap-4">
          <div className="flex justify-between items-center pb-2 border-b border-slate-800">
            <h3 className="font-bold text-white">Recent Optimizations</h3>
            <Link href="/resumes" className="text-xs text-indigo-400 hover:underline flex items-center gap-1">
              View History <ChevronRight size={14} />
            </Link>
          </div>

          {loadingResumes ? (
            <p className="text-sm text-slate-500 py-6 text-center">Loading histories...</p>
          ) : resumes.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-sm text-slate-400">No optimized resumes generated yet.</p>
              <Link href="/generate" className="mt-4 inline-flex items-center gap-2 bg-indigo-600/10 hover:bg-indigo-600/20 text-indigo-400 border border-indigo-900/30 text-xs py-2 px-4 rounded-xl transition-all">
                <PlusCircle size={14} /> Optimize first resume
              </Link>
            </div>
          ) : (
            <div className="flex flex-col gap-3">
              {resumes.slice(0, 3).map((res: any) => (
                <div key={res.id} className="glass-card p-4 rounded-xl flex justify-between items-center text-sm">
                  <div className="flex flex-col gap-1">
                    <span className="font-medium text-white">Generation Run</span>
                    <span className="text-xs text-slate-500">Status: <span className="text-indigo-400 font-semibold uppercase">{res.status}</span></span>
                  </div>
                  {res.status === "completed" && (
                    <Link href={`/resumes`} className="text-xs text-indigo-400 hover:underline">
                      Manage PDF
                    </Link>
                  )}
                </div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Right: Quick shortcuts */}
        <motion.div variants={itemVariants} className="glass-panel p-6 rounded-2xl flex flex-col gap-4">
          <h3 className="font-bold text-white pb-2 border-b border-slate-800">Quick Console</h3>
          <div className="flex flex-col gap-3">
            <Link href="/generate" className="glass-card p-4 rounded-xl flex items-center justify-between text-sm group">
              <span className="font-medium text-slate-300 group-hover:text-white transition-colors">Compile Optimized Resume</span>
              <ChevronRight size={16} className="text-slate-500 group-hover:text-indigo-400 transition-colors" />
            </Link>

            <Link href="/projects" className="glass-card p-4 rounded-xl flex items-center justify-between text-sm group">
              <span className="font-medium text-slate-300 group-hover:text-white transition-colors">Import GitHub Repository</span>
              <ChevronRight size={16} className="text-slate-500 group-hover:text-indigo-400 transition-colors" />
            </Link>

            <Link href="/profile" className="glass-card p-4 rounded-xl flex items-center justify-between text-sm group">
              <span className="font-medium text-slate-300 group-hover:text-white transition-colors">Update Master Profile</span>
              <ChevronRight size={16} className="text-slate-500 group-hover:text-indigo-400 transition-colors" />
            </Link>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
