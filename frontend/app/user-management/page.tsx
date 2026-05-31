"use client";
import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/app/services/api";
import { useAuth } from "@/app/hooks/useAuth";

interface Role {
  id: string;
  name: string;
}

interface ProgramStudi {
  id: string;
  kode: string;
  nama: string;
}

interface User {
  id: string;
  email: string;
  nama: string;
  nip: string | null;
  is_active: boolean;
  role: Role;
  program_studi: ProgramStudi | null;
  created_at: string;
  updated_at: string;
}

interface UserForm {
  nama: string;
  email: string;
  password: string;
  nip: string;
  role_id: string;
  program_studi_id: string;
  is_active: boolean;
}

type FormErrors = Partial<Record<keyof UserForm | "api", string>>;

const EMPTY_FORM: UserForm = {
  nama: "",
  email: "",
  password: "",
  nip: "",
  role_id: "",
  program_studi_id: "",
  is_active: true,
};

interface ModalProps {
  title: string;
  onClose: () => void;
  children: React.ReactNode;
}

function Modal({ title, onClose, children }: ModalProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div
        className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        onClick={onClose}
      />
      <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-lg mx-4 overflow-hidden">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 className="text-lg font-semibold text-gray-800">{title}</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors text-xl leading-none"
          >
            ×
          </button>
        </div>
        <div className="px-6 py-5">{children}</div>
      </div>
    </div>
  );
}

