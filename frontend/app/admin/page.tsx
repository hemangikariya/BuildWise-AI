"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { 
  Users, Cpu, FileText, Database, ShieldAlert, Ban, Trash2, ArrowLeft, RefreshCw 
} from "lucide-react";

export default function AdminPage() {
  const router = useRouter();
  
  // Tab states
  const [activeTab, setActiveTab] = useState("users"); // users, agent_runs, logs, rag
  
  // Data lists
  const [users, setUsers] = useState<any[]>([]);
  const [agentRuns, setAgentRuns] = useState<any[]>([]);
  const [systemLogs, setSystemLogs] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [kbItems, setKbItems] = useState<any[]>([]);
  
  // Loading & Ingestion states
  const [loading, setLoading] = useState(true);
  const [ingestPath, setIngestPath] = useState("");
  const [ingesting, setIngesting] = useState(false);
  const [ingestStatus, setIngestStatus] = useState("");

  const verifyAdmin = () => {
    const isAdmin = localStorage.getItem("is_admin");
    if (isAdmin !== "true") {
      router.push("/dashboard");
    }
  };

  const fetchAdminData = async () => {
    setLoading(true);
    try {
      if (activeTab === "users") {
        const res = await api.get("/admin/users");
        setUsers(res.data);
      } else if (activeTab === "agent_runs") {
        const res = await api.get("/admin/agent-runs");
        setAgentRuns(res.data);
      } else if (activeTab === "logs") {
        const sysRes = await api.get("/admin/system-logs");
        const auditRes = await api.get("/admin/audit-logs");
        setSystemLogs(sysRes.data);
        setAuditLogs(auditRes.data);
      } else if (activeTab === "rag") {
        const res = await api.get("/admin/knowledge-base");
        setKbItems(res.data);
      }
    } catch (err) {
      console.error("Failed to load admin data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    verifyAdmin();
    fetchAdminData();
  }, [activeTab]);

  // User Actions
  const handleToggleUserStatus = async (userId: string, currentStatus: boolean) => {
    try {
      const res = await api.put(`/admin/users/${userId}/status`, { is_active: !currentStatus });
      setUsers(users.map(u => u.id === userId ? res.data : u));
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to update user status");
    }
  };

  const handleDeleteUser = async (userId: string) => {
    if (!confirm("Are you sure you want to permanently delete this user account?")) return;
    try {
      await api.delete(`/admin/users/${userId}`);
      setUsers(users.filter(u => u.id !== userId));
    } catch (err: any) {
      alert(err.response?.data?.detail || "Failed to delete user");
    }
  };

  // RAG Ingestion Actions
  const handleIngest = async (e: React.FormEvent) => {
    e.preventDefault();
    setIngesting(true);
    setIngestStatus("");
    
    try {
      const res = await api.post("/admin/knowledge-base/ingest", {
        directory_path: ingestPath.trim() || null
      });
      setIngestStatus(res.data.message);
      // Refresh list
      const kbRes = await api.get("/admin/knowledge-base");
      setKbItems(kbRes.data);
    } catch (err: any) {
      setIngestStatus(err.response?.data?.detail || "Ingestion process encountered an error.");
    } finally {
      setIngesting(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-[#020617] text-white flex flex-col overflow-hidden">
      {/* Header */}
      <header className="relative z-10 border-b border-slate-800 bg-slate-950/45 backdrop-blur-md px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push("/dashboard")}
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-white transition"
          >
            <ArrowLeft size={16} />
          </button>
          <div>
            <h1 className="text-lg font-bold text-white leading-none mb-1">Admin Operations Center</h1>
            <p className="text-slate-400 text-xs">Monitor agent pipelines, users, and audit logs.</p>
          </div>
        </div>

        <button
          onClick={fetchAdminData}
          className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-white transition flex items-center gap-1.5 text-xs font-semibold"
        >
          <RefreshCw size={14} />
          Refresh
        </button>
      </header>

      {/* Main admin panels */}
      <div className="flex-grow max-w-6xl w-full mx-auto px-6 py-10 flex flex-col md:flex-row gap-8 relative z-10">
        
        {/* Navigation Tabs bar */}
        <div className="w-full md:w-[220px] flex flex-col gap-2">
          <button
            onClick={() => setActiveTab("users")}
            className={`px-4 py-3 rounded-xl text-left text-xs font-semibold flex items-center gap-2.5 transition ${activeTab === "users" ? "bg-sky-500/10 text-sky-400 border border-sky-500/20" : "hover:bg-slate-900 text-slate-400 hover:text-white"}`}
          >
            <Users size={16} />
            User Manager
          </button>
          <button
            onClick={() => setActiveTab("agent_runs")}
            className={`px-4 py-3 rounded-xl text-left text-xs font-semibold flex items-center gap-2.5 transition ${activeTab === "agent_runs" ? "bg-sky-500/10 text-sky-400 border border-sky-500/20" : "hover:bg-slate-900 text-slate-400 hover:text-white"}`}
          >
            <Cpu size={16} />
            Agent Pipeline Logs
          </button>
          <button
            onClick={() => setActiveTab("logs")}
            className={`px-4 py-3 rounded-xl text-left text-xs font-semibold flex items-center gap-2.5 transition ${activeTab === "logs" ? "bg-sky-500/10 text-sky-400 border border-sky-500/20" : "hover:bg-slate-900 text-slate-400 hover:text-white"}`}
          >
            <ShieldAlert size={16} />
            System & Audit Logs
          </button>
          <button
            onClick={() => setActiveTab("rag")}
            className={`px-4 py-3 rounded-xl text-left text-xs font-semibold flex items-center gap-2.5 transition ${activeTab === "rag" ? "bg-sky-500/10 text-sky-400 border border-sky-500/20" : "hover:bg-slate-900 text-slate-400 hover:text-white"}`}
          >
            <Database size={16} />
            Knowledge Base RAG
          </button>
        </div>

        {/* Dynamic content view panels */}
        <div className="flex-grow bg-[#090d1f] border border-slate-800/80 rounded-3xl p-6 overflow-y-auto max-h-[calc(100vh-180px)]">
          {loading ? (
            <div className="text-center text-slate-500 py-20 text-sm">Loading admin dashboard records...</div>
          ) : (
            <>
              {/* USER MANAGER PANELS */}
              {activeTab === "users" && (
                <div className="space-y-6">
                  <h2 className="text-lg font-bold mb-4 flex items-center gap-2 text-sky-400">
                    <Users size={18} />
                    Registered Users
                  </h2>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider">
                          <th className="py-3 px-4">Full Name</th>
                          <th className="py-3 px-4">Email</th>
                          <th className="py-3 px-4">Role</th>
                          <th className="py-3 px-4">Status</th>
                          <th className="py-3 px-4 text-right">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {users.map((u) => (
                          <tr key={u.id} className="border-b border-slate-850 hover:bg-slate-900/35 transition">
                            <td className="py-3 px-4 font-semibold text-white">{u.full_name}</td>
                            <td className="py-3 px-4 text-slate-300">{u.email}</td>
                            <td className="py-3 px-4">
                              <span className="px-2 py-0.5 rounded bg-slate-800 text-[10px] text-sky-400 font-bold">
                                {u.role?.name}
                              </span>
                            </td>
                            <td className="py-3 px-4">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${u.is_active ? "bg-emerald-500/10 text-emerald-400" : "bg-rose-500/10 text-rose-400"}`}>
                                {u.is_active ? "Active" : "Blocked"}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-right flex justify-end gap-2">
                              <button
                                onClick={() => handleToggleUserStatus(u.id, u.is_active)}
                                className={`p-1.5 rounded transition ${u.is_active ? "text-slate-400 hover:text-amber-400 hover:bg-amber-500/10" : "text-amber-400 hover:bg-amber-500/20"}`}
                                title={u.is_active ? "Block User" : "Unblock User"}
                              >
                                <Ban size={14} />
                              </button>
                              <button
                                onClick={() => handleDeleteUser(u.id)}
                                className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-500/10 rounded transition"
                                title="Delete User"
                              >
                                <Trash2 size={14} />
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* AGENT RUNS MONITOR PANELS */}
              {activeTab === "agent_runs" && (
                <div className="space-y-6">
                  <h2 className="text-lg font-bold mb-4 flex items-center gap-2 text-sky-400">
                    <Cpu size={18} />
                    Agent Orchestrator Pipeline Runs
                  </h2>
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="border-b border-slate-800 text-slate-400 uppercase tracking-wider">
                          <th className="py-3 px-4">Agent Name</th>
                          <th className="py-3 px-4">Version reference</th>
                          <th className="py-3 px-4">Status</th>
                          <th className="py-3 px-4">Execution Time</th>
                        </tr>
                      </thead>
                      <tbody>
                        {agentRuns.map((r) => (
                          <tr key={r.id} className="border-b border-slate-850 hover:bg-slate-900/35">
                            <td className="py-3 px-4 font-semibold text-white">{r.agent_name}</td>
                            <td className="py-3 px-4 text-slate-400 font-mono">{r.project_version_id}</td>
                            <td className="py-3 px-4">
                              <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${r.status === "COMPLETED" ? "bg-emerald-500/10 text-emerald-400" : r.status === "RUNNING" ? "bg-sky-500/10 text-sky-400" : "bg-rose-500/10 text-rose-400"}`}>
                                {r.status}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-slate-500">{new Date(r.created_at).toLocaleString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* SYSTEM & AUDIT LOG VIEWER PANELS */}
              {activeTab === "logs" && (
                <div className="space-y-8">
                  {/* System Logs */}
                  <div>
                    <h2 className="text-lg font-bold mb-4 flex items-center gap-2 text-rose-400">
                      <ShieldAlert size={18} />
                      System Diagnostic Logs
                    </h2>
                    <div className="max-h-[250px] overflow-y-auto border border-slate-800 rounded-xl">
                      <table className="w-full text-left text-xs border-collapse">
                        <thead>
                          <tr className="border-b border-slate-800 text-slate-400 uppercase bg-slate-950/40 sticky top-0">
                            <th className="py-2.5 px-4">Level</th>
                            <th className="py-2.5 px-4">Module</th>
                            <th className="py-2.5 px-4">Message</th>
                            <th className="py-2.5 px-4">Timestamp</th>
                          </tr>
                        </thead>
                        <tbody>
                          {systemLogs.map((log) => (
                            <tr key={log.id} className="border-b border-slate-850 hover:bg-slate-900/10">
                              <td className="py-2 px-4 font-mono font-bold">
                                <span className={log.level === "ERROR" || log.level === "CRITICAL" ? "text-rose-400" : log.level === "WARNING" ? "text-amber-400" : "text-sky-400"}>
                                  {log.level}
                                </span>
                              </td>
                              <td className="py-2 px-4 text-slate-300">{log.module}</td>
                              <td className="py-2 px-4 text-slate-400 max-w-[250px] truncate" title={log.message}>{log.message}</td>
                              <td className="py-2 px-4 text-slate-500">{new Date(log.created_at).toLocaleString()}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>

                  {/* Audit Logs */}
                  <div>
                    <h2 className="text-lg font-bold mb-4 flex items-center gap-2 text-teal-400">
                      <FileText size={18} />
                      Security Audit Logs
                    </h2>
                    <div className="max-h-[250px] overflow-y-auto border border-slate-800 rounded-xl">
                      <table className="w-full text-left text-xs border-collapse">
                        <thead>
                          <tr className="border-b border-slate-800 text-slate-400 uppercase bg-slate-950/40 sticky top-0">
                            <th className="py-2.5 px-4">Action</th>
                            <th className="py-2.5 px-4">IP Address</th>
                            <th className="py-2.5 px-4">User ID</th>
                            <th className="py-2.5 px-4">Timestamp</th>
                          </tr>
                        </thead>
                        <tbody>
                          {auditLogs.map((a) => (
                            <tr key={a.id} className="border-b border-slate-850 hover:bg-slate-900/10">
                              <td className="py-2 px-4 font-semibold text-teal-400">{a.action}</td>
                              <td className="py-2 px-4 text-slate-300">{a.ip_address || "N/A"}</td>
                              <td className="py-2 px-4 font-mono text-slate-500">{a.user_id || "Unauthenticated"}</td>
                              <td className="py-2 px-4 text-slate-500">{new Date(a.created_at).toLocaleString()}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>
              )}

              {/* KNOWLEDGE BASE RAG PANEL */}
              {activeTab === "rag" && (
                <div className="space-y-6">
                  <h2 className="text-lg font-bold mb-4 flex items-center gap-2 text-sky-400">
                    <Database size={18} />
                    RAG Knowledge Base Sources
                  </h2>
                  
                  {/* Load/Ingest Trigger Form */}
                  <form onSubmit={handleIngest} className="glass-panel p-5 rounded-2xl space-y-4 mb-6">
                    <h3 className="font-semibold text-xs uppercase tracking-wider text-slate-400">Bootstrap / Index Documentation Directories</h3>
                    <div className="flex gap-2">
                      <input
                        type="text"
                        className="flex-grow px-4 py-2 rounded-xl glass-input text-xs"
                        placeholder="Path to docs directory (Default: backend-hosted docs folder)"
                        value={ingestPath}
                        onChange={(e) => setIngestPath(e.target.value)}
                      />
                      <button
                        type="submit"
                        disabled={ingesting}
                        className="px-5 py-2 rounded-xl bg-sky-500 hover:bg-sky-400 text-slate-950 text-xs font-semibold transition disabled:opacity-50"
                      >
                        {ingesting ? "Ingesting..." : "Ingest Directory"}
                      </button>
                    </div>
                    {ingestStatus && (
                      <p className="text-[10px] font-mono text-teal-400">{ingestStatus}</p>
                    )}
                  </form>

                  {/* List items */}
                  <div className="border border-slate-800 rounded-xl overflow-hidden">
                    <table className="w-full text-left text-xs border-collapse">
                      <thead>
                        <tr className="border-b border-slate-800 text-slate-400 uppercase bg-slate-950/40">
                          <th className="py-3 px-4">Title</th>
                          <th className="py-3 px-4">File Path</th>
                          <th className="py-3 px-4">Imported At</th>
                        </tr>
                      </thead>
                      <tbody>
                        {kbItems.map((item) => (
                          <tr key={item.id} className="border-b border-slate-850 hover:bg-slate-900/10">
                            <td className="py-3 px-4 font-semibold text-white">{item.title}</td>
                            <td className="py-3 px-4 text-slate-400 font-mono truncate max-w-[200px]" title={item.file_path}>
                              {item.file_path}
                            </td>
                            <td className="py-3 px-4 text-slate-500">{new Date(item.created_at).toLocaleString()}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </>
          )}
        </div>

      </div>
    </div>
  );
}
