"use client";

import Image from "next/image";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/app/services/api";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const res = await fetch(`${API_URL}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setError(
          data.detail ?? "Login gagal. Periksa email dan password Anda.",
        );
        return;
      }

      const data = await res.json();
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);

      const profileRes = await apiFetch("/api/v1/auth/me");
      if (!profileRes.ok) {
        throw new Error("Gagal mendapatkan profil setelah login");
      }

      const profile = await profileRes.json();
      const role = profile.role?.name ?? "tim_prodi";

      if (role === "admin" || role === "pimpinan" || role === "koordinator") {
        router.push("/dashboard-multiprodi");
      } else {
        const prodiId = profile.program_studi_id;
        if (prodiId) {
          router.push(`/prodi/dashboard-prodi?id=${prodiId}`);
        } else {
          router.push("/prodi/dashboard-prodi");
        }
      }
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Tidak dapat terhubung ke server. Coba lagi nanti.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-100">
      <div className="grid min-h-screen md:grid-cols-2">
        <section className="relative overflow-hidden bg-[#00509d] px-8 py-12 text-white md:px-12 lg:px-16">
          <div className="absolute inset-0">
            <div className="absolute -left-20 -top-16 h-56 w-56 rounded-full bg-[#f3e412]/20 blur-3xl" />
            <div className="absolute -bottom-20 right-0 h-64 w-64 rounded-full bg-cyan-400/25 blur-3xl" />
            <div className="absolute inset-0 bg-linear-to-br from-[#00509d] via-[#005cae] to-[#0073c7]" />
          </div>

          <div className="relative z-10 flex h-full flex-col justify-between">
            <div>
              <Image
                src="/itb-stei-white.svg"
                alt="STEI ITB"
                width={220}
                height={44}
                className="h-10 w-auto"
                priority
              />
              <p className="mt-8 max-w-md text-3xl font-semibold leading-tight md:text-4xl">
                Dashboard Akreditasi Program Studi
              </p>
              <p className="mt-4 max-w-md text-sm text-blue-100 md:text-base">
                Mengelola data LKPS dan LED secara terintegrasi untuk mendukung
                evaluasi dan pengambilan keputusan.
              </p>
            </div>
          </div>
        </section>

        <section className="flex items-center justify-center px-6 py-12 md:px-10 lg:px-14">
          <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 shadow-lg shadow-slate-200/70 md:p-9">
            <h1 className="text-3xl font-bold text-slate-800">Masuk</h1>
            <p className="mt-2 text-sm text-slate-500">
              Gunakan akun terdaftar untuk melanjutkan.
            </p>

            <form onSubmit={handleSubmit} className="mt-7 space-y-4">
              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">
                  Email
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  placeholder="nama@example.com"
                  className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-[#00509d] focus:ring-2 focus:ring-[#00509d]/20"
                />
              </div>

              <div>
                <label className="mb-1 block text-sm font-medium text-slate-700">
                  Password
                </label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  placeholder="••••••••"
                  className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder-slate-400 outline-none transition focus:border-[#00509d] focus:ring-2 focus:ring-[#00509d]/20"
                />
              </div>

              {error && <p className="text-sm text-red-600">{error}</p>}

              <button
                type="submit"
                disabled={loading}
                className="w-full rounded-lg bg-[#00509d] px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-[#003f7c] disabled:cursor-not-allowed disabled:opacity-60"
              >
                {loading ? "Memuat..." : "Masuk"}
              </button>
            </form>
          </div>
        </section>
      </div>
    </div>
  );
}
