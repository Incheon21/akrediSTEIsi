"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/app/hooks/useAuth";
import { apiFetch } from "@/app/services/api";

interface ProdiProfile {
  id: string;
  kode: string;
  nama: string;
  jenjang: string;
  fakultas: string | null;
  perguruan_tinggi: string | null;
  akreditasi: string | null;
  no_sk_ban_pt: string | null;
  tanggal_akreditasi: string | null;
  tanggal_kadaluarsa: string | null;
  alamat: string | null;
  kota: string | null;
  kode_pos: string | null;
  nomor_telepon: string | null;
  email: string | null;
  website: string | null;
  no_sk_pendirian_pt: string | null;
  tanggal_sk_pendirian_pt: string | null;
  pejabat_sk_pendirian_pt: string | null;
  no_sk_pembukaan_ps: string | null;
  tanggal_sk_pembukaan_ps: string | null;
  pejabat_sk_pembukaan_ps: string | null;
  tahun_pertama_menerima_mahasiswa: number | null;
}

type EditableFields = Omit<ProdiProfile, "id" | "kode" | "jenjang">;

const EDITABLE_ROLES = ["koordinator", "admin"];

function Field({ label, value }: { label: string; value: string | number | null }) {
  return (
    <div>
      <p className="text-xs text-slate-500 mb-0.5">{label}</p>
      <p className="text-sm text-slate-800 font-medium">{value ?? <span className="text-slate-400 italic">Belum diisi</span>}</p>
    </div>
  );
}

function InputField({
  label,
  name,
  value,
  type = "text",
  onChange,
}: {
  label: string;
  name: string;
  value: string | number | null;
  type?: string;
  onChange: (name: string, value: string) => void;
}) {
  return (
    <div>
      <label className="text-xs text-slate-500 mb-0.5 block">{label}</label>
      <input
        type={type}
        value={value ?? ""}
        onChange={(e) => onChange(name, e.target.value)}
        className="w-full border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-[#00509d]/30 focus:border-[#00509d]"
      />
    </div>
  );
}

function SectionCard({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-white rounded-xl border border-slate-100 shadow-sm p-6">
      <h2 className="text-sm font-semibold text-[#00509d] uppercase tracking-wide mb-4">{title}</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">{children}</div>
    </div>
  );
}

