from sqlalchemy.orm import Session

from app.models.simulasi import IndikatorSimulasi, KomponenPenilaian, MatriksAkreditasi
from app.schemas.simulasi import SimulasiRequest, SimulasiResponse


class SimulasiService:
    def __init__(self, db: Session):
        self.db = db

    def _evaluasi_formula(self, formula: str, variables: dict) -> float:
        try:
            # Safely evaluate formula with given variables
            # Replace variables in formula
            import math

            allowed_names = {"math": math, "min": min, "max": max}
            allowed_names.update(variables)
            return float(eval(formula, {"__builtins__": {}}, allowed_names))
        except Exception:
            return 0.0

    def _hitung_skor_mentah(
        self, indikator_db: IndikatorSimulasi, nilai_input: float
    ) -> float:
        tipe = indikator_db.tipe_evaluasi
        config = indikator_db.konfigurasi_rumus

        if tipe == "DIRECT_SCORE":
            return min(config.get("max", 4.0), max(config.get("min", 0.0), nilai_input))

        elif tipe == "LINEAR_SCALE":
            if nilai_input >= config.get("max", float("inf")):
                return 4.0
            if nilai_input <= config.get("min", float("-inf")):
                return 0.0
            formula = config.get("formula", "")
            if formula:
                # Get the variable name from the formula (e.g. BOP, DPD)
                # For simplicity, we pass it as a generic variable
                vars_dict = {
                    "BOP": nilai_input,
                    "DPD": nilai_input,
                    "DPkMD": nilai_input,
                    "RIPK": nilai_input,
                    "PTW": nilai_input,
                    "PPDMhs": nilai_input,
                    "PKDMhs": nilai_input,
                }
                return min(4.0, max(0.0, self._evaluasi_formula(formula, vars_dict)))
            return 0.0

        elif tipe == "LESS_IS_BETTER":
            ideal_min = config.get("ideal_min", 0)
            ideal_max = config.get("ideal_max", 0)
            batas_atas = config.get("batas_atas", float("inf"))
            if ideal_min <= nilai_input <= ideal_max:
                return 4.0
            if nilai_input > batas_atas:
                return 0.0
            formula = config.get("formula", "")
            if formula:
                vars_dict = {"RBK": nilai_input, "MS": nilai_input}
                return min(4.0, max(0.0, self._evaluasi_formula(formula, vars_dict)))
            return 0.0

        elif tipe == "STEP_SCALE":
            steps = config.get("steps", [])
            for step in steps:
                if step.get("min", 0) <= nilai_input <= step.get("max", float("inf")):
                    return float(step.get("score", 0))
            return 0.0

        elif tipe == "PIECEWISE":
            conditions = config.get("conditions", [])
            for cond in conditions:
                condition_str = cond.get("condition", "")
                formula_str = cond.get("formula", "")
                vars_dict = {"PJP": nilai_input}

                # Check condition
                # Transform "PJP < 0.2" to Python eval
                try:
                    is_true = eval(condition_str, {"__builtins__": {}}, vars_dict)
                    if is_true:
                        return min(
                            4.0,
                            max(0.0, self._evaluasi_formula(formula_str, vars_dict)),
                        )
                except Exception:
                    continue
            return 0.0

        return min(4.0, max(0.0, nilai_input))

    def process_simulasi(self, request: SimulasiRequest) -> SimulasiResponse:
        matriks = (
            self.db.query(MatriksAkreditasi)
            .filter(
                MatriksAkreditasi.lembaga == request.lembaga,
                MatriksAkreditasi.jenjang == request.jenjang,
            )
            .first()
        )

        if not matriks:
            raise ValueError("Matriks tidak ditemukan")

        breakdown_skor = {}
        total_nilai_akhir = 0.0

        for komponen in matriks.komponen:
            skor_komponen = 0.0
            data_list = []
            if komponen.nama.lower() == "input":
                data_list = request.data_input
            elif komponen.nama.lower() == "proses":
                data_list = request.data_proses
            elif komponen.nama.lower() == "output":
                data_list = request.data_output

            for item in data_list:
                indikator_db = next(
                    (
                        i
                        for i in komponen.indikator
                        if i.kode_indikator == item.kode_indikator
                    ),
                    None,
                )
                if indikator_db:
                    skor = self._hitung_skor_mentah(indikator_db, item.nilai_input)
                    skor_komponen += skor

            # Asumsi rata-rata dari skor_komponen * bobot. Bobot bisa dalam persentase (e.g. 25.0)
            num_indikator = len(komponen.indikator) if komponen.indikator else 1
            rata_rata = skor_komponen / num_indikator

            # Since total bobot = 100, we divide by 100 if bobot is in percentage.
            nilai_berbobot = (rata_rata / 4.0) * komponen.bobot * 4.0
            # Or if bobot is 25%, and max score is 4.0: (rata_rata * komponen.bobot) is up to (4 * 25) = 100
            # Wait, max total score in LAM Teknik is typically 400.
            # If bobot is 25, 35, 40 -> total = 100. (rata_rata * bobot) = 4 * 100 = 400.
            nilai_berbobot = rata_rata * komponen.bobot

            breakdown_skor[komponen.nama] = nilai_berbobot
            total_nilai_akhir += nilai_berbobot

        status_prediksi = "Baik"
        keterangan = "Memenuhi Syarat Minimum"

        # Syarat perlu Unggul dan Baik Sekali
        if request.lembaga == "TEKNIK":
            if total_nilai_akhir >= 361:
                status_prediksi = "Unggul"
                keterangan = "Nilai Akhir memenuhi syarat Unggul (>= 361)"
            elif total_nilai_akhir >= 301:
                status_prediksi = "Baik Sekali"
                keterangan = "Nilai Akhir memenuhi syarat Baik Sekali (>= 301)"
        elif request.lembaga == "INFOKOM":
            if total_nilai_akhir >= 361:
                status_prediksi = "Unggul"
                keterangan = "Nilai Akhir memenuhi syarat Unggul (>= 361)"
            elif total_nilai_akhir >= 301:
                status_prediksi = "Baik Sekali"
                keterangan = "Nilai Akhir memenuhi syarat Baik Sekali (>= 301)"

            if total_nilai_akhir < 321 and status_prediksi == "Unggul":
                # Example constraint
                status_prediksi = "Baik Sekali"
                keterangan = "Penalti: Tidak memenuhi syarat minimum komponen tertentu"

        return SimulasiResponse(
            nilai_akhir=total_nilai_akhir,
            status_prediksi=status_prediksi,
            keterangan=keterangan,
            breakdown_skor=breakdown_skor,
        )
