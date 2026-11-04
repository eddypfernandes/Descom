"""DESCOM: investigação geográfica preliminar via Nominatim/OSM.

Gera candidatos para revisão humana. Nunca altera config/regions.json
nem habilita a descoberta comercial automaticamente.
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
USER_AGENT = "DESCOM/1.0 (GUIA COMERCIAL; https://github.com/eddypfernandes/Descom)"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", "-", value).strip("-")


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    return "".join(c for c in value if not unicodedata.combining(c))


def nominatim_search(name: str) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({
        "format": "jsonv2",
        "q": f"{name}, Distrito Federal, Brasil",
        "countrycodes": "br",
        "addressdetails": 1,
        "extratags": 1,
        "namedetails": 1,
        "polygon_geojson": 1,
        "limit": 10,
    })
    request = urllib.request.Request(
        f"https://nominatim.openstreetmap.org/search?{params}",
        headers={
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Nominatim respondeu HTTP {exc.code}.") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"Falha na consulta ao Nominatim: {exc}") from exc

    if not isinstance(payload, list):
        raise RuntimeError("Resposta do Nominatim em formato inesperado.")
    return payload


def area_id_for(osm_type: str, osm_id: int) -> int | None:
    if osm_type == "relation":
        return 3_600_000_000 + osm_id
    if osm_type == "way":
        return 2_400_000_000 + osm_id
    return None


def build_candidates(name: str, results: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    requested = normalize(name.strip())

    for item in results:
        address = item.get("address") or {}
        state = str(address.get("state") or "")
        country_code = str(address.get("country_code") or "").lower()
        display_name = str(item.get("display_name") or "")
        name_match = normalize(str(item.get("name") or "")) == requested
        display_match = requested in normalize(display_name)

        # Evita aceitar resultados homônimos de outra unidade federativa.
        if country_code != "br":
            continue
        if "distrito federal" not in normalize(state) and not display_match:
            continue
        if not (name_match or display_match):
            continue

        osm_type = str(item.get("osm_type") or "")
        try:
            osm_id = int(item.get("osm_id"))
        except (TypeError, ValueError):
            continue

        category = str(item.get("category") or "")
        place_type = str(item.get("type") or "")
        extratags = item.get("extratags") or {}
        geojson = item.get("geojson")
        has_polygon = isinstance(geojson, dict) and geojson.get("type") in {
            "Polygon", "MultiPolygon"
        }
        administrative_boundary = (
            category == "boundary"
            and place_type == "administrative"
            and osm_type == "relation"
            and has_polygon
        )
        try:
            center = [float(item["lat"]), float(item["lon"])]
        except (KeyError, TypeError, ValueError):
            center = None

        candidates.append({
            "osm_type": osm_type,
            "osm_id": osm_id,
            "name": item.get("name") or name,
            "display_name": display_name,
            "category": category,
            "type": place_type,
            "admin_level": extratags.get("admin_level"),
            "place": extratags.get("place") or (place_type if category == "place" else None),
            "area_id": area_id_for(osm_type, osm_id) if administrative_boundary else None,
            "center": center,
            "boundingbox": item.get("boundingbox"),
            "geojson": geojson if has_polygon else None,
            "usable_for_discovery": administrative_boundary,
            "osm_url": f"https://www.openstreetmap.org/{osm_type}/{osm_id}",
            "address": address,
            "extratags": extratags,
            "importance": item.get("importance"),
        })

    candidates.sort(
        key=lambda item: (
            not item["usable_for_discovery"],
            item["osm_type"] != "relation",
            -(float(item["importance"]) if item["importance"] is not None else 0),
            item["osm_id"],
        )
    )
    return candidates


def save_result(name: str, uf: str, output: dict[str, Any]) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_file = OUTPUT_DIR / f"{slugify(name)}-{uf.lower()}.json"
    temporary_file = output_file.with_suffix(".json.tmp")
    temporary_file.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    json.loads(temporary_file.read_text(encoding="utf-8"))
    temporary_file.replace(output_file)
    return output_file


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
        # Uma consulta direta ao Nominatim evita depender de múltiplas
        # instâncias Overpass, que podem estar congestionadas.
        results = nominatim_search(name)
        time.sleep(1)  # Respeita o limite de uso do serviço público.
        candidates = build_candidates(name, results)

        usable = sum(1 for item in candidates if item["usable_for_discovery"])
        output = {
            "schema_version": "1.1",
            "generated_at": now_iso(),
            "requested_locality": name,
            "uf": uf,
            "search_status": "candidates_found" if candidates else "no_candidates",
            "source": "OpenStreetMap / Nominatim",
            "attribution": "© OpenStreetMap contributors",
            "license": "Open Database License (ODbL)",
            "candidate_count": len(candidates),
            "usable_boundary_count": usable,
            "review_required": True,
            "activation_allowed": False,
            "candidates": candidates,
            "message": (
                "Candidatos para conferência humana. A existência de um resultado "
                "não significa que seus limites representem a área comercial desejada. "
                "Nenhuma região foi aprovada ou ativada."
            ),
        }

        output_file = save_result(name, uf, output)
        print(f"Localidade: {name}/{uf}")
        print(f"Resultados compatíveis: {len(candidates)}")
        print(f"Limites administrativos candidatos: {usable}")
        print(f"Resultado: {output_file.relative_to(ROOT)}")
        print("Nenhuma região foi ativada. A aprovação humana continua obrigatória.")
        return 0

    except (OSError, ValueError, RuntimeError) as exc:
        print(f"Investigação geográfica interrompida: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