interface ConfirmDialogProps {
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

function ConfirmDialog({ message, onConfirm, onCancel }: ConfirmDialogProps) {
  return (
    <Modal title="Konfirmasi" onClose={onCancel}>
      <p className="text-gray-600 mb-6">{message}</p>
      <div className="flex gap-3 justify-end">
        <button
          onClick={onCancel}
          className="px-4 py-2 rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 transition-colors text-sm"
        >
          Batal
        </button>
        <button
          onClick={onConfirm}
          className="px-4 py-2 rounded-lg bg-red-500 hover:bg-red-600 text-white transition-colors text-sm"
        >
          Hapus
        </button>
      </div>
    </Modal>
  );
}

interface UserFormProps {
  initialData?: UserForm;
  roles: Role[];
  programStudiList: ProgramStudi[];
  onSubmit: (payload: UserForm) => Promise<void>;
  onClose: () => void;
  isEdit: boolean;
}

function UserFormComponent({
  initialData,
  roles,
  programStudiList,
  onSubmit,
  onClose,
  isEdit,
}: UserFormProps) {
  const [form, setForm] = useState<UserForm>(initialData ?? EMPTY_FORM);
  const [loading, setLoading] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});

  function setField<K extends keyof UserForm>(field: K, value: UserForm[K]) {
    setForm((f) => ({ ...f, [field]: value }));
    setErrors((e) => ({ ...e, [field]: undefined }));
  }

  function validate(): FormErrors {
    const e: FormErrors = {};
    if (!form.nama.trim()) e.nama = "Nama wajib diisi";
    if (!form.email.trim()) e.email = "Email wajib diisi";
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email))
      e.email = "Format email tidak valid";
    if (!isEdit && !form.password) e.password = "Password wajib diisi";
    if (form.nip && !/^\d{18}$/.test(form.nip)) e.nip = "NIP harus terdiri dari 18 digit angka";
    if (!form.role_id) e.role_id = "Role wajib dipilih";
    return e;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    const errs = validate();
    if (Object.keys(errs).length) {
      setErrors(errs);
      return;
    }
    setLoading(true);
    try {
      const payload = { ...form };
      if (isEdit && !payload.password) delete (payload as Partial<UserForm>).password;
      await onSubmit(payload);
    } catch (err: any) {
      setErrors((e) => ({ ...e, api: err.message }));
    } finally {
      setLoading(false);
    }
  }

  const inputCls = (field: keyof UserForm) =>
    `w-full px-3 py-2 rounded-lg border text-sm outline-none transition-colors ${
      errors[field]
        ? "border-red-300 focus:border-red-400 bg-red-50"
        : "border-gray-200 focus:border-indigo-400 bg-gray-50 focus:bg-white"
    }`;

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">

        <div className="col-span-2">
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Nama Lengkap
          </label>
          <input
            className={inputCls("nama")}
            value={form.nama}
            onChange={(e) => setField("nama", e.target.value)}
            placeholder="Masukkan nama lengkap"
          />
          {errors.nama && (
            <p className="text-red-500 text-xs mt-1">{errors.nama}</p>
          )}
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Email
          </label>
          <input
            type="email"
            className={inputCls("email")}
            value={form.email}
            onChange={(e) => setField("email", e.target.value)}
            placeholder="email@domain.com"
          />
          {errors.email && (
            <p className="text-red-500 text-xs mt-1">{errors.email}</p>
          )}
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">
            NIP
          </label>
          <input
            className={inputCls("nip")}
            value={form.nip}
            onChange={(e) => setField("nip", e.target.value.replace(/\D/g, "").slice(0, 18))}
            placeholder="Opsional"
          />
          {errors.nip && (
            <p className="text-red-500 text-xs mt-1">{errors.nip}</p>
          )}
        </div>

        <div className="col-span-2">
          <label className="block text-xs font-medium text-gray-500 mb-1">
            {isEdit
              ? "Password Baru (kosongkan jika tidak diubah)"
              : "Password"}
          </label>
          <input
            type="password"
            className={inputCls("password")}
            value={form.password}
            onChange={(e) => setField("password", e.target.value)}
            placeholder={isEdit ? "••••••••" : "Masukkan password"}
          />
          {errors.password && (
            <p className="text-red-500 text-xs mt-1">{errors.password}</p>
          )}
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Role
          </label>
          <select
            className={inputCls("role_id")}
            value={form.role_id}
            onChange={(e) => setField("role_id", e.target.value)}
          >
            <option value="">Pilih role</option>
            {roles.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name}
              </option>
            ))}
          </select>
          {errors.role_id && (
            <p className="text-red-500 text-xs mt-1">{errors.role_id}</p>
          )}
        </div>

        <div>
          <label className="block text-xs font-medium text-gray-500 mb-1">
            Program Studi
          </label>
          <select
            className={inputCls("program_studi_id")}
            value={form.program_studi_id}
            onChange={(e) => setField("program_studi_id", e.target.value)}
          >
            <option value="">— Tidak ada —</option>
            {programStudiList.map((p) => (
              <option key={p.id} value={p.id}>
                {p.kode} – {p.nama}
              </option>
            ))}
          </select>
        </div>

        <div className="col-span-2 flex items-center gap-2">
          <button
            type="button"
            onClick={() => setField("is_active", !form.is_active)}
            className={`relative w-10 h-5 rounded-full transition-colors ${
              form.is_active ? "bg-indigo-500" : "bg-gray-300"
            }`}
          >
            <span
              className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${
                form.is_active ? "translate-x-5" : ""
              }`}
            />
          </button>
          <span className="text-sm text-gray-600">
            {form.is_active ? "Aktif" : "Nonaktif"}
          </span>
        </div>
      </div>

      <div className="flex gap-3 justify-end pt-2">
        {errors.api && (
          <p className="flex-1 text-red-500 text-sm self-center">{errors.api}</p>
        )}
        <button
          type="button"
          onClick={onClose}
          className="px-4 py-2 rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50 transition-colors text-sm"
        >
          Batal
        </button>
        <button
          type="submit"
          disabled={loading}
          className="px-5 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 disabled:opacity-60 text-white transition-colors text-sm font-medium"
        >
          {loading ? "Menyimpan..." : isEdit ? "Simpan Perubahan" : "Tambah User"}
        </button>
      </div>
    </form>
  );
}

function StatusBadge({ active }: { active: boolean }) {
  return (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
        active
          ? "bg-green-100 text-green-700"
          : "bg-gray-100 text-gray-500"
      }`}
    >
      <span
        className={`w-1.5 h-1.5 rounded-full ${
          active ? "bg-green-500" : "bg-gray-400"
        }`}
      />
      {active ? "Aktif" : "Nonaktif"}
    </span>
  );
}

