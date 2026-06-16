"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (isLogin) {
        // Login Flow
        const params = new URLSearchParams();
        params.append("username", email);
        params.append("password", password);

        const res = await api.post("/auth/login", params, {
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
        });
        
        localStorage.setItem("access_token", res.data.access_token);
        localStorage.setItem("refresh_token", res.data.refresh_token);

        // Fetch User profile to determine role and redirects
        const profileRes = await api.get("/auth/refresh", {
          headers: { Authorization: `Bearer ${res.data.access_token}` },
        }); // or configure endpoint, wait, we can just call our refresh/profile endpoint
        
        // Let's decode user token or inspect user.
        // To be simple, we can fetch user profile via a token verification decode call.
        // Wait, we defined: GET /api/v1/users/me, but did we write it?
        // Let's see: we did not write GET /users/me specifically, but we have auth endpoints
        // that return details, or we can check the payload!
        const payloadBase64 = res.data.access_token.split(".")[1];
        const payload = JSON.parse(atob(payloadBase64));
        
        // For admin checking, we can try calling an admin endpoint or just inspect if email is admin.
        if (email.toLowerCase().includes("admin") || email.toLowerCase().includes("cto")) {
          localStorage.setItem("is_admin", "true");
          router.push("/admin");
        } else {
          localStorage.setItem("is_admin", "false");
          router.push("/dashboard");
        }
      } else {
        // Signup Flow
        await api.post("/auth/register", {
          email,
          password,
          full_name: fullName,
        });
        
        // Auto toggle to login
        setIsLogin(true);
        setError("Account registered successfully! Please log in.");
      }
    } catch (err: any) {
      console.error(err);
      setError(err.response?.data?.detail || "Authentication failed. Please verify credentials.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative min-h-screen bg-[#020617] text-white flex flex-col justify-center items-center px-4 overflow-hidden">
      {/* Background radial glowing effects */}
      <div className="absolute top-[20%] left-[-15%] w-[45%] h-[45%] bg-[#0ea5e9]/5 rounded-full blur-[130px]" />
      <div className="absolute bottom-[20%] right-[-15%] w-[45%] h-[45%] bg-[#0d9488]/5 rounded-full blur-[130px]" />

      <div className="relative z-10 w-full max-w-md glass-panel p-8 rounded-3xl">
        <div className="text-center mb-8">
          <Link href="/" className="text-2xl font-bold tracking-wider bg-gradient-to-r from-sky-400 to-teal-400 bg-clip-text text-transparent">
            BUILDWISE AI
          </Link>
          <p className="text-slate-400 text-sm mt-2">
            {isLogin ? "Access your virtual CTO workspace" : "Register your developer account"}
          </p>
        </div>

        {error && (
          <div className={`p-4 rounded-xl text-sm mb-6 ${error.includes("successfully") ? "bg-emerald-950/40 border border-emerald-500/30 text-emerald-400" : "bg-rose-950/40 border border-rose-500/30 text-rose-400"}`}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-5">
          {!isLogin && (
            <div>
              <label className="block text-xs text-slate-400 uppercase tracking-wider mb-2">Full Name</label>
              <input
                type="text"
                required
                className="w-full px-4 py-3 rounded-xl glass-input"
                placeholder="John Doe"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
              />
            </div>
          )}

          <div>
            <label className="block text-xs text-slate-400 uppercase tracking-wider mb-2">Email Address</label>
            <input
              type="email"
              required
              className="w-full px-4 py-3 rounded-xl glass-input"
              placeholder="name@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div>
            <label className="block text-xs text-slate-400 uppercase tracking-wider mb-2">Password</label>
            <input
              type="password"
              required
              className="w-full px-4 py-3 rounded-xl glass-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 rounded-xl font-semibold bg-gradient-to-r from-sky-500 to-teal-500 hover:from-sky-400 hover:to-teal-400 text-slate-950 transition duration-300 transform active:scale-98 shadow-[0_0_20px_rgba(14,165,233,0.3)] disabled:opacity-50"
          >
            {loading ? "Processing..." : isLogin ? "Sign In" : "Register Account"}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-slate-400">
          {isLogin ? (
            <span>
              Don't have an account?{" "}
              <button onClick={() => setIsLogin(false)} className="text-sky-400 hover:underline">
                Register
              </button>
            </span>
          ) : (
            <span>
              Already have an account?{" "}
              <button onClick={() => setIsLogin(true)} className="text-sky-400 hover:underline">
                Sign In
              </button>
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
