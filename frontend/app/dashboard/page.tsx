"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { LogOut, Plus, Folder, Calendar, ArrowRight, Trash2 } from "lucide-react";

interface Project {
  id: string;
  title: string;
  description: string;
  created_at: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [listLoading, setListLoading] = useState(true);

  // Fetch projects
  const fetchProjects = async () => {
    try {
      const res = await api.get("/projects");
      setProjects(res.data);
    } catch (err) {
      console.error("Failed to load projects", err);
      // Redirect to login on token failures
      router.push("/login");
    } finally {
      setListLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, []);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setLoading(true);
    try {
      const res = await api.post("/projects", {
        title,
        description,
      });
      // Close modal and redirect to project workspace
      setShowCreateModal(false);
      router.push(`/project/${res.data.id}`);
    } catch (err) {
      console.error("Failed to create project", err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation(); // prevent card click
    if (!confirm("Are you sure you want to delete this project?")) return;

    try {
      await api.delete(`/projects/${id}`);
      setProjects(projects.filter((p) => p.id !== id));
    } catch (err) {
      console.error("Failed to delete project", err);
    }
  };

  const handleSignOut = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("is_admin");
    router.push("/login");
  };

  return (
    <div className="relative min-h-screen bg-[#020617] text-white flex flex-col overflow-hidden">
      {/* Background glowing gradients */}
      <div className="absolute top-[-10%] right-[-10%] w-[40%] h-[40%] bg-[#0ea5e9]/5 rounded-full blur-[120px]" />
      
      {/* Header bar */}
      <header className="relative z-10 border-b border-slate-800/80 bg-slate-950/45 backdrop-blur-md px-6 py-4 flex justify-between items-center">
        <div className="flex items-center gap-3">
          <span className="text-xl font-bold tracking-wider bg-gradient-to-r from-sky-400 to-teal-400 bg-clip-text text-transparent">
            BUILDWISE AI
          </span>
          <span className="px-2.5 py-0.5 rounded-full bg-slate-800 text-[10px] uppercase font-bold text-sky-400 tracking-wider">
            Workspace
          </span>
        </div>
        
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push("/admin")}
            className="text-xs text-slate-400 hover:text-white transition"
          >
            Admin Panel
          </button>
          <button
            onClick={handleSignOut}
            className="p-2 rounded-lg bg-slate-900 border border-slate-800 hover:bg-slate-800 text-slate-400 hover:text-white transition flex items-center gap-2 text-xs"
          >
            <LogOut size={14} />
            Sign Out
          </button>
        </div>
      </header>

      {/* Main dashboard content */}
      <div className="relative z-10 flex-grow max-w-6xl w-full mx-auto px-6 py-10">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-10">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white mb-2">Projects Dashboard</h1>
            <p className="text-slate-400 text-sm">Create workspaces and consult your virtual AI CTO on architecture blueprints.</p>
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-5 py-3 rounded-xl font-semibold bg-gradient-to-r from-sky-500 to-teal-500 hover:from-sky-400 hover:to-teal-400 text-slate-950 flex items-center gap-2 transition duration-300 transform active:scale-95 shadow-[0_0_15px_rgba(14,165,233,0.3)]"
          >
            <Plus size={18} />
            New Project
          </button>
        </div>

        {/* Projects List Grid */}
        {listLoading ? (
          <div className="text-center text-slate-500 py-20 text-sm">Loading projects...</div>
        ) : projects.length === 0 ? (
          <div className="glass-panel text-center py-20 px-6 rounded-3xl max-w-xl mx-auto">
            <Folder size={48} className="mx-auto text-slate-600 mb-4" />
            <h2 className="text-lg font-semibold mb-2">No Projects Found</h2>
            <p className="text-slate-400 text-sm mb-6 max-w-sm mx-auto">Create a workspace to begin mapping out system structures and generating professional reports.</p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-5 py-2.5 rounded-xl text-xs font-semibold bg-sky-500 hover:bg-sky-400 text-slate-950 transition"
            >
              Get Started
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((p) => (
              <div
                key={p.id}
                onClick={() => router.push(`/project/${p.id}`)}
                className="glass-panel p-6 rounded-2xl cursor-pointer flex flex-col justify-between h-[180px] relative group"
              >
                <div>
                  <div className="flex justify-between items-start gap-4">
                    <h3 className="font-semibold text-lg text-white group-hover:text-sky-400 transition truncate max-w-[80%]">
                      {p.title}
                    </h3>
                    <button
                      onClick={(e) => handleDelete(p.id, e)}
                      className="p-1 text-slate-600 hover:text-rose-400 hover:bg-rose-500/10 rounded transition"
                      title="Delete Project"
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                  <p className="text-slate-400 text-xs line-clamp-2 mt-2 leading-relaxed">
                    {p.description || "No description provided."}
                  </p>
                </div>
                
                <div className="flex items-center justify-between border-t border-slate-800/80 pt-4 mt-4">
                  <div className="flex items-center gap-1.5 text-[10px] text-slate-500">
                    <Calendar size={11} />
                    {new Date(p.created_at).toLocaleDateString()}
                  </div>
                  <span className="text-xs text-sky-400 font-semibold inline-flex items-center gap-1 group-hover:translate-x-1 transition-transform">
                    Consult <ArrowRight size={12} />
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Project Modal Dialog */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm px-4">
          <div className="glass-panel w-full max-w-lg p-8 rounded-3xl relative">
            <h2 className="text-xl font-bold mb-4">Create New Project</h2>
            <form onSubmit={handleCreate} className="space-y-5">
              <div>
                <label className="block text-xs text-slate-400 uppercase tracking-wider mb-2">Project Title</label>
                <input
                  type="text"
                  required
                  className="w-full px-4 py-3 rounded-xl glass-input"
                  placeholder="E.g. AI Fitness Application"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
              </div>

              <div>
                <label className="block text-xs text-slate-400 uppercase tracking-wider mb-2">Project Description</label>
                <textarea
                  rows={4}
                  required
                  className="w-full px-4 py-3 rounded-xl glass-input resize-none"
                  placeholder="Explain the idea. E.g. A mobile application that tracks user runs, leverages AI to create custom fitness plans, and logs progress in a database."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-5 py-2.5 rounded-xl border border-slate-700 bg-slate-900/50 hover:bg-slate-800 transition text-xs font-semibold"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-sky-500 to-teal-500 hover:from-sky-400 hover:to-teal-400 text-slate-950 font-semibold text-xs transition disabled:opacity-50"
                >
                  {loading ? "Creating..." : "Create Project"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
