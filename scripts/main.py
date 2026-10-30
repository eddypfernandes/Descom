"""DESCOM: coleta pública, consolidação JSON e seleção para o carousel."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "nucleo-bandeirante" / "estabelecimentos.json"
CAROUSEL_FILE = ROOT / "carousel" / "empresas-carousel.json"
REGION = "Núcleo Bandeirante"
CITY = "Brasília"
UF = "DF"
SEARCH_ENDPOINT = "https://api.tavily.com/search"
ACTIVITY_GROUPS = {
    "Alimentação": "restaurantes lanchonetes cafeterias padarias bares",
    "Comércio": "mercados lojas vestuário variedades materiais de construção",
    "Saúde e bem-estar": "clínicas consultórios laboratórios farmácias academias",
    "Serviços profissionais": "contabilidade advocacia consultoria arquitetura",
    "Serviços pessoais": "salões barbearias estética assistência técnica",
    "Automotivo": "oficinas autopeças lava-jatos concessionárias",
    "Educação e cultura": "escolas cursos idiomas atividades culturais",
    "Hospedagem, lazer e eventos": "hotéis hospedagem lazer espaços eventos",
    "Serviços diversos": "prestadores de serviços comércio local",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def load_data(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": "1.0", "generated_at": None, "region": REGION, "uf": UF, "establishments": []}
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError(f"A raiz de {path.name} precisa ser um objeto JSON.")
    return data


def validate_data(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "1.0":
        errors.append("schema_version deve ser '1.0'.")
    if data.get("region") != REGION or data.get("uf") != UF:
        errors.append("A base contém região ou UF diferente do território configurado.")
    establishments = data.get("establishments")
    if not isinstance(establishments, list):
        return errors + ["establishments deve ser uma lista."]
    ids: set[str] = set()
    for i, item in enumerate(establishments):
        if not isinstance(item, dict):
            errors.append(f"establishments[{i}] deve ser um objeto.")
            continue
        rid = item.get("id")
        if not isinstance(rid, str) or not rid:
            errors.append(f"establishments[{i}].id ausente.")
        elif rid in ids:
            errors.append(f"ID duplicado: {rid}.")
        else:
            ids.add(rid)
        for field in ("name", "category", "address", "contacts", "sources", "dates", "validation"):
            if field not in item:
                errors.append(f"establishments[{i}] não contém '{field}'.")
    return errors


def tavily_search(query: str, api_key: str) -> list[dict[str, Any]]:
    body = json.dumps({
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "topic": "general",
        "max_results": 10,
        "include_answer": False,
    }).encode("utf-8")
    request = urllib.request.Request(
        SEARCH_ENDPOINT,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload.get("results", [])


def candidate_to_record(item: dict[str, Any], category: str, timestamp: str) -> dict[str, Any] | None:
    title = (item.get("title") or "").strip()
    url = (item.get("url") or "").strip()
    description = (item.get("content") or "").strip()
    if not title or not url:
        return None
    # A pesquisa é territorialmente restrita: só aceitar resultado cujo texto identifique a RA.
    searchable = f"{title} {description} {url}".casefold()
    if "núcleo bandeirante" not in searchable and "nucleo bandeirante" not in searchable:
        return None
    rid = "descom-" + hashlib.sha256(url.casefold().encode("utf-8")).hexdigest()[:16]
    return {
        "id": rid,
        "name": title,
        "category": category,
        "description": description or None,
        "address": {
            "street": None, "number": None, "complement": None,
            "neighborhood": None, "city": CITY, "state": UF, "postal_code": None
        },
        "contacts": {"phone": None, "whatsapp": None, "website": None, "email": None, "public_profile": url},
        "location": {"latitude": None, "longitude": None},
        "image": {"url": None, "source_url": None, "permission_status": "not_available"},
        "sources": [{"url": url, "type": "web_search_result", "checked_at": timestamp}],
        "dates": {"first_seen_at": timestamp, "last_checked_at": timestamp, "last_updated_at": timestamp},
        "validation": {"status": "pending", "confidence": "low", "notes": "Candidato localizado em pesquisa pública; dados ainda não verificados."},
        "data_origin": "descom",
        "merchant_claim": {"claimed": False, "verified": False, "declared_at": None},
    }



AGGREGATOR_HOSTS = (
    "tripadvisor.", "yelp.", "wikipedia.org", "instagram.com",
    "facebook.com", "consed.org.br", "cbm.df.gov.br",
    "centro-oeste-do-brasil-hoteis.com",
)
GENERIC_TITLE_TERMS = (
    "top 10", "os 10 melhores", "melhores restaurantes", "listas para",
    "oferta de cursos", "regiões administrativas", "lista de empresas",
    "empresas brigadas ativas", "resultados para",
)


def eligible_for_carousel(record: dict[str, Any]) -> bool:
    """Só libera estabelecimentos individuais com validação concluída."""
    name = str(record.get("name") or "").strip().casefold()
    validation = record.get("validation") or {}
    sources = record.get("sources") or []
    if validation.get("status") != "verified":
        return False
    if not name or any(term in name for term in GENERIC_TITLE_TERMS):
        return False
    if len(name.split()) < 2 or not sources:
        return False
    urls = [str(source.get("url") or "") for source in sources if isinstance(source, dict)]
    if not urls:
        return False
    for url in urls:
        host = (urlsplit(url).hostname or "").casefold()
        if not host or any(blocked in host for blocked in AGGREGATOR_HOSTS):
            continue
        if host.endswith(".gov.br") or host.endswith(".gov"):
            continue
        return True
    return False

def atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    json.loads(temporary.read_text(encoding="utf-8"))
    temporary.replace(path)


def run_search(api_key: str) -> tuple[int, int]:
    timestamp = now_iso()
    current = load_data(DATA_FILE)
    existing = current.get("establishments", [])
    if not isinstance(existing, list):
        raise ValueError("A lista establishments da base atual está inválida.")
    by_id = {item["id"]: item for item in existing if isinstance(item, dict) and item.get("id")}
    found = 0

    for category, terms in ACTIVITY_GROUPS.items():
        query = f"{terms} em {REGION}, {CITY}, {UF}, Brasil. Empresas e estabelecimentos localizados exclusivamente nesta região administrativa."
        print(f"Pesquisando: {category}")
        for result in tavily_search(query, api_key):
            record = candidate_to_record(result, category, timestamp)
            if not record:
                continue
            old = by_id.get(record["id"])
            if old:
                old["dates"]["last_checked_at"] = timestamp
                old["sources"] = old.get("sources", [])
                if not any(source.get("url") == record["sources"][0]["url"] for source in old["sources"]):
                    old["sources"].append(record["sources"][0])
            else:
                by_id[record["id"]] = record
                found += 1

    all_records = sorted(by_id.values(), key=lambda x: x.get("dates", {}).get("first_seen_at") or "", reverse=True)
    new_base = {
        "schema_version": "1.0",
        "generated_at": timestamp,
        "region": REGION,
        "uf": UF,
        "establishments": all_records,
    }
    errors = validate_data(new_base)
    if errors:
        raise ValueError("Base não foi gravada: " + "; ".join(errors))

    # A base preserva todos os candidatos; o carousel recebe apenas empresas verificadas.
    carousel_records = [record for record in all_records if eligible_for_carousel(record)][:20]
    carousel = {
        "schema_version": "1.0",
        "generated_at": timestamp,
        "region": REGION,
        "uf": UF,
        "minimum_cards": 10,
        "total_cards": len(carousel_records),
        "cards": carousel_records,
    }
    atomic_write(DATA_FILE, new_base)
    atomic_write(CAROUSEL_FILE, carousel)
    print(f"Novos candidatos: {found}")
    print(f"Total na base: {len(all_records)}")
    print(f"Cards no carousel: {len(carousel_records)}")
    if len(carousel_records) < 10:
        print("AVISO: menos de 10 empresas verificadas; o carousel deve permanecer em estado de espera.")
    return len(all_records), len(carousel_records)


def main() -> int:
    parser = argparse.ArgumentParser(description="Coleta e organiza empresas do DESCOM.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate", action="store_true", help="Valida a base JSON atual.")
    group.add_argument("--search", action="store_true", help="Pesquisa empresas e atualiza os JSONs.")
    args = parser.parse_args()

    try:
        if args.validate:
            errors = validate_data(load_data(DATA_FILE))
            if errors:
                print("\n".join(errors), file=sys.stderr)
                return 1
            print("Base JSON válida.")
            return 0

        api_key = os.environ.get("TAVILY_API_KEY", "").strip()
        if not api_key:
            print("Secret TAVILY_API_KEY não configurado no GitHub.", file=sys.stderr)
            return 1
        run_search(api_key)
        return 0
    except (OSError, ValueError, json.JSONDecodeError, urllib.error.URLError) as exc:
        print(f"DESCOM interrompido: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
