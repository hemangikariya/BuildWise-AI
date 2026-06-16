"use client";

import { useEffect, useState, useRef, use } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { 
  ArrowLeft, Download, Send, CheckCircle, Clock, Loader2, AlertTriangle, 
  Briefcase, Code, FileText, Database, ShieldAlert, Cpu, Eye, Image as ImageIcon 
} from "lucide-react";

interface AgentStatus {
  agent: string;
  status: string;
  error?: string;
}

interface ChatMessage {
  id: string;
  role: string;
  message: string;
  created_at: string;
}

export default function ProjectWorkspacePage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const { id: projectId } = use(params);
  
  // Project & Version state
  const [project, setProject] = useState<any>(null);
  const [latestVersion, setLatestVersion] = useState<any>(null);
  
  // UI Tab state
  const [activeTab, setActiveTab] = useState("specs"); // specs, logo, ui, chat
  const [activeSpecSection, setActiveSpecSection] = useState("summary"); // summary, architecture, database, api, security
  
  // Real-time SSE Agent status state
  const [isGenerating, setIsGenerating] = useState(false);
  const [progress, setProgress] = useState(0);
  const [agentRuns, setAgentRuns] = useState<AgentStatus[]>([]);
  const [generationError, setGenerationError] = useState("");
  
  // CTO Chat state
  const [chats, setChats] = useState<ChatMessage[]>([]);
  const [message, setMessage] = useState("");
  const [chatLoading, setChatLoading] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  
  // Logo Studio state
  const [logoData, setLogoData] = useState<any>(null);
  const [logoLoading, setLogoLoading] = useState(false);
  const [activeLogoMode, setActiveLogoMode] = useState("light"); // light, dark, icon
  const canvasRef = useRef<HTMLCanvasElement>(null);

  // UI Generator state
  const [uiData, setUiData] = useState<any>(null);
  const [uiLoading, setUiLoading] = useState(false);

  // Fetch project basic details
  const fetchProjectDetails = async () => {
    try {
      const res = await api.get(`/projects/${projectId}`);
      setProject(res.data);
    } catch (err) {
      console.error("Failed to load project details", err);
      router.push("/dashboard");
    }
  };

  // Fetch latest compiled version if any
  const fetchLatestVersion = async () => {
    try {
      const res = await api.get(`/projects/${projectId}/versions`);
      if (res.data.length > 0) {
        // Find most recent completed version
        const latest = res.data[0];
        if (latest.output_data && Object.keys(latest.output_data).length > 0) {
          setLatestVersion(latest);
        }
      }
    } catch (err) {
      console.error("Failed to fetch versions", err);
    }
  };

  // Fetch chats
  const fetchChats = async () => {
    try {
      const res = await api.get(`/projects/${projectId}/chats`);
      setChats(res.data);
    } catch (err) {
      console.error("Failed to fetch chats", err);
    }
  };

  useEffect(() => {
    fetchProjectDetails();
    fetchLatestVersion();
    fetchChats();
  }, [projectId]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chats]);

  // Starts the LangGraph multi-agent run
  const handleStartGeneration = async () => {
    setIsGenerating(true);
    setGenerationError("");
    setProgress(0);
    setAgentRuns([]);

    try {
      const res = await api.post(`/projects/${projectId}/generate`);
      const { version_id } = res.data;

      // Connect to Server-Sent Events (SSE) stream
      const eventSource = new EventSource(`${api.defaults.baseURL}/projects/${projectId}/versions/${version_id}/stream`);

      eventSource.addEventListener("progress", (event: any) => {
        const payload = JSON.parse(event.data);
        setProgress(payload.progress);
        setAgentRuns(payload.agents);
      });

      eventSource.addEventListener("complete", (event: any) => {
        setIsGenerating(false);
        eventSource.close();
        fetchLatestVersion();
      });

      eventSource.addEventListener("failed", (event: any) => {
        setIsGenerating(false);
        setGenerationError("Agent validation failed or Judge rejected plan after max attempts.");
        eventSource.close();
      });

      eventSource.addEventListener("error", (event: any) => {
        console.error("SSE stream error", event);
        setIsGenerating(false);
        setGenerationError("A network error occurred while streaming agent logs.");
        eventSource.close();
      });

    } catch (err: any) {
      console.error("Failed to launch workflow", err);
      setIsGenerating(false);
      setGenerationError(err.response?.data?.detail || "Failed to initiate technical plan generation.");
    }
  };

  // Handle virtual CTO chat message submission
  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || chatLoading) return;

    const userText = message;
    setMessage("");
    setChatLoading(true);
    
    // Optimistic state update
    const tempChat: ChatMessage = {
      id: Math.random().toString(),
      role: "user",
      message: userText,
      created_at: new Date().toISOString()
    };
    setChats(prev => [...prev, tempChat]);

    try {
      const res = await api.post(`/projects/${projectId}/chat`, { message: userText });
      setChats(prev => [...prev.filter(c => c.id !== tempChat.id), tempChat, res.data]);
    } catch (err) {
      console.error("Chat consult failed", err);
    } finally {
      setChatLoading(false);
    }
  };

  // Generate Logo Branding Package
  const handleGenerateLogoPackage = async () => {
    setLogoLoading(true);
    try {
      const res = await api.post("/logo-studio/generate", { idea: project.description || project.title });
      setLogoData(res.data);
    } catch (err) {
      console.error("Branding failed", err);
    } finally {
      setLogoLoading(false);
    }
  };

  // Generate UI Blueprint
  const handleGenerateUIBlueprint = async () => {
    setUiLoading(true);
    try {
      const res = await api.post("/ui-generator/generate", { idea: project.description || project.title });
      setUiData(res.data);
    } catch (err) {
      console.error("UI Generator failed", err);
    } finally {
      setUiLoading(false);
    }
  };

  // Download raw SVG Logo
  const downloadLogoSVG = () => {
    if (!logoData) return;
    const svgContent = activeLogoMode === "light" 
      ? logoData.logo_svg_light 
      : activeLogoMode === "dark" 
        ? logoData.logo_svg_dark 
        : logoData.logo_svg_icon;

    const blob = new Blob([svgContent], { type: "image/svg+xml" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `logo_${activeLogoMode}.svg`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  // Export SVG to PNG using HTML5 Canvas client side
  const exportLogoPNG = () => {
    if (!logoData) return;
    const svgContent = activeLogoMode === "light" 
      ? logoData.logo_svg_light 
      : activeLogoMode === "dark" 
        ? logoData.logo_svg_dark 
        : logoData.logo_svg_icon;

    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const img = new Image();
    const svgBlob = new Blob([svgContent], { type: "image/svg+xml;charset=utf-8" });
    const url = URL.createObjectURL(svgBlob);

    img.onload = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      
      const pngUrl = canvas.toDataURL("image/png");
      const a = document.createElement("a");
      a.href = pngUrl;
      a.download = `logo_${activeLogoMode}.png`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    };
    img.src = url;
  };

  return (
    <div className="relative min-h-screen bg-[#020617] text-white flex flex-col overflow-hidden">
      {/* Background gradients */}
      <div className="absolute top-[-10%] left-[-10%] w-[35%] h-[35%] bg-[#0ea5e9]/5 rounded-full blur-[110px]" />
      
      <header className="relative z-10 border-b border-slate-800 bg-slate-950/45 backdrop-blur-md px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push("/dashboard")}
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-white transition"
          >
            <ArrowLeft size={16} />
          </button>
          <div>
            <h1 className="text-lg font-bold text-white leading-none mb-1">
              {project ? project.title : "Workspace"}
            </h1>
            <p className="text-slate-400 text-xs truncate max-w-[300px]">
              {project ? project.description : ""}
            </p>
          </div>
        </div>

        {latestVersion && (
          <a
            href={`${api.defaults.baseURL}/reports/${latestVersion.id}/pdf`}
            download
            className="px-4 py-2 rounded-xl border border-slate-700 bg-slate-900/50 hover:bg-slate-800 text-xs font-semibold flex items-center gap-1.5 transition text-sky-400"
          >
            <Download size={14} />
            Export Spec PDF
          </a>
        )}
      </header>

      <div className="flex-grow flex flex-col md:flex-row relative z-10">
        
        {/* LEFT COLUMN: Controls & Generation State / Navigation Tabs */}
        <div className="w-full md:w-[350px] border-r border-slate-800/80 bg-slate-950/30 p-6 flex flex-col gap-6">
          
          {/* Action trigger button */}
          {!latestVersion && !isGenerating && (
            <div className="p-5 rounded-2xl bg-sky-950/20 border border-sky-500/20 text-center">
              <Cpu size={36} className="mx-auto text-sky-400 mb-3" />
              <h3 className="font-semibold mb-1 text-sm">Design Blueprint Pending</h3>
              <p className="text-slate-400 text-xs mb-4">Run the AI Agent system to construct architectures, specs, and database designs.</p>
              <button
                onClick={handleStartGeneration}
                className="w-full py-2.5 rounded-xl font-semibold bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs transition"
              >
                Generate Blueprint
              </button>
            </div>
          )}

          {/* SSE Generation Progression Visualizer */}
          {(isGenerating || agentRuns.length > 0) && (
            <div className="glass-panel p-5 rounded-2xl space-y-4">
              <div className="flex justify-between items-center text-xs font-semibold">
                <span>Agent Pipeline Runs</span>
                <span className="text-sky-400">{Math.round(progress * 100)}%</span>
              </div>
              
              {/* Progress bar */}
              <div className="w-full h-1.5 rounded-full bg-slate-800 overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-sky-500 to-teal-500 transition-all duration-500" 
                  style={{ width: `${progress * 100}%` }}
                />
              </div>

              {/* Individual Agents Status */}
              <div className="space-y-3 pt-2">
                {agentRuns.map((r, i) => (
                  <div key={i} className="flex items-center justify-between text-xs">
                    <span className="text-slate-300">{r.agent}</span>
                    <div className="flex items-center gap-1.5">
                      {r.status === "COMPLETED" && <CheckCircle size={14} className="text-emerald-400" />}
                      {r.status === "PENDING" && <Clock size={14} className="text-slate-600" />}
                      {r.status === "RUNNING" && <Loader2 size={14} className="text-sky-400 animate-spin" />}
                      {r.status === "FAILED" && <AlertTriangle size={14} className="text-rose-400" />}
                      <span className={`capitalize ${r.status === "COMPLETED" ? "text-emerald-400" : r.status === "RUNNING" ? "text-sky-400 font-semibold" : r.status === "FAILED" ? "text-rose-400" : "text-slate-600"}`}>
                        {r.status.toLowerCase()}
                      </span>
                    </div>
                  </div>
                ))}
              </div>

              {generationError && (
                <div className="p-3 rounded-lg bg-rose-950/40 border border-rose-500/20 text-rose-400 text-[10px] mt-2">
                  {generationError}
                </div>
              )}
            </div>
          )}

          {/* spec menu tabs */}
          {latestVersion && (
            <nav className="flex flex-col gap-2">
              <button
                onClick={() => setActiveTab("specs")}
                className={`px-4 py-3 rounded-xl text-left text-xs font-semibold flex items-center gap-2.5 transition ${activeTab === "specs" ? "bg-sky-500/10 text-sky-400 border border-sky-500/20" : "hover:bg-slate-900 text-slate-400 hover:text-white"}`}
              >
                <FileText size={16} />
                Technical Spec Sheets
              </button>
              <button
                onClick={() => {
                  setActiveTab("logo");
                  if (!logoData) handleGenerateLogoPackage();
                }}
                className={`px-4 py-3 rounded-xl text-left text-xs font-semibold flex items-center gap-2.5 transition ${activeTab === "logo" ? "bg-sky-500/10 text-sky-400 border border-sky-500/20" : "hover:bg-slate-900 text-slate-400 hover:text-white"}`}
              >
                <ImageIcon size={16} />
                Branding Logo Studio
              </button>
              <button
                onClick={() => {
                  setActiveTab("ui");
                  if (!uiData) handleGenerateUIBlueprint();
                }}
                className={`px-4 py-3 rounded-xl text-left text-xs font-semibold flex items-center gap-2.5 transition ${activeTab === "ui" ? "bg-sky-500/10 text-sky-400 border border-sky-500/20" : "hover:bg-slate-900 text-slate-400 hover:text-white"}`}
              >
                <Code size={16} />
                UX/UI Wireframe Generator
              </button>
              <button
                onClick={() => setActiveTab("chat")}
                className={`px-4 py-3 rounded-xl text-left text-xs font-semibold flex items-center gap-2.5 transition ${activeTab === "chat" ? "bg-sky-500/10 text-sky-400 border border-sky-500/20" : "hover:bg-slate-900 text-slate-400 hover:text-white"}`}
              >
                <Cpu size={16} />
                CTO Chat Consultation
              </button>
            </nav>
          )}

          {latestVersion && !isGenerating && (
            <button
              onClick={handleStartGeneration}
              className="mt-auto w-full py-2.5 rounded-xl font-semibold border border-slate-800 bg-slate-900 hover:bg-slate-800 text-xs transition"
            >
              Re-generate Blueprint
            </button>
          )}
        </div>

        {/* RIGHT COLUMN: Tab Panel Outputs */}
        <div className="flex-grow bg-[#090d1f] p-8 overflow-y-auto max-h-[calc(100vh-73px)]">
          {!latestVersion ? (
            <div className="h-full flex flex-col items-center justify-center text-slate-500 text-sm py-20">
              {isGenerating ? "Compiling tech specifications with Judge iteration loops..." : "Start generation to load specifications."}
            </div>
          ) : (
            <>
              {/* SPECIFICATION TAB */}
              {activeTab === "specs" && (
                <div className="space-y-6">
                  {/* Internal spec sub-navigation */}
                  <div className="flex flex-wrap gap-2 border-b border-slate-800 pb-3 mb-6">
                    {["summary", "architecture", "database", "api", "security"].map((sec) => (
                      <button
                        key={sec}
                        onClick={() => setActiveSpecSection(sec)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize transition ${activeSpecSection === sec ? "bg-sky-500 text-slate-950 font-bold" : "bg-slate-900/50 hover:bg-slate-800 text-slate-400"}`}
                      >
                        {sec}
                      </button>
                    ))}
                  </div>

                  {/* Summary spec panel */}
                  {activeSpecSection === "summary" && (
                    <div className="space-y-6">
                      <div className="glass-panel p-6 rounded-2xl">
                        <h2 className="text-xl font-bold mb-4 text-sky-400 flex items-center gap-2">
                          <Briefcase size={20} />
                          Executive Summary
                        </h2>
                        <p className="text-slate-300 text-sm leading-relaxed">
                          {latestVersion.output_data?.business_analysis?.executive_summary}
                        </p>
                      </div>

                      <div className="glass-panel p-6 rounded-2xl grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <h3 className="font-semibold text-white mb-2">Market Fit</h3>
                          <p className="text-slate-400 text-xs leading-relaxed">
                            {latestVersion.output_data?.business_analysis?.market_fit}
                          </p>
                        </div>
                        <div>
                          <h3 className="font-semibold text-white mb-2">Revenue Model</h3>
                          <p className="text-slate-400 text-xs leading-relaxed">
                            {latestVersion.output_data?.business_analysis?.revenue_model}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* System Architecture panel */}
                  {activeSpecSection === "architecture" && (
                    <div className="space-y-6">
                      <div className="glass-panel p-6 rounded-2xl">
                        <h2 className="text-xl font-bold mb-4 text-sky-400 flex items-center gap-2">
                          <Cpu size={20} />
                          System Architecture Overview
                        </h2>
                        <p className="text-slate-300 text-sm leading-relaxed mb-6">
                          {latestVersion.output_data?.system_architecture?.overview}
                        </p>
                        
                        <h3 className="font-semibold text-white mb-3 text-sm">Mermaid Architecture Flow</h3>
                        <pre className="bg-slate-950 p-4 rounded-xl text-xs text-teal-400 overflow-x-auto border border-slate-800 font-mono">
                          {latestVersion.output_data?.system_architecture?.diagram}
                        </pre>
                      </div>
                    </div>
                  )}

                  {/* Database Design panel */}
                  {activeSpecSection === "database" && (
                    <div className="space-y-6">
                      <div className="glass-panel p-6 rounded-2xl">
                        <h2 className="text-xl font-bold mb-4 text-sky-400 flex items-center gap-2">
                          <Database size={20} />
                          Database Schema Layout
                        </h2>
                        <p className="text-slate-300 text-sm leading-relaxed mb-6">
                          {latestVersion.output_data?.database_design?.overview}
                        </p>

                        <h3 className="font-semibold text-white mb-3 text-sm">PostgreSQL DDL Statements</h3>
                        <pre className="bg-slate-950 p-4 rounded-xl text-xs text-teal-400 overflow-x-auto border border-slate-800 font-mono mb-6">
                          {latestVersion.output_data?.database_design?.schema_ddl}
                        </pre>

                        <h3 className="font-semibold text-white mb-2 text-sm">Indexing Strategy</h3>
                        <p className="text-slate-400 text-xs leading-relaxed">
                          {latestVersion.output_data?.database_design?.indexing_strategy}
                        </p>
                      </div>
                    </div>
                  )}

                  {/* API design panel */}
                  {activeSpecSection === "api" && (
                    <div className="space-y-6">
                      <div className="glass-panel p-6 rounded-2xl">
                        <h2 className="text-xl font-bold mb-4 text-sky-400 flex items-center gap-2">
                          <Code size={20} />
                          API Specifications
                        </h2>
                        <p className="text-slate-300 text-sm leading-relaxed mb-6">
                          {latestVersion.output_data?.api_design?.overview}
                        </p>

                        <h3 className="font-semibold text-white mb-4 text-sm">REST API Endpoint Contracts</h3>
                        <div className="space-y-4">
                          {latestVersion.output_data?.api_design?.endpoints?.map((ep: any, index: number) => (
                            <div key={index} className="bg-slate-950/65 border border-slate-800/80 p-4 rounded-xl">
                              <div className="flex items-center gap-3 mb-2">
                                <span className={`px-2 py-1.5 rounded-lg text-[10px] font-bold uppercase ${ep.method === "POST" ? "bg-emerald-500/20 text-emerald-400" : "bg-sky-500/20 text-sky-400"}`}>
                                  {ep.method}
                                </span>
                                <span className="font-mono text-xs text-white">{ep.path}</span>
                              </div>
                              <p className="text-slate-400 text-xs mb-3">{ep.summary}</p>
                              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-[10px] font-mono">
                                <div>
                                  <span className="text-slate-500 uppercase tracking-wider block mb-1">Request Payload</span>
                                  <pre className="bg-slate-900 p-2 rounded text-slate-300 overflow-x-auto truncate">{JSON.stringify(ep.request_body, null, 2)}</pre>
                                </div>
                                <div>
                                  <span className="text-slate-500 uppercase tracking-wider block mb-1">Success Response</span>
                                  <pre className="bg-slate-900 p-2 rounded text-slate-300 overflow-x-auto truncate">{JSON.stringify(ep.response_body, null, 2)}</pre>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Security panel */}
                  {activeSpecSection === "security" && (
                    <div className="space-y-6">
                      <div className="glass-panel p-6 rounded-2xl">
                        <h2 className="text-xl font-bold mb-4 text-sky-400 flex items-center gap-2">
                          <ShieldAlert size={20} />
                          Security Review
                        </h2>
                        
                        <div className="space-y-4">
                          <div>
                            <h3 className="font-semibold text-white mb-1.5 text-sm">Security Strategy</h3>
                            <p className="text-slate-300 text-xs leading-relaxed">{latestVersion.output_data?.security_review?.strategy}</p>
                          </div>
                          <div>
                            <h3 className="font-semibold text-white mb-1.5 text-sm">Authentication Strategy</h3>
                            <p className="text-slate-300 text-xs leading-relaxed">{latestVersion.output_data?.security_review?.auth_review}</p>
                          </div>
                          <div>
                            <h3 className="font-semibold text-white mb-1.5 text-sm">OWASP Top 10 Protections</h3>
                            <p className="text-slate-300 text-xs leading-relaxed">{latestVersion.output_data?.security_review?.owasp_mitigation}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* LOGO STUDIO TAB */}
              {activeTab === "logo" && (
                <div className="space-y-6">
                  {logoLoading ? (
                    <div className="text-center text-slate-500 py-20">Generating branding suggestions...</div>
                  ) : !logoData ? (
                    <div className="text-center py-20">
                      <p className="text-slate-400 text-xs mb-4">No branding files exist yet.</p>
                      <button
                        onClick={handleGenerateLogoPackage}
                        className="px-5 py-2.5 rounded-xl bg-sky-500 text-slate-950 font-semibold text-xs"
                      >
                        Generate Brand Guidelines
                      </button>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                      {/* Logo details */}
                      <div className="lg:col-span-2 space-y-6">
                        <div className="glass-panel p-6 rounded-2xl">
                          <h2 className="text-lg font-bold mb-4 text-sky-400">Design Concepts</h2>
                          <div className="space-y-3">
                            {logoData.concepts?.map((c: string, idx: number) => (
                              <p key={idx} className="text-slate-300 text-xs leading-relaxed">
                                - {c}
                              </p>
                            ))}
                          </div>
                        </div>

                        {/* Colors & Fonts */}
                        <div className="glass-panel p-6 rounded-2xl grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div>
                            <h3 className="font-semibold text-white mb-3 text-sm">Color Palette</h3>
                            <div className="flex gap-4">
                              {logoData.brand_colors?.map((col: any, idx: number) => (
                                <div key={idx} className="text-center flex-1">
                                  <div 
                                    className="w-full h-10 rounded-lg border border-slate-700/80 mb-1" 
                                    style={{ backgroundColor: col.hex }}
                                  />
                                  <span className="text-[10px] text-slate-400 font-semibold">{col.hex}</span>
                                  <span className="block text-[8px] text-slate-500">{col.name}</span>
                                </div>
                              ))}
                            </div>
                          </div>

                          <div>
                            <h3 className="font-semibold text-white mb-2 text-sm">Suggested Typography</h3>
                            <div className="space-y-2">
                              {logoData.typography?.map((t: any, idx: number) => (
                                <div key={idx} className="text-xs">
                                  <span className="text-slate-300 font-semibold">{t.font_family}</span>
                                  <span className="text-slate-500 text-[10px] ml-2">({t.category})</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Visual SVG display */}
                      <div className="space-y-6">
                        <div className="glass-panel p-6 rounded-2xl flex flex-col items-center">
                          <h2 className="text-sm font-bold text-slate-400 mb-4 self-start">Logo Preview</h2>
                          
                          {/* Selector */}
                          <div className="flex gap-2 mb-6 self-start">
                            {["light", "dark", "icon"].map((m) => (
                              <button
                                key={m}
                                onClick={() => setActiveLogoMode(m)}
                                className={`px-2.5 py-1 rounded text-[10px] uppercase font-semibold transition ${activeLogoMode === m ? "bg-sky-500 text-slate-950" : "bg-slate-900 text-slate-400"}`}
                              >
                                {m}
                              </button>
                            ))}
                          </div>

                          {/* Logo container */}
                          <div 
                            className={`w-full aspect-square flex items-center justify-center p-6 border border-slate-800 rounded-xl mb-4 ${activeLogoMode === "light" ? "bg-slate-50" : "bg-slate-950"}`}
                            dangerouslySetInnerHTML={{ 
                              __html: activeLogoMode === "light" 
                                ? logoData.logo_svg_light 
                                : activeLogoMode === "dark" 
                                  ? logoData.logo_svg_dark 
                                  : logoData.logo_svg_icon 
                            }}
                          />

                          {/* Hidden canvas for PNG export */}
                          <canvas ref={canvasRef} width={500} height={500} className="hidden" />

                          <div className="flex gap-2 w-full">
                            <button
                              onClick={downloadLogoSVG}
                              className="flex-1 py-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-[10px] font-semibold text-center transition"
                            >
                              Export SVG
                            </button>
                            <button
                              onClick={exportLogoPNG}
                              className="flex-1 py-2 rounded-lg bg-sky-500 hover:bg-sky-400 text-slate-950 text-[10px] font-semibold text-center transition"
                            >
                              Export PNG
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* UI BLUEPRINT TAB */}
              {activeTab === "ui" && (
                <div className="space-y-6">
                  {uiLoading ? (
                    <div className="text-center text-slate-500 py-20">Generating UI Blueprint suggestions...</div>
                  ) : !uiData ? (
                    <div className="text-center py-20">
                      <p className="text-slate-400 text-xs mb-4">No wireframe blueprints generated yet.</p>
                      <button
                        onClick={handleGenerateUIBlueprint}
                        className="px-5 py-2.5 rounded-xl bg-sky-500 text-slate-950 font-semibold text-xs"
                      >
                        Generate UI Blueprint
                      </button>
                    </div>
                  ) : (
                    <div className="space-y-6">
                      <div className="glass-panel p-6 rounded-2xl">
                        <h2 className="text-lg font-bold mb-4 text-sky-400">Core Screens Layout</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          {uiData.screens?.map((scr: any, idx: number) => (
                            <div key={idx} className="bg-slate-950/60 p-4 rounded-xl border border-slate-850">
                              <h4 className="font-semibold text-white text-sm mb-1">{scr.name}</h4>
                              <p className="text-slate-400 text-xs mb-3">{scr.purpose}</p>
                              <div className="flex flex-wrap gap-1.5">
                                {scr.key_elements?.map((el: string, elIdx: number) => (
                                  <span key={elIdx} className="px-2 py-0.5 rounded bg-slate-900 text-[10px] text-slate-400 border border-slate-800">
                                    {el}
                                  </span>
                                ))}
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="glass-panel p-6 rounded-2xl grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div>
                          <h3 className="font-semibold text-white mb-3 text-sm">Dashboard Configuration</h3>
                          <p className="text-slate-300 text-xs leading-relaxed">{uiData.dashboard_layout}</p>
                        </div>
                        <div>
                          <h3 className="font-semibold text-white mb-3 text-sm">Core Component Hierarchy</h3>
                          <div className="space-y-2">
                            {uiData.component_hierarchy?.map((comp: any, idx: number) => (
                              <div key={idx} className="text-xs">
                                <span className="font-semibold text-sky-400">{comp.component_name}</span>{" "}
                                <span className="text-slate-500">({comp.type})</span>
                                <p className="text-slate-400 text-[10px] mt-0.5">{comp.props_and_states}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* VIRTUAL CTO CHAT TAB */}
              {activeTab === "chat" && (
                <div className="glass-panel rounded-3xl overflow-hidden flex flex-col h-[550px]">
                  {/* Chat header */}
                  <div className="bg-slate-950/50 border-b border-slate-800 px-6 py-4 flex items-center justify-between">
                    <div>
                      <h2 className="font-bold text-sm text-white">Consulting CTO Agent</h2>
                      <p className="text-[10px] text-slate-400">Ask questions about this project spec (powered by RAG knowledge search)</p>
                    </div>
                  </div>

                  {/* Messages list */}
                  <div className="flex-grow p-6 overflow-y-auto space-y-4">
                    {chats.length === 0 ? (
                      <div className="h-full flex flex-col items-center justify-center text-slate-500 text-xs">
                        No messages. Ask how to build a feature or explain scaling strategies.
                      </div>
                    ) : (
                      chats.map((c) => (
                        <div 
                          key={c.id} 
                          className={`flex ${c.role === "user" ? "justify-end" : "justify-start"}`}
                        >
                          <div 
                            className={`max-w-[70%] p-3.5 rounded-2xl text-xs leading-relaxed ${c.role === "user" ? "bg-sky-500 text-slate-950 font-medium rounded-tr-none" : "bg-slate-900 border border-slate-800 text-slate-300 rounded-tl-none"}`}
                          >
                            <pre className="whitespace-pre-wrap font-sans">{c.message}</pre>
                          </div>
                        </div>
                      ))
                    )}
                    {chatLoading && (
                      <div className="flex justify-start">
                        <div className="bg-slate-900 border border-slate-800 text-slate-500 text-xs p-3 rounded-2xl rounded-tl-none flex items-center gap-2">
                          <Loader2 size={12} className="animate-spin text-sky-400" />
                          CTO is thinking...
                        </div>
                      </div>
                    )}
                    <div ref={chatEndRef} />
                  </div>

                  {/* Input form */}
                  <form onSubmit={handleSendMessage} className="p-4 bg-slate-950/40 border-t border-slate-800 flex gap-2">
                    <input
                      type="text"
                      className="flex-grow px-4 py-3 rounded-xl glass-input text-xs"
                      placeholder="Ask virtual CTO... (e.g. 'Suggest index keys for postgres')"
                      value={message}
                      onChange={(e) => setMessage(e.target.value)}
                    />
                    <button
                      type="submit"
                      disabled={chatLoading || !message.trim()}
                      className="p-3 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 disabled:opacity-40 transition"
                    >
                      <Send size={16} />
                    </button>
                  </form>
                </div>
              )}
            </>
          )}
        </div>

      </div>
    </div>
  );
}
