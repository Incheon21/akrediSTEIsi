export const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export async function apiFetch(path: string, options?: RequestInit) {
    const token = localStorage.getItem("access_token");
    const res = await fetch(`${API_URL}${path}`, {
        cache: "no-store",
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...(token && { Authorization: `Bearer ${token}` }),
            ...options?.headers,
        },
    });
    return res;
}