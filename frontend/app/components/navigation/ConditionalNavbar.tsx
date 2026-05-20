"use client";

import { usePathname } from "next/navigation";
import Navbar from "./Navbar";
import { useAuth } from "../../hooks/useAuth";

export default function ConditionalNavbar() {
  const pathname = usePathname();
  const { user, loading } = useAuth();

  if (pathname === "/login") return null;

  const prodiName = loading ? "..." : (user?.program_studi?.nama || "");
  const prodiId = loading ? "" : (user?.program_studi_id || "");
  const fullName = loading ? "..." : (user?.nama || "User");
  const initial = loading ? "" : (user?.nama ? user.nama.charAt(0).toUpperCase() : "?");
  const role = loading ? "" : (user?.role || "");

  return (
    <Navbar
      programStudi={prodiName}
      programStudiId={prodiId}
      userName={fullName}
      userInitial={initial}
      role={role}
    />
  );
}
