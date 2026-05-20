"use client";

import { useEffect, useState, useRef } from "react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

import { apiFetch } from "@/app/services/api";

interface NavbarProps {
  programStudi?: string;
  programStudiId?: string;
  userName?: string;
  userInitial?: string;
  role?: string;
}

interface NotificationItem {
  id: string;
  kategori: string;
  severity: "info" | "warning" | "critical" | string;
  judul: string;
  pesan: string;
  href?: string | null;
  is_read: boolean;
}

export default function Navbar({
  programStudi = "",
  programStudiId = "",
  userName = "",
  userInitial = "",
  role = "",
}: NavbarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [notificationOpen, setNotificationOpen] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const searchParams = useSearchParams();
  const dropdownRef = useRef<HTMLDivElement>(null);
  const notificationRef = useRef<HTMLDivElement>(null);
  const prodiId = searchParams.get("id") || programStudiId;
  const prodiQuery = prodiId ? `?id=${prodiId}` : "";
  const notificationQuery = prodiId ? `&program_studi_id=${prodiId}` : "";

  async function fetchNotifications() {
    if (!role) return;

    const response = await apiFetch(`/api/v1/notifikasi?limit=10${notificationQuery}`);
    if (!response.ok) return;

    const data = await response.json();
    setNotifications(data.items ?? []);
    setUnreadCount(data.unread_count ?? 0);
  }

  useEffect(() => {
    const timeoutId = window.setTimeout(fetchNotifications, 0);
    const intervalId = window.setInterval(fetchNotifications, 60000);
    return () => {
      window.clearTimeout(timeoutId);
      window.clearInterval(intervalId);
    };
    // fetchNotifications reads the latest auth token from localStorage through apiFetch.
    // Re-subscribing on role changes is enough for this navbar-level polling.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [role, notificationQuery]);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    router.push("/login");
  };

  const isActive = (path: string) => pathname.startsWith(path);

  // Admin sedang di dalam dashboard prodi tertentu
  const isAdminInProdiPage =
    (role === "admin" || role === "pimpinan") &&
    (pathname.includes("/prodi/") || pathname.includes("/akreditasi/"));

  const markNotificationRead = async (item: NotificationItem) => {
    if (item.is_read) return;

    setNotifications((current) =>
      current.map((notification) =>
        notification.id === item.id
          ? { ...notification, is_read: true }
          : notification,
      ),
    );
    setUnreadCount((current) => Math.max(0, current - 1));

    await apiFetch(`/api/v1/notifikasi/${item.id}/read`, { method: "POST" });
  };

  const markAllNotificationsRead = async () => {
    setNotifications((current) =>
      current.map((notification) => ({ ...notification, is_read: true })),
    );
    setUnreadCount(0);
    const readAllQuery = prodiId ? `?program_studi_id=${prodiId}` : "";
    await apiFetch(`/api/v1/notifikasi/read-all${readAllQuery}`, { method: "POST" });
  };

  const severityClass = (severity: NotificationItem["severity"]) => {
    if (severity === "critical") return "bg-red-500";
    if (severity === "warning") return "bg-amber-400";
    return "bg-blue-500";
  };

  return (
    <nav className="w-full bg-[#00509d] shadow-md py-2">
      <div className="flex items-stretch h-14">
        {/* Logo */}
        <div className="flex items-center px-5 min-w-[140px] border-r border-[#0060b8]">
          <img
            src="/itb-stei-white.svg"
            alt="STEI ITB"
            className="h-8 w-auto"
          />
        </div>

        {/* Nav links */}
        <div className="flex items-stretch flex-1 px-2">
          {role === "admin" || role === "pimpinan" ? (
            <>
              <Link
                href="/dashboard-multiprodi"
                className={`px-6 flex items-center text-sm font-semibold transition-all duration-150 ${
                  isActive("/dashboard-multiprodi")
                    ? "text-[#f3e412]"
                    : "text-white hover:text-[#f3e412]"
                }`}
              >
                Dashboard Multiprodi
              </Link>

              {/* Link halaman prodi — hanya muncul saat sedang di konteks prodi tertentu */}
              {isAdminInProdiPage && (
                <>
                  <Link
                    href={`/prodi/dashboard-prodi${prodiQuery}`}
                    className={`px-5 flex items-center text-sm font-semibold transition-all duration-150 ${
                      isActive("/prodi/dashboard-prodi")
                        ? "text-[#f3e412]"
                        : "text-white hover:text-[#f3e412]"
                    }`}
                  >
                    Dashboard Prodi
                  </Link>
                  <Link
                    href={`/prodi/simulasi-skor${prodiQuery}`}
                    className={`px-5 flex items-center text-sm font-semibold transition-all duration-150 ${
                      isActive("/prodi/simulasi-skor")
                        ? "text-[#f3e412]"
                        : "text-white hover:text-[#f3e412]"
                    }`}
                  >
                    Simulasi Skor
                  </Link>
                  <Link
                    href={`/prodi/evidence${prodiQuery}`}
                    className={`px-5 flex items-center text-sm font-semibold transition-all duration-150 ${
                      isActive("/prodi/evidence")
                        ? "text-[#f3e412]"
                        : "text-white hover:text-[#f3e412]"
                    }`}
                  >
                    Evidence
                  </Link>
                </>
              )}
            </>
          ) : (
            <>
              <Link
                href="/prodi/simulasi-skor"
                className={`px-6 flex items-center text-sm font-semibold transition-all duration-150 ${
                  isActive("/prodi/simulasi-skor")
                    ? "text-[#f3e412]"
                    : "text-white hover:text-[#f3e412]"
                }`}
              >
                Simulasi Skor
              </Link>
              <Link
                href="/prodi/dashboard-prodi"
                className={`px-6 flex items-center text-sm font-semibold transition-all duration-150 ${
                  isActive("/prodi/dashboard-prodi")
                    ? "text-[#f3e412]"
                    : "text-white hover:text-[#f3e412]"
                }`}
              >
                Dashboard Prodi
              </Link>
              <Link
                href="/prodi/evidence"
                className={`px-6 flex items-center text-sm font-semibold transition-all duration-150 ${
                  isActive("/prodi/evidence")
                    ? "text-[#f3e412]"
                    : "text-white hover:text-[#f3e412]"
                }`}
              >
                Evidence
              </Link>
            </>
          )}
        </div>

        {/* Kanan — info prodi + avatar */}
        <div className="flex items-center gap-3 px-5 border-l border-[#0060b8]">
          <div className="relative" ref={notificationRef}>
            <button
              type="button"
              onClick={() => setNotificationOpen((current) => !current)}
              className="relative flex h-9 w-9 items-center justify-center rounded-full text-white transition-colors hover:bg-[#0060b8] focus:outline-none focus:ring-2 focus:ring-yellow-400 focus:ring-offset-1 focus:ring-offset-[#00509d]"
              aria-label="Notifikasi"
            >
              <svg
                aria-hidden="true"
                viewBox="0 0 24 24"
                className="h-5 w-5"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M18 8a6 6 0 0 0-12 0c0 7-3 7-3 7h18s-3 0-3-7" />
                <path d="M13.73 21a2 2 0 0 1-3.46 0" />
              </svg>
              {unreadCount > 0 && (
                <span className="absolute -right-0.5 -top-0.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-bold leading-none text-white">
                  {unreadCount > 9 ? "9+" : unreadCount}
                </span>
              )}
            </button>

            {notificationOpen && (
              <div className="absolute right-0 mt-2 w-[min(24rem,calc(100vw-2rem))] overflow-hidden rounded-lg border border-gray-100 bg-white shadow-lg z-50">
                <div className="flex items-center justify-between border-b border-gray-100 px-4 py-3">
                  <div>
                    <p className="text-sm font-bold text-gray-800">Notifikasi</p>
                    <p className="text-xs text-gray-400">
                      {unreadCount} belum dibaca
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={markAllNotificationsRead}
                    className="text-xs font-semibold text-[#00509d] hover:text-[#003f7d]"
                  >
                    Tandai dibaca
                  </button>
                </div>

                <div className="max-h-96 overflow-y-auto">
                  {notifications.length === 0 ? (
                    <div className="px-4 py-6 text-center text-sm text-gray-500">
                      Tidak ada notifikasi.
                    </div>
                  ) : (
                    notifications.map((item) => {
                      const content = (
                        <div
                          className={`flex gap-3 px-4 py-3 text-left transition-colors hover:bg-gray-50 ${
                            item.is_read ? "bg-white" : "bg-blue-50/60"
                          }`}
                        >
                          <span
                            className={`mt-1 h-2.5 w-2.5 shrink-0 rounded-full ${severityClass(
                              item.severity,
                            )}`}
                          />
                          <span className="min-w-0 flex-1">
                            <span className="block text-sm font-semibold text-gray-800">
                              {item.judul}
                            </span>
                            <span className="mt-0.5 block text-xs leading-relaxed text-gray-500">
                              {item.pesan}
                            </span>
                          </span>
                        </div>
                      );

                      if (item.href) {
                        return (
                          <Link
                            key={item.id}
                            href={item.href}
                            onClick={() => {
                              markNotificationRead(item);
                              setNotificationOpen(false);
                            }}
                            className="block"
                          >
                            {content}
                          </Link>
                        );
                      }

                      return (
                        <button
                          key={item.id}
                          type="button"
                          onClick={() => markNotificationRead(item)}
                          className="block w-full"
                        >
                          {content}
                        </button>
                      );
                    })
                  )}
                </div>
              </div>
            )}
          </div>

          {/* Info konteks — nama prodi untuk non-admin, label role untuk admin */}
          <div className="text-right hidden sm:block">
            {role === "admin" ? (
              <p className="text-sm font-semibold text-white leading-none">
                Administrator
              </p>
            ) : role === "pimpinan" ? (
              <p className="text-sm font-semibold text-white leading-none">
                Pimpinan STEI
              </p>
            ) : (
              <>
                <p className="text-xs text-blue-200 leading-none mb-0.5">
                  Program Studi
                </p>
                <p className="text-sm font-semibold text-white leading-none">
                  {programStudi}
                </p>
              </>
            )}
          </div>

          {/* Avatar dropdown */}
          <div className="relative" ref={dropdownRef}>
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
                <Link
                  href="/program-studi"
                  onClick={() => setDropdownOpen(false)}
                  className="block w-full text-left px-4 py-2 text-sm text-gray-600 hover:bg-gray-50 transition-colors"
                >
                  Profil Program Studi
                </Link>
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
