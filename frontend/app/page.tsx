"use client";

import React, { useState } from "react";
import { motion } from "framer-motion";
import { ArrowRight, CheckCircle, Cpu, FileCheck, Layers } from "lucide-react";
import Link from "next/link";

export default function LandingPage() {
  const [waitlistEmail, setWaitlistEmail] = useState("");
  const [registered, setRegistered] = useState(false);

  const handleWaitlistSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (waitlistEmail.trim()) {
      setRegistered(true);
      setWaitlistEmail("");
    }
  };

  return (
    <div className="flex flex-col items-center justify-center py-12 md:py-24 text-center">
      {/* Hero Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        className="max-w-3xl"
      >
        <span className="px-3 py-1 text-xs font-semibold text-indigo-400 bg-indigo-950/40 border border-indigo-900 rounded-full inline-block mb-4">
          Powered by Advanced Agentic AI
        </span>
        <h1 className="text-4xl md:text-6xl font-extrabold tracking-tight leading-tight">
          Create One Master Profile. <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400">
            Generate Optimized Resumes.
          </span>
        </h1>
        <p className="mt-6 text-lg text-slate-400 max-w-xl mx-auto">
          Tailor resumes and cover letters specifically for any job description in seconds. Optimize for ATS and compile server-side using professional LaTeX templates.
        </p>

        <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/auth/signup"
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-3 px-8 rounded-xl flex items-center justify-center gap-2 transition-all shadow-lg shadow-indigo-600/30 hover:scale-[1.02]"
          >
            Create Your Account
            <ArrowRight size={18} />
          </Link>
          <a
            href="#features"
            className="glass-card hover:bg-slate-800/20 py-3 px-8 rounded-xl font-medium flex items-center justify-center transition-colors"
          >
            Explore Features
          </a>
        </div>
      </motion.div>

      {/* Feature cards Grid */}
      <motion.div
        id="features"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.8, delay: 0.2 }}
        className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-24 max-w-5xl w-full text-left"
      >
        <div className="glass-card p-6 rounded-2xl flex flex-col gap-4">
          <div className="p-3 bg-indigo-950/40 border border-indigo-950 rounded-xl text-indigo-400 w-fit">
            <Cpu size={24} />
          </div>
          <h3 className="text-lg font-bold text-white">Multi-AI Adaptability</h3>
          <p className="text-sm text-slate-400">
            Bring your own API key (GPT-4o, Claude 3.5, Gemini, DeepSeek). Encrypted safely via Fernet cryptography keys.
          </p>
        </div>

        <div className="glass-card p-6 rounded-2xl flex flex-col gap-4">
          <div className="p-3 bg-purple-950/40 border border-purple-950 rounded-xl text-purple-400 w-fit">
            <Layers size={24} />
          </div>
          <h3 className="text-lg font-bold text-white">LaTeX Compilation</h3>
          <p className="text-sm text-slate-400">
            Production grade server-side XeLaTeX compilation. Delivers publication-quality PDF assets with zero parsing errors.
          </p>
        </div>

        <div className="glass-card p-6 rounded-2xl flex flex-col gap-4">
          <div className="p-3 bg-pink-950/40 border border-pink-950 rounded-xl text-pink-400 w-fit">
            <FileCheck size={24} />
          </div>
          <h3 className="text-lg font-bold text-white">Deterministic ATS Scorer</h3>
          <p className="text-sm text-slate-400">
            Scan documents through an objective scoring module matching action verbs, format checks, and JD keywords.
          </p>
        </div>
      </motion.div>

      {/* Waitlist Call-to-action */}
      <div className="glass-panel p-8 md:p-12 rounded-3xl mt-24 max-w-2xl w-full">
        <h3 className="text-xl md:text-2xl font-bold text-white">Join the Premium Waitlist</h3>
        <p className="text-sm text-slate-400 mt-2">
          Get notified when new features, custom templates, and AI resume models are released.
        </p>

        <form onSubmit={handleWaitlistSubmit} className="mt-6 flex flex-col sm:flex-row gap-3">
          <input
            type="email"
            value={waitlistEmail}
            onChange={(e) => setWaitlistEmail(e.target.value)}
            placeholder="Enter your email"
            className="flex-1 bg-slate-900 border border-slate-800 rounded-xl py-3 px-4 text-white placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            required
            disabled={registered}
          />
          <button
            type="submit"
            disabled={registered}
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-3 px-6 rounded-xl transition-all shadow-md shadow-indigo-600/25 disabled:bg-indigo-850"
          >
            {registered ? "Registered!" : "Notify Me"}
          </button>
        </form>
        {registered && (
          <p className="text-xs text-indigo-400 mt-3 flex items-center justify-center gap-1">
            <CheckCircle size={14} /> Thank you! You've been successfully added to our waiting list.
          </p>
        )}
      </div>
    </div>
  );
}