export default function ProgramStudiPage() {
  const { user, loading: authLoading } = useAuth();
  const [profile, setProfile] = useState<ProdiProfile | null>(null);
  const [editing, setEditing] = useState(false);
  const [draft, setDraft] = useState<Partial<EditableFields>>({});
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const canEdit = EDITABLE_ROLES.includes(user?.role ?? "");

  useEffect(() => {
    if (!user?.program_studi_id) return;
    apiFetch(`/api/v1/program-studi/${user.program_studi_id}`)
      .then((r) => r.json())
      .then(setProfile)
      .catch(() => setError("Gagal memuat data program studi."));
  }, [user?.program_studi_id]);

  function startEdit() {
    if (!profile) return;
    setDraft({
      nama: profile.nama,
      fakultas: profile.fakultas,
      perguruan_tinggi: profile.perguruan_tinggi,
      akreditasi: profile.akreditasi,
      no_sk_ban_pt: profile.no_sk_ban_pt,
      tanggal_akreditasi: profile.tanggal_akreditasi?.slice(0, 10) ?? null,
      tanggal_kadaluarsa: profile.tanggal_kadaluarsa?.slice(0, 10) ?? null,
      alamat: profile.alamat,
      kota: profile.kota,
      kode_pos: profile.kode_pos,
      nomor_telepon: profile.nomor_telepon,
      email: profile.email,
      website: profile.website,
      no_sk_pendirian_pt: profile.no_sk_pendirian_pt,
      tanggal_sk_pendirian_pt: profile.tanggal_sk_pendirian_pt?.slice(0, 10) ?? null,
      pejabat_sk_pendirian_pt: profile.pejabat_sk_pendirian_pt,
      no_sk_pembukaan_ps: profile.no_sk_pembukaan_ps,
      tanggal_sk_pembukaan_ps: profile.tanggal_sk_pembukaan_ps?.slice(0, 10) ?? null,
      pejabat_sk_pembukaan_ps: profile.pejabat_sk_pembukaan_ps,
      tahun_pertama_menerima_mahasiswa: profile.tahun_pertama_menerima_mahasiswa,
    });
    setEditing(true);
    setSuccess(false);
  }

  function handleChange(name: string, value: string) {
    setDraft((prev) => ({ ...prev, [name]: value === "" ? null : value }));
  }

  async function handleSave() {
    if (!profile) return;
    setSaving(true);
    setError(null);
    try {
      const res = await apiFetch(`/api/v1/program-studi/${profile.id}`, {
        method: "PUT",
        body: JSON.stringify(draft),
      });
      if (!res.ok) throw new Error("Gagal menyimpan.");
      const updated = await res.json();
      setProfile(updated);
      setEditing(false);
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch {
      setError("Gagal menyimpan data. Silakan coba lagi.");
    } finally {
      setSaving(false);
    }
  }

  if (authLoading || !profile) {
    return (
      <div className="min-h-screen flex items-center justify-center text-slate-400 text-sm">
        Memuat data program studi...
      </div>
    );
  }

  const v = editing ? draft : profile;
  const val = (key: keyof EditableFields) => (v as Record<string, unknown>)[key] as string | number | null;

  return (
    <div className="min-h-screen bg-slate-50 py-8 px-4">
      <div className="max-w-4xl mx-auto space-y-5">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-slate-500 uppercase tracking-wide font-medium">Profil Program Studi</p>
            <h1 className="text-xl font-bold text-slate-800 mt-0.5">{profile.nama}</h1>
            <p className="text-xs text-slate-400 mt-0.5">{profile.jenjang} · {profile.kode}</p>
          </div>
          {canEdit && !editing && (
            <button
              onClick={startEdit}
              className="px-4 py-2 bg-[#00509d] text-white text-sm font-semibold rounded-lg hover:bg-[#003f7d] transition-colors"
            >
              Edit Profil
            </button>
          )}
          {editing && (
            <div className="flex gap-2">
              <button
                onClick={() => setEditing(false)}
                className="px-4 py-2 text-sm font-semibold text-slate-600 border border-slate-200 rounded-lg hover:bg-slate-100 transition-colors"
              >
                Batal
              </button>
              <button
                onClick={handleSave}
                disabled={saving}
                className="px-4 py-2 bg-[#00509d] text-white text-sm font-semibold rounded-lg hover:bg-[#003f7d] transition-colors disabled:opacity-50"
              >
                {saving ? "Menyimpan..." : "Simpan"}
              </button>
            </div>
          )}
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded-lg">{error}</div>
        )}
        {success && (
          <div className="bg-green-50 border border-green-200 text-green-700 text-sm px-4 py-3 rounded-lg">
            Data berhasil disimpan.
          </div>
        )}

        {/* Identitas Dasar */}
        <SectionCard title="Identitas Program Studi">
          {editing ? (
            <>
              <InputField label="Nama Program Studi" name="nama" value={val("nama")} onChange={handleChange} />
              <InputField label="Perguruan Tinggi" name="perguruan_tinggi" value={val("perguruan_tinggi")} onChange={handleChange} />
              <InputField label="Fakultas / Unit Pengelola" name="fakultas" value={val("fakultas")} onChange={handleChange} />
              <InputField label="Peringkat Akreditasi" name="akreditasi" value={val("akreditasi")} onChange={handleChange} />
              <InputField label="No. SK BAN-PT" name="no_sk_ban_pt" value={val("no_sk_ban_pt")} onChange={handleChange} />
              <InputField label="Tanggal Akreditasi" name="tanggal_akreditasi" value={val("tanggal_akreditasi")} type="date" onChange={handleChange} />
              <InputField label="Tanggal Kadaluarsa" name="tanggal_kadaluarsa" value={val("tanggal_kadaluarsa")} type="date" onChange={handleChange} />
            </>
          ) : (
            <>
              <Field label="Nama Program Studi" value={profile.nama} />
              <Field label="Perguruan Tinggi" value={profile.perguruan_tinggi} />
              <Field label="Fakultas / Unit Pengelola" value={profile.fakultas} />
              <Field label="Peringkat Akreditasi" value={profile.akreditasi} />
              <Field label="No. SK BAN-PT" value={profile.no_sk_ban_pt} />
              <Field label="Tanggal Akreditasi" value={profile.tanggal_akreditasi?.slice(0, 10) ?? null} />
              <Field label="Tanggal Kadaluarsa" value={profile.tanggal_kadaluarsa?.slice(0, 10) ?? null} />
            </>
          )}
        </SectionCard>

        {/* Kontak */}
        <SectionCard title="Alamat & Kontak">
          {editing ? (
            <>
              <div className="md:col-span-2">
                <InputField label="Alamat" name="alamat" value={val("alamat")} onChange={handleChange} />
              </div>
              <InputField label="Kota" name="kota" value={val("kota")} onChange={handleChange} />
              <InputField label="Kode Pos" name="kode_pos" value={val("kode_pos")} onChange={handleChange} />
              <InputField label="Nomor Telepon" name="nomor_telepon" value={val("nomor_telepon")} onChange={handleChange} />
              <InputField label="Email" name="email" value={val("email")} type="email" onChange={handleChange} />
              <div className="md:col-span-2">
                <InputField label="Website" name="website" value={val("website")} onChange={handleChange} />
              </div>
            </>
          ) : (
            <>
              <div className="md:col-span-2"><Field label="Alamat" value={profile.alamat} /></div>
              <Field label="Kota" value={profile.kota} />
              <Field label="Kode Pos" value={profile.kode_pos} />
              <Field label="Nomor Telepon" value={profile.nomor_telepon} />
              <Field label="Email" value={profile.email} />
              <div className="md:col-span-2"><Field label="Website" value={profile.website} /></div>
            </>
          )}
        </SectionCard>

        {/* SK Pendirian PT */}
        <SectionCard title="SK Pendirian Perguruan Tinggi">
          {editing ? (
            <>
              <InputField label="No. SK Pendirian PT" name="no_sk_pendirian_pt" value={val("no_sk_pendirian_pt")} onChange={handleChange} />
              <InputField label="Tanggal SK Pendirian PT" name="tanggal_sk_pendirian_pt" value={val("tanggal_sk_pendirian_pt")} type="date" onChange={handleChange} />
              <div className="md:col-span-2">
                <InputField label="Pejabat Penandatangan SK Pendirian PT" name="pejabat_sk_pendirian_pt" value={val("pejabat_sk_pendirian_pt")} onChange={handleChange} />
              </div>
            </>
          ) : (
            <>
              <Field label="No. SK Pendirian PT" value={profile.no_sk_pendirian_pt} />
              <Field label="Tanggal SK Pendirian PT" value={profile.tanggal_sk_pendirian_pt?.slice(0, 10) ?? null} />
              <div className="md:col-span-2"><Field label="Pejabat Penandatangan SK Pendirian PT" value={profile.pejabat_sk_pendirian_pt} /></div>
            </>
          )}
        </SectionCard>

        {/* SK Pembukaan PS */}
        <SectionCard title="SK Pembukaan Program Studi">
          {editing ? (
            <>
              <InputField label="No. SK Pembukaan PS" name="no_sk_pembukaan_ps" value={val("no_sk_pembukaan_ps")} onChange={handleChange} />
              <InputField label="Tanggal SK Pembukaan PS" name="tanggal_sk_pembukaan_ps" value={val("tanggal_sk_pembukaan_ps")} type="date" onChange={handleChange} />
              <div className="md:col-span-2">
                <InputField label="Pejabat Penandatangan SK Pembukaan PS" name="pejabat_sk_pembukaan_ps" value={val("pejabat_sk_pembukaan_ps")} onChange={handleChange} />
              </div>
              <InputField label="Tahun Pertama Menerima Mahasiswa" name="tahun_pertama_menerima_mahasiswa" value={val("tahun_pertama_menerima_mahasiswa")} type="number" onChange={handleChange} />
            </>
          ) : (
            <>
              <Field label="No. SK Pembukaan PS" value={profile.no_sk_pembukaan_ps} />
              <Field label="Tanggal SK Pembukaan PS" value={profile.tanggal_sk_pembukaan_ps?.slice(0, 10) ?? null} />
              <div className="md:col-span-2"><Field label="Pejabat Penandatangan SK Pembukaan PS" value={profile.pejabat_sk_pembukaan_ps} /></div>
              <Field label="Tahun Pertama Menerima Mahasiswa" value={profile.tahun_pertama_menerima_mahasiswa} />
            </>
          )}
        </SectionCard>
      </div>
    </div>
  );
}
