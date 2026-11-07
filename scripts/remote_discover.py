"""ADÃO remoto: consulta OSM para áreas recebidas do painel DESCOM."""
from __future__ import annotations
import json, os, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import main as collector

def stamp():
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    json.loads(tmp.read_text(encoding="utf-8"))
    tmp.replace(path)

def push_status(path, data, execution_id):
    save(path, data)
    subprocess.run(["git", "add", str(path.relative_to(ROOT))], cwd=ROOT, check=True)
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode == 1:
        subprocess.run(["git", "commit", "-m", f"DESCOM: andamento {execution_id}"], cwd=ROOT, check=True)
        subprocess.run(["git", "push"], cwd=ROOT, check=True)

def main():
    event_path = os.environ.get("GITHUB_EVENT_PATH", "")
    event = json.loads(Path(event_path).read_text(encoding="utf-8")) if event_path else {}
    inputs = event.get("inputs", {})
    execution_id = inputs.get("execution_id", "").strip()
    if not execution_id or not all(c.isalnum() or c == "-" for c in execution_id):
        raise ValueError("Identificador de execução inválido.")
    areas = json.loads(inputs.get("areas_json", "[]"))
    if not isinstance(areas, list) or not areas:
        raise ValueError("Nenhuma área foi enviada.")
    jobs = ROOT / "data" / "jobs"
    status_path = jobs / f"{execution_id}.status.json"
    result_path = jobs / f"{execution_id}.json"
    status = {"execution_id": execution_id, "status": "EM_ANDAMENTO", "stage": "Preparando descoberta",
              "total_areas": len(areas), "areas_completed": 0, "total_found": 0,
              "current_area": "", "updated_at": stamp(), "error": None}
    unique, summaries = {}, []
    push_status(status_path, status, execution_id)
    try:
        for n, area in enumerate(areas, 1):
            for key in ("exec_id", "area_id", "area_name", "locality", "uf", "osm_type", "osm_id"):
                if str(area.get(key, "")).strip() == "":
                    raise ValueError(f"Campo {key} ausente na área {n}.")
            if area["osm_type"].lower() != "relation" or not str(area["osm_id"]).isdigit():
                raise ValueError(f"Identificador OSM inválido: {area['area_name']}.")
            status.update(stage="Consultando OpenStreetMap",
                          current_area=f"{area['locality']} / {area['area_name']}", updated_at=stamp())
            push_status(status_path, status, execution_id)
            collector.REGION = str(area["area_name"])
            collector.CITY = str(area["locality"])
            collector.UF = str(area["uf"]).upper()
            collector.AREA_ID = int(area["osm_id"]) + 3600000000
            elements = collector.request_overpass()
            status.update(stage="Analisando estabelecimentos encontrados", updated_at=stamp())
            push_status(status_path, status, execution_id)
            count = 0
            for element in elements:
                record = collector.build_record(element, collector.now_iso())
                if record:
                    record.update(descom_exec_id=int(area["exec_id"]), descom_area_id=int(area["area_id"]),
                                  descom_locality=str(area["locality"]), descom_uf=str(area["uf"]).upper())
                    unique.setdefault(record["external_id"], record)
                    count += 1
            summaries.append({"exec_id": int(area["exec_id"]), "area_id": int(area["area_id"]),
                              "area_name": area["area_name"], "locality": area["locality"],
                              "osm_elements_received": len(elements), "establishments_found": count,
                              "status": "CONCLUIDA"})
            status.update(areas_completed=n, total_found=len(unique),
                          stage="Área concluída" if n < len(areas) else "Finalizando resultados",
                          updated_at=stamp())
            if n < len(areas):
                push_status(status_path, status, execution_id)
        result = {"schema_version": "1.0", "execution_id": execution_id, "status": "CONCLUIDA",
                  "generated_at": stamp(), "source": "OpenStreetMap",
                  "attribution": "© OpenStreetMap contributors", "license": "Open Database License (ODbL)",
                  "review_required_before_publication": True, "total_areas": len(areas),
                  "total_found": len(unique), "areas": summaries, "establishments": list(unique.values())}
        save(result_path, result)
        status.update(status="CONCLUIDA", stage="Descoberta concluída; aguardando importação no DESCOM",
                      areas_completed=len(areas), total_found=len(unique), current_area="", updated_at=stamp())
        save(status_path, status)
        print(f"Execução {execution_id}: {len(unique)} estabelecimentos.")
    except Exception as exc:
        status.update(status="ERRO", stage="Descoberta interrompida", error=str(exc), updated_at=stamp())
        try:
            push_status(status_path, status, execution_id)
        except Exception as push_exc:
            print(f"Falha ao publicar status: {push_exc}", file=sys.stderr)
        raise

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ADÃO: {exc}", file=sys.stderr)
        raise SystemExit(1)
