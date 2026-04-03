import { useEffect, useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { apiFetch } from "@/app/services/api";

interface AuthUser {
    id: string;
    email: string;
    nama: string;
    role: string;
    program_studi_id: string;
    program_studi?: {
        id: string;
        nama: string;
        kode: string;
    };
}

export function useAuth() {
    const router = useRouter();
    const pathname = usePathname();
    const [user, setUser] = useState<AuthUser | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchUser() {
            try {
                const token = localStorage.getItem("access_token");
                if (!token) {
                    if (pathname !== "/login") {
                        router.push("/login");
                    }
                    setLoading(false);
                    return;
                }

                setLoading(true);
                const res = await apiFetch("/api/v1/auth/me");
                
                if (res.status === 401) {
                    localStorage.removeItem("access_token");
                    if (pathname !== "/login") {
                        router.push("/login");
                    }
                    setUser(null);
                    return;
                }

                if (!res.ok) {
                    throw new Error("Gagal mengambil profil user");
                }

                const data = await res.json();
                setUser({
                    id: data.id,
                    email: data.email,
                    nama: data.nama,
                    role: data.role?.name ?? "tim_prodi",
                    program_studi_id: data.program_studi_id,
                    program_studi: data.program_studi,
                });
            } catch (err) {
                console.error(err);
                setUser(null);
            } finally {
                setLoading(false);
            }
        }

        fetchUser();
    }, [router, pathname]);

    return { user, loading };
}