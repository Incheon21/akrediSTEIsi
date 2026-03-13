"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";

interface NavbarProps {
  programStudi?: string;
  userName?: string;
  userInitial?: string;
}

export default function Navbar({
  programStudi = "Teknik Informatika",
  userName = "Admin",
  userInitial = "A",
}: NavbarProps) {
  const pathname = usePathname();
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const isActive = (path: string) => pathname.startsWith(path);

  return (
    <nav className="w-full bg-blue-300 border-b border-gray-200 shadow-sm">
      <div className="flex items-stretch h-14">
        {/* Logo */}
        <div className="flex items-center px-5 min-w-[120px] border-r border-gray-200">
          <span className="text-sm font-semibold text-gray-500 tracking-wide">
            Logo
          </span>
        </div>

        {/* Nav Tabs */}
        <div className="flex items-stretch flex-1 justify-end px-0">
          <Link
            href="/page/prodi/simulasi-skor"
            className={`px-6 flex items-center text-sm font-medium transition-all duration-150 ${isActive("/page/prodi/simulasi-skor")
                ? "bg-[#177093] text-white shadow"
                : "bg-cyan-300 text-black hover:bg-cyan-400"
              }`}
          >
            Simulasi Skor
          </Link>
          <Link
            href="/page/prodi/dashboard-prodi"
            className={`px-6 flex items-center text-sm font-medium transition-all duration-150 ${isActive("/page/prodi/dashboard-prodi")
                ? "bg-[#177093] text-white shadow"
                : "bg-cyan-300 text-black hover:bg-cyan-400"
              }`}
          >
            Dashboard Prodi
          </Link>
        </div>

        {/* Right Section: Program Studi + Avatar */}
        <div className="flex items-center gap-3 px-5 border-l border-gray-200">
          {/* Program Studi */}
          <div className="text-right hidden sm:block">
            <p className="text-xs text-gray-400 leading-none mb-0.5">
              Program Studi
            </p>
            <p className="text-sm font-semibold text-gray-700 leading-none">
              {programStudi}
            </p>
          </div>

          {/* Avatar Dropdown */}
          <div className="relative">
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="w-9 h-9 rounded-full bg-cyan-500 text-white font-bold text-sm flex items-center justify-center hover:bg-cyan-600 transition-colors focus:outline-none focus:ring-2 focus:ring-cyan-400 focus:ring-offset-1"
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
                  <button className="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-red-50 transition-colors">
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