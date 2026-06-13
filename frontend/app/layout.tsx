"use client";

import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import "./globals.css";
import Link from "next/link";
import { useStore } from "../store/useStore";
import { LogOut, LayoutDashboard, User, Github, FileText, Settings, Award } from "lucide-react";

// Initialize QueryClient
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased min-h-screen flex flex-col">
        <QueryClientProvider client={queryClient}>
          <AppShell>{children}</AppShell>
        </QueryClientProvider>
      </body>
    </html>
  );
}

function AppShell({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, logout, user } = useStore();

  return (
    <div className="flex flex-col min-h-screen bg-[#0b0f19] text-slate-100">
      {/* Top Navbar */}
      <nav className="glass-panel sticky top-0 z-50 px-6 py-4 flex justify-between items-center">
        <Link href="/" className="text-xl font-bold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-purple-400">
          Resume Intelligence
        </Link>
        
        {isAuthenticated ? (
          <div className="flex items-center gap-6">
            <span className="text-sm text-slate-400 hidden md:inline">Logged in: {user?.email}</span>
            <button 
              onClick={() => {
                logout();
                window.location.href = "/auth/login";
              }}
              className="flex items-center gap-2 text-sm text-rose-400 hover:text-rose-300 transition-colors"
            >
              <LogOut size={16} />
              Logout
            </button>
          </div>
        ) : (
          <div className="flex gap-4">
            <Link href="/auth/login" className="text-sm text-slate-300 hover:text-white transition-colors py-2 px-4 rounded-lg">
              Login
            </Link>
            <Link href="/auth/signup" className="text-sm bg-indigo-600 hover:bg-indigo-500 py-2 px-4 rounded-lg font-medium transition-all shadow-md shadow-indigo-600/30">
              Get Started
            </Link>
          </div>
        )}
      </nav>

      {/* Main Workspace Layout */}
      <div className="flex flex-1">
        {/* Sidebar for authenticated users */}
        {isAuthenticated && (
          <aside className="w-64 glass-panel border-t-0 border-l-0 hidden md:flex flex-col gap-2 p-4">
            <SidebarLink href="/dashboard" icon={<LayoutDashboard size={18} />} label="Dashboard" />
            <SidebarLink href="/profile" icon={<User size={18} />} label="Master Profile" />
            <SidebarLink href="/projects" icon={<Github size={18} />} label="Projects Vault" />
            <SidebarLink href="/generate" icon={<Award size={18} />} label="Generate Resume" />
            <SidebarLink href="/resumes" icon={<FileText size={18} />} label="Resumes History" />
            <SidebarLink href="/settings" icon={<Settings size={18} />} label="Settings" />
            
            {user?.is_admin && (
              <div className="mt-8 pt-4 border-t border-slate-800">
                <p className="text-xs font-bold text-slate-500 uppercase tracking-widest px-3 mb-2">Admin</p>
                <SidebarLink href="/admin" icon={<Settings size={18} />} label="Console Panel" />
              </div>
            )}
          </aside>
        )}

        {/* Content Area */}
        <main className="flex-1 p-6 md:p-10 max-w-7xl mx-auto w-full">
          {children}
        </main>
      </div>

      {/* Footer */}
      <footer className="border-t border-slate-900 py-6 text-center text-xs text-slate-600">
        © 2026 Resume Intelligence Platform. All rights reserved.
      </footer>
    </div>
  );
}

function SidebarLink({ href, icon, label }: { href: string; icon: React.ReactNode; label: string }) {
  return (
    <Link href={href} className="flex items-center gap-3 py-3 px-4 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800/40 transition-all">
      {icon}
      <span className="text-sm font-medium">{label}</span>
    </Link>
  );
}
