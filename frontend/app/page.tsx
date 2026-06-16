import Link from "next/link";

export default function Home() {
  return (
    <div className="relative min-h-screen bg-[#020617] text-white flex flex-col justify-center items-center overflow-hidden">
      {/* Background radial glowing effects */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-[#0ea5e9]/10 rounded-full blur-[150px]" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-[#0d9488]/10 rounded-full blur-[150px]" />
      
      {/* Grid overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-35" />

      <div className="relative z-10 max-w-5xl px-6 text-center flex flex-col items-center">
        {/* Header Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-sky-500/30 bg-sky-950/20 text-sky-400 text-xs font-semibold uppercase tracking-wider mb-6 animate-pulse">
          ⚡ BuildWise AI - Phase 1 MVP
        </div>

        {/* Hero Title */}
        <h1 className="text-5xl md:text-7xl font-bold tracking-tight bg-gradient-to-r from-sky-400 via-teal-300 to-indigo-500 bg-clip-text text-transparent mb-6">
          Your AI CTO Platform <br/> Powered by Agentic AI
        </h1>

        {/* Subtitle */}
        <p className="text-lg md:text-xl text-slate-400 max-w-2xl mb-10 leading-relaxed">
          Transform simple software ideas into production-ready technical specifications, database schemas, REST APIs, logo portfolios, and consultant-grade reports in seconds.
        </p>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 mb-16">
          <Link href="/login" className="px-8 py-4 rounded-xl font-semibold bg-gradient-to-r from-sky-500 to-teal-500 hover:from-sky-400 hover:to-teal-400 text-slate-950 transition duration-300 transform hover:scale-105 shadow-[0_0_20px_rgba(14,165,233,0.4)]">
            Get Started Free
          </Link>
          <Link href="/login" className="px-8 py-4 rounded-xl font-semibold border border-slate-700 bg-slate-900/50 hover:bg-slate-800/80 transition duration-300">
            Sign In Account
          </Link>
        </div>

        {/* 3 Grid Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full max-w-4xl">
          <div className="glass-panel p-6 rounded-2xl text-left">
            <div className="w-10 h-10 rounded-lg bg-sky-500/10 flex items-center justify-center text-sky-400 mb-4 font-bold text-lg">
              01
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Multi-Agent LangGraph</h3>
            <p className="text-slate-400 text-sm">
              7 specialized agents (Architects, SecOps, API Designers) validate your spec through strict Judge iteration loops.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-2xl text-left">
            <div className="w-10 h-10 rounded-lg bg-teal-500/10 flex items-center justify-center text-teal-400 mb-4 font-bold text-lg">
              02
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Design RAG Engine</h3>
            <p className="text-slate-400 text-sm">
              Retrieves standard guidelines from documentation bases (FastAPI, Postgres, System Design) for accurate details.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-2xl text-left">
            <div className="w-10 h-10 rounded-lg bg-indigo-500/10 flex items-center justify-center text-indigo-400 mb-4 font-bold text-lg">
              03
            </div>
            <h3 className="text-lg font-semibold text-white mb-2">Studio Logo & Mocks</h3>
            <p className="text-slate-400 text-sm">
              Generate fully-compliant SVG branding sets, screen routes, and export PDF reports instantly.
            </p>
          </div>
        </div>
      </div>
      
      {/* Footer */}
      <footer className="absolute bottom-6 text-xs text-slate-600">
        © {new Date().getFullYear()} BuildWise AI. All rights reserved. Commercial In Confidence.
      </footer>
    </div>
  );
}