export default function UserManagement() {
  const router = useRouter();
  const { user: authUser, loading: authLoading } = useAuth();

  const [users, setUsers] = useState<User[]>([]);
  const [roles, setRoles] = useState<Role[]>([]);
  const [programStudiList, setProgramStudiList] = useState<ProgramStudi[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [showCreate, setShowCreate] = useState(false);
  const [editUser, setEditUser] = useState<UserForm & { id: string } | null>(null);
  const [deleteUser, setDeleteUser] = useState<User | null>(null);

  const [search, setSearch] = useState("");
  const [filterRole, setFilterRole] = useState("");

  useEffect(() => {
    if (!authLoading && authUser?.role !== "admin") {
      router.replace("/login");
    }
  }, [authLoading, authUser, router]);

  const fetchUsers = useCallback(async () => {
    const res = await apiFetch("/api/v1/user-management/users");
    const data = await res.json();
    setUsers(data.users);
  }, []);

  useEffect(() => {
    if (authLoading || authUser?.role !== "admin") return;
    async function init() {
      setLoading(true);
      try {
        const [usersRes, rolesRes, prodiRes] = await Promise.all([
          apiFetch("/api/v1/user-management/users"),
          apiFetch("/api/v1/user-management/roles"),
          apiFetch("/api/v1/user-management/program-studi"),
        ]);
        const [usersData, rolesData, prodiData] = await Promise.all([
          usersRes.json(),
          rolesRes.json(),
          prodiRes.json(),
        ]);
        setUsers(usersData.users);
        setRoles(rolesData.roles ?? []);
        setProgramStudiList(prodiData.program_studi ?? []);
      } catch (err) {
        setError("Gagal memuat data.");
        console.error(err);
      } finally {
        setLoading(false);
      }
    }
    init();
  }, [authLoading, authUser]);

  async function handleCreate(payload: UserForm) {
    const res = await apiFetch("/api/v1/user-management/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      const detail = err.detail;
      throw new Error(
        Array.isArray(detail)
          ? detail.map((d: any) => d.msg).join(", ")
          : detail ?? "Gagal menambah user"
      );
    }
    setShowCreate(false);
    await fetchUsers();
  }

  async function handleUpdate(payload: UserForm) {
    if (!editUser) return;
    const res = await apiFetch(`/api/v1/user-management/users/${editUser.id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json();
      const detail = err.detail;
      throw new Error(
        Array.isArray(detail)
          ? detail.map((d: any) => d.msg).join(", ")
          : detail ?? "Gagal memperbarui user"
      );
    }
    setEditUser(null);
    await fetchUsers();
  }

  async function handleDelete() {
    if (!deleteUser) return;
    await apiFetch(`/api/v1/user-management/users/${deleteUser.id}`, {
      method: "DELETE",
    });
    setDeleteUser(null);
    await fetchUsers();
  }

  const filtered = users.filter((u) => {
    const q = search.toLowerCase();
    const matchSearch =
      !q ||
      u.nama.toLowerCase().includes(q) ||
      u.email.toLowerCase().includes(q) ||
      (u.nip?.includes(q) ?? false);
    const matchRole = !filterRole || u.role?.id === filterRole;
    return matchSearch && matchRole;
  });

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
  
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">
              Manajemen Pengguna
            </h1>
            <p className="text-sm text-gray-500 mt-0.5">
              {users.length} pengguna terdaftar
            </p>
          </div>
          <button
            onClick={() => setShowCreate(true)}
            className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition-colors shadow-sm"
          >
            <span className="text-lg leading-none">+</span>
            Tambah Pengguna
          </button>
        </div>

        <div className="flex gap-3 mb-4">
          <div className="relative flex-1 max-w-sm">
            <svg
              className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
              />
            </svg>
            <input
              className="w-full pl-9 pr-3 py-2 text-sm border border-gray-200 rounded-lg bg-white focus:outline-none focus:border-indigo-400 transition-colors"
              placeholder="Cari nama, email, atau NIP..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <select
            className="px-3 py-2 text-sm border border-gray-200 rounded-lg bg-white focus:outline-none focus:border-indigo-400 transition-colors"
            value={filterRole}
            onChange={(e) => setFilterRole(e.target.value)}
          >
            <option value="">Semua Role</option>
            {roles.map((r) => (
              <option key={r.id} value={r.id}>
                {r.name}
              </option>
            ))}
          </select>
        </div>

        <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
          {loading ? (
            <div className="py-20 text-center text-gray-400 text-sm">
              Memuat data...
            </div>
          ) : error ? (
            <div className="py-20 text-center text-red-500 text-sm">
              {error}
            </div>
          ) : filtered.length === 0 ? (
            <div className="py-20 text-center text-gray-400 text-sm">
              Tidak ada data pengguna.
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-100 bg-gray-50/60">
                  {[
                    "Nama",
                    "Email",
                    "NIP",
                    "Program Studi",
                    "Role",
                    "Status",
                    "Aksi",
                  ].map((h, i) => (
                    <th
                      key={h}
                      className={`px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide ${
                        i === 6 ? "text-right" : "text-left"
                      }`}
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {filtered.map((user) => (
                  <tr
                    key={user.id}
                    className="hover:bg-gray-50/50 transition-colors"
                  >
                    <td className="px-5 py-3.5 font-medium text-gray-800 whitespace-nowrap">
                      {user.nama}
                    </td>
                    <td className="px-5 py-3.5 text-gray-500 whitespace-nowrap">
                      {user.email}
                    </td>
                    <td className="px-5 py-3.5 text-gray-500 whitespace-nowrap">
                      {user.nip ?? "—"}
                    </td>
                    <td className="px-5 py-3.5 text-gray-500 whitespace-nowrap">
                      {user.program_studi ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded bg-blue-50 text-blue-700 text-xs font-medium">
                          {user.program_studi.kode}
                        </span>
                      ) : (
                        "—"
                      )}
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap">
                      <span className="inline-flex items-center px-2 py-0.5 rounded bg-indigo-50 text-indigo-700 text-xs font-medium">
                        {user.role?.name}
                      </span>
                    </td>
                    <td className="px-5 py-3.5 whitespace-nowrap">
                      <StatusBadge active={user.is_active} />
                    </td>
                    <td className="px-5 py-3.5 text-right whitespace-nowrap">
                      <div className="inline-flex gap-1">
                        <button
                          onClick={() =>
                            setEditUser({
                              id: user.id,
                              nama: user.nama,
                              email: user.email,
                              password: "",
                              nip: user.nip ?? "",
                              role_id: user.role?.id ?? "",
                              program_studi_id: user.program_studi?.id ?? "",
                              is_active: user.is_active,
                            })
                          }
                          className="px-3 py-1.5 rounded-lg text-xs font-medium text-indigo-600 hover:bg-indigo-50 transition-colors"
                        >
                          Edit
                        </button>
                        {user.id !== authUser?.id && (
                          <button
                            onClick={() => setDeleteUser(user)}
                            className="px-3 py-1.5 rounded-lg text-xs font-medium text-red-500 hover:bg-red-50 transition-colors"
                          >
                            Hapus
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {showCreate && (
        <Modal title="Tambah Pengguna Baru" onClose={() => setShowCreate(false)}>
          <UserFormComponent
            roles={roles}
            programStudiList={programStudiList}
            onSubmit={handleCreate}
            onClose={() => setShowCreate(false)}
            isEdit={false}
          />
        </Modal>
      )}

      {editUser && (
        <Modal title="Edit Pengguna" onClose={() => setEditUser(null)}>
          <UserFormComponent
            initialData={editUser}
            roles={roles}
            programStudiList={programStudiList}
            onSubmit={handleUpdate}
            onClose={() => setEditUser(null)}
            isEdit={true}
          />
        </Modal>
      )}

      {deleteUser && (
        <ConfirmDialog
          message={`Hapus pengguna "${deleteUser.nama}"? Tindakan ini tidak dapat dibatalkan.`}
          onConfirm={handleDelete}
          onCancel={() => setDeleteUser(null)}
        />
      )}
    </div>
  );
}
