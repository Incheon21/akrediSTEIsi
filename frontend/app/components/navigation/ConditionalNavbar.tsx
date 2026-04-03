"use client";

import { usePathname } from "next/navigation";
import Navbar from "./Navbar";
import { useAuth } from "../../hooks/useAuth";

export default function ConditionalNavbar() {
  const pathname = usePathname();
  const { user } = useAuth();

  if (pathname === "/login") return null;

  const prodiName = user?.program_studi?.nama || "Program Studi";
  const fullName = user?.nama || "Admin";
  const initial = user?.nama ? user.nama.charAt(0).toUpperCase() : "A";

  return <Navbar programStudi={prodiName} userName={fullName} userInitial={initial} />;
}
