"""DESCOM: investigação preliminar de limites geográficos no OpenStreetMap.

Esta rotina apenas produz candidatos para revisão humana. Ela nunca altera
config/regions.json nem habilita a descoberta comercial automaticamente.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "data" / "geography-pending"
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
]
USER_AGENT = "DESCOM/1.0 (GUIA COMERCIAL; https://github.com/eddypfernandes/Descom)"
TEMPORARY_HTTP_ERRORS = {429, 502, 503, 504}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def overpass(query: str) -> dict[str, Any]:
    body = urllib.parse.urlencode({"data": query}).encode("utf-8")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }
    failures: list[str] = []

    for endpoint in OVERPASS_ENDPOINTS:
        request = urllib.request.Request(endpoint, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=100) as response:
                payload = json.loads(response.read().decode("utf-8"))
            if not isinstance(payload.get("elements"), list):
                raise RuntimeError("Resposta do Overpass sem lista de elementos.")
            return payload
        except urllib.error.HTTPError as exc:
            failures.append(f"{endpoint}: HTTP {exc.code}")
            if exc.code not in TEMPORARY_HTTP_ERRORS:
                continue
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            failures.append(f"{endpoint}: {exc}")
        time.sleep(2)

    raise RuntimeError("Servidores Overpass indisponíveis: " + " | ".join(failures))


def find_federal_district_area() -> int:
    query = """
[out:json][timeout:45];
area["name"~"^Distrito Federal$",i]["admin_level"="4"];
out ids tags;
"""
    payload = overpass(query)
    areas = payload.get("elements", [])
    if not areas:
        raise RuntimeError(
            "Não foi possível identificar com segurança a área do Distrito Federal "
            "no OpenStreetMap. Nenhum candidato foi gerado."
        )
    if len(areas) > 1:
        raise RuntimeError(
            f"Foram encontradas {len(areas)} áreas candidatas para o DF. "
            "A identificação precisa de revisão antes de continuar."
        )
    area_id = areas[0].get("id")
    if not isinstance(area_id, int):
        raise RuntimeError("A área do Distrito Federal retornada não possui ID válido.")
    return area_id


def area_id_for(element: dict[str, Any]) -> int | None:
    osm_type = element.get("type")
    osm_id = element.get("id")
    if not isinstance(osm_id, int):
        return None
    if osm_type == "relation":
        return 3_600_000_000 + osm_id
    if osm_type == "way":
        return 2_400_000_000 + osm_id
    return None


def center_for(element: dict[str, Any]) -> list[float] | None:
    if isinstance(element.get("lat"), (int, float)) and isinstance(element.get("lon"), (int, float)):
        return [float(element["lat"]), float(element["lon"])]
    center = element.get("center") or {}
    if isinstance(center.get("lat"), (int, float)) and isinstance(center.get("lon"), (int, float)):
        return [float(center["lat"]), float(center["lon"])]
    return None


def find_candidates(name: str, df_area_id: int) -> list[dict[str, Any]]:
    safe_name = re.escape(name.strip())
    query = f"""
[out:json][timeout:75];
area({df_area_id})->.df;
(
  relation(area.df)["boundary"="administrative"]["name"~"^{safe_name}$",i];
  way(area.df)["boundary"="administrative"]["name"~"^{safe_name}$",i];
  relation(area.df)["place"~"^(suburb|town|village|neighbourhood)$"]["name"~"^{safe_name}$",i];
  way(area.df)["place"~"^(suburb|town|village|neighbourhood)$"]["name"~"^{safe_name}$",i];
  node(area.df)["place"~"^(suburb|town|village|neighbourhood)$"]["name"~"^{safe_name}$",i];
);
out center tags;
"""
    payload = overpass(query)
    candidates: list[dict[str, Any]] = []

    for element in payload.get("elements", []):
        tags = element.get("tags") or {}
        osm_type = element.get("type")
        osm_id = element.get("id")
        if osm_type not in {"node", "way", "relation"} or not isinstance(osm_id, int):
            continue

        boundary = tags.get("boundary")
        candidate_area_id = area_id_for(element) if boundary == "administrative" else None
        center = center_for(element)

        candidates.append({
            "osm_type": osm_type,
            "osm_id": osm_id,
            "name": tags.get("name") or name,
            "boundary": boundary,
            "admin_level": tags.get("admin_level"),
            "place": tags.get("place"),
            "area_id": candidate_area_id,
            "center": center,
            "usable_for_discovery": bool(candidate_area_id and center),
            "osm_url": f"https://www.openstreetmap.org/{osm_type}/{osm_id}",
            "tags": tags,
        })

    candidates.sort(
        key=lambda item: (
            not item["usable_for_discovery"],
            item["osm_type"] != "relation",
            str(item.get("admin_level") or "99"),
            item["osm_id"],
        )
    )
    return candidates


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Localiza candidatos geográficos no OSM sem ativar a região."
    )
    parser.add_argument("--name", required=True, help="Nome da localidade.")
    parser.add_argument("--uf", default="DF", help="UF da localidade (nesta fase, DF).")
    args = parser.parse_args()

    name = " ".join(args.name.split())
    uf = args.uf.strip().upper()

    if len(name) < 2:
        parser.error("O nome da localidade precisa ter pelo menos dois caracteres.")
    if uf != "DF":
        parser.error("Esta primeira versão investiga localidades do Distrito Federal (DF).")

    try:
        df_area_id = find_federal_district_area()
        candidates = find_candidates(name, df_area_id)

        output = {
            "schema_version": "1.0",
            "generated_at": now_iso(),
            "requested_locality": name,
            "uf": uf,
            "search_status": "candidates_found" if candidates else "no_candidates",
            "source": "OpenStreetMap / Overpass API",
            "attribution": "© OpenStreetMap contributors",
            "license": "Open Database License (ODbL)",
            "df_area_osm_id": df_area_id,
            "candidate_count": len(candidates),
            "review_required": True,
            "activation_allowed": False,
            "candidates": candidates,
            "message": (
                "Candidatos para conferência humana. Nenhum limite foi aprovado "
                "e nenhuma configuração de descoberta foi alterada."
            ),
        }

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_file = OUTPUT_DIR / f"{slugify(name)}-{uf.lower()}.json"
        temporary_file = output_file.with_suffix(".json.tmp")
        temporary_file.write_text(
            json.dumps(output, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        json.loads(temporary_file.read_text(encoding="utf-8"))
        temporary_file.replace(output_file)

        print(f"Localidade: {name}/{uf}")
        print(f"Candidatos encontrados: {len(candidates)}")
        print(f"Candidatos com área OSM utilizável: {sum(1 for item in candidates if item['usable_for_discovery'])}")
        print(f"Resultado: {output_file.relative_to(ROOT)}")
        print("Nenhuma região foi ativada. A aprovação humana continua obrigatória.")
        return 0

    except (OSError, ValueError, RuntimeError, urllib.error.URLError) as exc:
        print(f"Investigação geográfica interrompida: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
