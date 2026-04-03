"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { apiFetch } from "../../services/api";

interface NavbarProps {
  programStudi?: string;
  userName?: string;
  userInitial?: string;
  role?: string;
}

export default function Navbar({
  programStudi = "",
  userName = "",
  userInitial = "",
  role = "",
}: NavbarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [prodiDropdownOpen, setProdiDropdownOpen] = useState(false);
  const [prodiList, setProdiList] = useState<{ id: string; name: string }[]>([]);

  useEffect(() => {
    if (role === "admin") {
      // Fetch list prodi for admin
      const fetchProdiList = async () => {
        try {
          const res = await apiFetch("/api/v1/multiprodi/dashboard");
          if (res.ok) {
            const data = await res.json();
            setProdiList(data.prodi_list.map((p: any) => ({ id: p.id, name: p.name })));
          }
        } catch (err) {
          console.error("Failed to fetch prodi list:", err);
        }
      };
      fetchProdiList();
    }
  }, [role]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    router.push("/login");
  };

  const isActive = (path: string) => pathname.startsWith(path);

  return (
    <nav className="w-full bg-[#00509d] shadow-md py-2">
      <div className="flex items-stretch h-14">
        <div className="flex items-center px-5 min-w-[140px] border-r border-[#0060b8]">
          <img
            src="/itb-stei-white.svg"
            alt="STEI ITB"
            className="h-8 w-auto"
          />
        </div>

        <div className="flex items-stretch flex-1 justify-end px-0">
          {role !== "admin" && (
            <>
              <Link
                href="/prodi/simulasi-skor"
                className={`px-6 flex items-center text-sm font-semibold transition-all duration-150 ${isActive("/prodi/simulasi-skor")
                  ? "text-[#f3e412]"
                  : "text-white hover:text-[#f3e412]"
                  }`}
              >
                Simulasi Skor
              </Link>
              <Link
                href="/prodi/dashboard-prodi"
                className={`px-6 flex items-center text-sm font-semibold transition-all duration-150 ${isActive("/prodi/dashboard-prodi")
                  ? "text-[#f3e412]"
                  : "text-white hover:text-[#f3e412]"
                  }`}
              >
                Dashboard Prodi
              </Link>
            </>
          )}
        </div>

        <div className="flex items-center gap-3 px-5 border-l border-[#0060b8]">
          {/* Program Studi or Prodi Selector for Admin */}
          {role === "admin" ? (
            <div className="relative hidden sm:block">
              <button
                onClick={() => setProdiDropdownOpen(!prodiDropdownOpen)}
                className="flex items-center gap-2 text-right text-sm font-semibold text-white hover:text-[#f3e412] transition-colors"
              >
                <span>Pilih Prodi</span>
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              {prodiDropdownOpen && (
                <div className="absolute right-0 mt-2 w-64 bg-white rounded-lg shadow-lg border border-gray-100 z-50 max-h-60 overflow-y-auto">
                  {prodiList.map((prodi) => (
                    <div key={prodi.id} className="border-b border-gray-100 last:border-b-0">
                      <div className="px-4 py-2 text-xs text-gray-400">{prodi.name}</div>
                      <Link
                        href={`/prodi/dashboard-prodi?id=${prodi.id}`}
                        className="block px-6 py-2 text-sm text-gray-600 hover:bg-gray-50 transition-colors"
                        onClick={() => setProdiDropdownOpen(false)}
                      >
                        📊 Dashboard Prodi
                      </Link>
                      <Link
                        href={`/prodi/simulasi-skor?id=${prodi.id}`}
                        className="block px-6 py-2 text-sm text-gray-600 hover:bg-gray-50 transition-colors"
                        onClick={() => setProdiDropdownOpen(false)}
                      >
                        🎯 Simulasi Skor
                      </Link>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="text-right hidden sm:block">
              <p className="text-xs text-blue-200 leading-none mb-0.5">
                Program Studi
              </p>
              <p className="text-sm font-semibold text-white leading-none">
                {programStudi}
              </p>
            </div>
          )}

          {/* Avatar Dropdown */}
          <div className="relative">
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="w-9 h-9 rounded-full bg-[#f39c12] text-white font-bold text-sm flex items-center justify-center hover:bg-[#e08e0b] transition-colors focus:outline-none focus:ring-2 focus:ring-yellow-400 focus:ring-offset-1 focus:ring-offset-[#00509d]"
              aria-label="User menu"
            >
              {userInitial}
            </button>

            {dropdownOpen && (
              <div className="absolute right-0 mt-2 w-44 bg-white rounded-lg shadow-lg border border-gray-100 z-50 py-1">
                <div className="px-4 py-2 border-b border-gray-100">
                  <p className="text-xs text-gray-400">Masuk sebagai</p>
                  <p className="text-sm font-semibold text-gray-700">
                    {userName}
                  </p>
                </div>
                <button className="w-full text-left px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 transition-colors">
                  Profil
                </button>
                <button className="w-full text-left px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 transition-colors">
                  Pengaturan
                </button>
                <div className="border-t border-gray-100 mt-1">
                  <button
                    onClick={handleLogout}
                    className="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-red-50 transition-colors"
                  >
                    Keluar
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
