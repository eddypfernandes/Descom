"""DESCOM: descoberta de estabelecimentos em dados abertos do OpenStreetMap.

O coletor não acessa nem raspa o Google Maps. OSM é fonte de descoberta;
Google Maps pode ser usado manualmente para conferência visual.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import unicodedata
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REGION = "Núcleo Bandeirante"
CITY = "Brasília"
UF = "DF"
DATA_FILE = ROOT / "data" / "nucleo-bandeirante" / "estabelecimentos.json"
DISCOVERY_FILE = ROOT / "data" / "nucleo-bandeirante" / "descobertas.json"
OVERPASS_ENDPOINT = "https://overpass-api.de/api/interpreter"
USER_AGENT = "DESCOM/1.0 (GUIA COMERCIAL; public business discovery)"
OVERPASS_QUERY = r"""
[out:json][timeout:90];
area["name"="Núcleo Bandeirante"]["boundary"="administrative"]->.searchArea;
(
  nwr(area.searchArea)["name"]["shop"];
  nwr(area.searchArea)["name"]["amenity"];
  nwr(area.searchArea)["name"]["office"];
  nwr(area.searchArea)["name"]["craft"];
  nwr(area.searchArea)["name"]["healthcare"];
  nwr(area.searchArea)["name"]["tourism"];
  nwr(area.searchArea)["name"]["leisure"];
);
out center tags;
"""

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.casefold())
    value = "".join(char for char in value if not unicodedata.combining(char))
    return re.sub(r"[^a-z0-9]+", " ", value).strip()

def load_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"A raiz de {path.name} precisa ser um objeto JSON.")
    return data

def is_business(tags: dict[str, str]) -> bool:
    if tags.get("shop") or tags.get("office") or tags.get("craft") or tags.get("healthcare"):
        return True
    if tags.get("tourism") in {"hotel", "guest_house", "hostel", "motel", "attraction"}:
        return True
    if tags.get("leisure") in {"fitness_centre", "sports_centre", "beauty", "escape_game"}:
        return True
    amenity = tags.get("amenity", "")
    return amenity in {
        "restaurant", "cafe", "bar", "pub", "fast_food", "food_court",
        "ice_cream", "pharmacy", "clinic", "doctors", "dentist",
        "hospital", "veterinary", "bank", "bureau_de_change",
        "car_rental", "car_wash", "fuel", "school", "language_school",
        "college", "university", "cinema", "theatre", "marketplace",
        "coworking_space", "social_facility"
    }

def classify(tags: dict[str, str]) -> str:
    shop = tags.get("shop", "")
    amenity = tags.get("amenity", "")
    office = tags.get("office", "")
    craft = tags.get("craft", "")
    healthcare = tags.get("healthcare", "")
    tourism = tags.get("tourism", "")
    leisure = tags.get("leisure", "")

    if amenity in {"restaurant", "cafe", "bar", "pub", "fast_food", "food_court", "ice_cream"} or shop in {"bakery", "butcher", "confectionery", "deli", "greengrocer"}:
        return "Alimentação"
    if healthcare or amenity in {"pharmacy", "clinic", "doctors", "dentist", "hospital", "veterinary"}:
        return "Saúde e bem-estar"
    if tourism in {"hotel", "guest_house", "hostel", "motel"}:
        return "Hospedagem, lazer e eventos"
    if amenity in {"school", "language_school", "college", "university"}:
        return "Educação e cultura"
    if amenity in {"car_rental", "car_wash", "fuel"} or shop in {"car", "car_repair", "car_parts", "tyres"} or craft in {"carpenter", "painter", "plumber"}:
        return "Automotivo" if (amenity in {"car_rental", "car_wash", "fuel"} or shop in {"car", "car_repair", "car_parts", "tyres"}) else "Serviços diversos"
    if office in {"accountant", "lawyer", "architect", "company", "financial", "insurance", "estate_agent", "consulting"}:
        return "Serviços profissionais"
    if leisure in {"fitness_centre", "sports_centre", "beauty"} or shop in {"hairdresser", "beauty", "massage"}:
        return "Serviços pessoais"
    if tourism or leisure:
        return "Hospedagem, lazer e eventos"
    if office:
        return "Serviços profissionais"
    if craft:
        return "Serviços diversos"
    if shop:
        return "Comércio"
    return "Serviços diversos"

def request_overpass() -> list[dict[str, Any]]:
    request = urllib.request.Request(
        OVERPASS_ENDPOINT,
        data=OVERPASS_QUERY.encode("utf-8"),
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        if exc.code in {429, 502, 503, 504}:
            raise RuntimeError("O serviço público do OpenStreetMap está temporariamente ocupado. Tente novamente mais tarde.") from exc
        raise RuntimeError(f"OpenStreetMap respondeu HTTP {exc.code}.") from exc
    elements = payload.get("elements")
    if not isinstance(elements, list):
        raise RuntimeError("Resposta do OpenStreetMap sem lista de elementos.")
    if not elements:
        raise RuntimeError("Nenhum resultado encontrado. A área administrativa pode não estar mapeada com esse nome no OpenStreetMap.")
    return elements

def element_coordinates(element: dict[str, Any]) -> tuple[float | None, float | None, str]:
    if isinstance(element.get("lat"), (int, float)) and isinstance(element.get("lon"), (int, float)):
        return float(element["lat"]), float(element["lon"]), "node"
    center = element.get("center") or {}
    if isinstance(center.get("lat"), (int, float)) and isinstance(center.get("lon"), (int, float)):
        return float(center["lat"]), float(center["lon"]), "way_or_relation_center"
    return None, None, "unavailable"

def build_record(element: dict[str, Any], timestamp: str) -> dict[str, Any] | None:
    tags = element.get("tags") or {}
    name = str(tags.get("name") or "").strip()
    if not name or not is_business(tags):
        return None

    osm_type = str(element.get("type") or "")
    osm_id = str(element.get("id") or "")
    if osm_type not in {"node", "way", "relation"} or not osm_id:
        return None

    latitude, longitude, coordinate_method = element_coordinates(element)
    street = tags.get("addr:street")
    number = tags.get("addr:housenumber")
    neighborhood = tags.get("addr:suburb") or tags.get("addr:neighbourhood") or REGION
    has_address = bool(street and number)
    has_coordinates = latitude is not None and longitude is not None
    status = "partial" if has_address and has_coordinates else "pending"
    confidence = "medium" if has_address and has_coordinates and coordinate_method == "node" else "low"
    external_id = f"{osm_type}/{osm_id}"
    record_id = "descom-osm-" + hashlib.sha256(external_id.encode("utf-8")).hexdigest()[:16]

    contact = {
        "phone": tags.get("phone") or tags.get("contact:phone"),
        "whatsapp": tags.get("contact:whatsapp"),
        "website": tags.get("website") or tags.get("contact:website"),
        "email": tags.get("email") or tags.get("contact:email"),
        "public_profile": f"https://www.openstreetmap.org/{osm_type}/{osm_id}",
    }
    address = {
        "street": street,
        "number": number,
        "complement": tags.get("addr:unit") or tags.get("addr:door"),
        "neighborhood": neighborhood,
        "city": tags.get("addr:city") or CITY,
        "state": UF,
        "postal_code": tags.get("addr:postcode"),
    }
    return {
        "id": record_id,
        "external_id": external_id,
        "name": name,
        "category": classify(tags),
        "description": tags.get("description"),
        "address": address,
        "contacts": contact,
        "location": {
            "latitude": latitude,
            "longitude": longitude,
            "source": "OpenStreetMap",
            "coordinate_method": coordinate_method,
        },
        "image": {
            "url": None,
            "source_url": None,
            "permission_status": "not_available",
        },
        "sources": [{
            "url": f"https://www.openstreetmap.org/{osm_type}/{osm_id}",
            "type": "openstreetmap",
            "checked_at": timestamp,
        }],
        "dates": {
            "first_seen_at": timestamp,
            "last_checked_at": timestamp,
            "last_updated_at": timestamp,
        },
        "validation": {
            "status": status,
            "confidence": confidence,
            "notes": "Descoberto no OpenStreetMap. Conferência de identidade, endereço e funcionamento ainda necessária.",
        },
        "data_origin": "descom_osm",
        "merchant_claim": {
            "claimed": False,
            "verified": False,
            "declared_at": None,
        },
        "osm_tags": tags,
    }

def validate_data(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "1.0":
        errors.append("schema_version deve ser '1.0'.")
    if data.get("region") != REGION or data.get("uf") != UF:
        errors.append("Região ou UF incompatível com a configuração.")
    records = data.get("establishments")
    if not isinstance(records, list):
        return errors + ["establishments deve ser uma lista."]
    ids: set[str] = set()
    external_ids: set[str] = set()
    for index, item in enumerate(records):
        if not isinstance(item, dict):
            errors.append(f"establishments[{index}] não é um objeto.")
            continue
        rid = item.get("id")
        ext = item.get("external_id")
        if not rid or rid in ids:
            errors.append(f"ID ausente ou duplicado no registro {index}.")
        ids.add(rid)
        if not ext or ext in external_ids:
            errors.append(f"external_id ausente ou duplicado no registro {index}.")
        external_ids.add(ext)
        for field in ("name", "category", "address", "contacts", "location", "sources", "dates", "validation"):
            if field not in item:
                errors.append(f"Registro {index} sem campo '{field}'.")
        loc = item.get("location") or {}
        lat, lon = loc.get("latitude"), loc.get("longitude")
        if (lat is None) != (lon is None):
            errors.append(f"Coordenadas incompletas no registro {index}.")
        if lat is not None and not (-90 <= lat <= 90):
            errors.append(f"Latitude fora do intervalo no registro {index}.")
        if lon is not None and not (-180 <= lon <= 180):
            errors.append(f"Longitude fora do intervalo no registro {index}.")
    return errors

def atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    json.loads(temporary.read_text(encoding="utf-8"))
    temporary.replace(path)

def discover() -> tuple[int, int]:
    timestamp = now_iso()
    previous = load_json(DISCOVERY_FILE, {
        "schema_version": "1.0", "generated_at": None,
        "region": REGION, "uf": UF, "establishments": []
    })
    previous_records = previous.get("establishments", [])
    by_external_id = {
        item["external_id"]: item
        for item in previous_records
        if isinstance(item, dict) and item.get("external_id")
    }

    # A base anterior é usada apenas para sinalizar possíveis coincidências.
    legacy = load_json(DATA_FILE, {"establishments": []})
    legacy_names = {
        normalize(str(item.get("name") or ""))
        for item in legacy.get("establishments", [])
        if isinstance(item, dict) and item.get("name")
    }

    elements = request_overpass()
    new_count = 0
    possible_matches = 0
    for element in elements:
        record = build_record(element, timestamp)
        if not record:
            continue
        old = by_external_id.get(record["external_id"])
        if old:
            old["dates"]["last_checked_at"] = timestamp
            # Preserva a primeira descoberta e não apaga dados enriquecidos anteriormente.
            for field in ("name", "category", "address", "contacts", "location", "osm_tags"):
                if not old.get(field) and record.get(field):
                    old[field] = record[field]
            old["sources"] = old.get("sources", [])
            source_url = record["sources"][0]["url"]
            if not any(source.get("url") == source_url for source in old["sources"] if isinstance(source, dict)):
                old["sources"].append(record["sources"][0])
        else:
            normalized_name = normalize(record["name"])
            record["duplicate_check"] = {
                "status": "possible_match" if normalized_name in legacy_names else "not_found_by_exact_name",
                "review_required": normalized_name in legacy_names,
            }
            if normalized_name in legacy_names:
                possible_matches += 1
            by_external_id[record["external_id"]] = record
            new_count += 1

    records = sorted(
        by_external_id.values(),
        key=lambda item: item.get("dates", {}).get("first_seen_at", ""),
        reverse=True,
    )
    output = {
        "schema_version": "1.0",
        "generated_at": timestamp,
        "region": REGION,
        "uf": UF,
        "source": "OpenStreetMap",
        "attribution": "© OpenStreetMap contributors",
        "license": "Open Database License (ODbL)",
        "review_required_before_publication": True,
        "total_records": len(records),
        "new_records_this_run": new_count,
        "possible_matches_with_legacy_base": possible_matches,
        "establishments": records,
    }
    errors = validate_data(output)
    if errors:
        raise ValueError("Descobertas não foram gravadas: " + "; ".join(errors))
    atomic_write(DISCOVERY_FILE, output)
    print(f"Elementos recebidos do OpenStreetMap: {len(elements)}")
    print(f"Estabelecimentos identificados: {len(records)}")
    print(f"Novos nesta execução: {new_count}")
    print(f"Possíveis coincidências com a base anterior: {possible_matches}")
    print(f"Arquivo gerado: {DISCOVERY_FILE.relative_to(ROOT)}")
    print("Todos os registros permanecem pendentes de conferência; nada é publicado automaticamente.")
    return len(records), new_count

def main() -> int:
    parser = argparse.ArgumentParser(description="DESCOM — descoberta própria de estabelecimentos.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate", action="store_true", help="Valida o arquivo de descobertas.")
    group.add_argument("--discover", action="store_true", help="Descobre estabelecimentos em dados abertos.")
    args = parser.parse_args()
    try:
        if args.validate:
            data = load_json(DISCOVERY_FILE, {
                "schema_version": "1.0", "region": REGION, "uf": UF, "establishments": []
            })
            errors = validate_data(data)
            if errors:
                print("\n".join(errors), file=sys.stderr)
                return 1
            print("Arquivo de descobertas válido.")
            return 0
        discover()
        return 0
    except (OSError, ValueError, json.JSONDecodeError, urllib.error.URLError, RuntimeError) as exc:
        print(f"DESCOM interrompido: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
