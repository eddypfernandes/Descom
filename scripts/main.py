"""Rotinas iniciais do DESCOM: validação e descoberta web de candidatos."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "nucleo-bandeirante" / "estabelecimentos.json"
DISCOVERY_FILE = ROOT / "discovery-results.json"
REGION = "Núcleo Bandeirante"
SEARCH_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"
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


def load_data(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)
    if not isinstance(data, dict):
        raise ValueError("A raiz do JSON precisa ser um objeto.")
    return data


def validate_data(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema_version") != "1.0":
        errors.append("schema_version deve ser '1.0'.")
    if data.get("region") != REGION:
        errors.append(f"region deve ser '{REGION}'.")
    if data.get("uf") != "DF":
        errors.append("uf deve ser 'DF'.")
    establishments = data.get("establishments")
    if not isinstance(establishments, list):
        errors.append("establishments deve ser uma lista.")
        return errors
    seen_ids: set[str] = set()
    for index, item in enumerate(establishments):
        label = f"establishments[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} deve ser um objeto.")
            continue
        record_id = item.get("id")
        if not isinstance(record_id, str) or not record_id.strip():
            errors.append(f"{label}.id deve ser um texto não vazio.")
        elif record_id in seen_ids:
            errors.append(f"ID duplicado: {record_id}.")
        else:
            seen_ids.add(record_id)
        for field in ("name", "category", "address", "sources", "dates", "validation"):
            if field not in item:
                errors.append(f"{label} não contém o campo obrigatório '{field}'.")
    return errors


def brave_search(query: str, api_key: str) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({
        "q": query,
        "country": "BR",
        "search_lang": "pt",
        "count": 10,
    })
    request = urllib.request.Request(
        f"{SEARCH_ENDPOINT}?{params}",
        headers={
            "Accept": "application/json",
            "X-Subscription-Token": api_key,
            "User-Agent": "DESCOM/0.1 (+https://github.com/eddypfernandes/Descom)",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    results = payload.get("web", {}).get("results", [])
    candidates = []
    for item in results:
        url = item.get("url")
        title = item.get("title")
        if not url or not title:
            continue
        candidates.append({
            "title": title,
            "url": url,
            "description": item.get("description"),
            "source": "Brave Search API",
        })
    return candidates


def discover() -> int:
    api_key = os.environ.get("BRAVE_API_KEY", "").strip()
    if not api_key:
        print("ERRO: configure BRAVE_API_KEY nos Secrets do GitHub Actions.")
        return 2

    collected: list[dict[str, Any]] = []
    for category, terms in ACTIVITY_GROUPS.items():
        query = f"{terms} no Núcleo Bandeirante Brasília DF"
        try:
            results = brave_search(query, api_key)
            for result in results:
                result["category_group"] = category
                result["query"] = query
                collected.append(result)
            print(f"{category}: {len(results)} resultados")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            print(f"AVISO: falha na pesquisa de '{category}': {exc}")
        except Exception as exc:
            print(f"AVISO: resposta inesperada em '{category}': {exc}")

    # Deduplica somente URLs idênticas; não presume que resultados sejam empresas distintas.
    unique: dict[str, dict[str, Any]] = {}
    for item in collected:
        unique.setdefault(item["url"].rstrip("/").lower(), item)

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "region": REGION,
        "uf": "DF",
        "provider": "Brave Search API",
        "review_required": True,
        "note": "Resultados de busca são candidatos. Não representam cadastros verificados.",
        "candidate_count": len(unique),
        "candidates": list(unique.values()),
    }
    DISCOVERY_FILE.write_text(
        json.dumps(output, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Descoberta concluída: {len(unique)} candidatos únicos.")
    print(f"Arquivo de revisão: {DISCOVERY_FILE.name}")
    print("A base oficial de estabelecimentos não foi alterada.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Rotinas iniciais do DESCOM")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--validate", action="store_true", help="valida a base oficial")
    mode.add_argument("--search", action="store_true", help="pesquisa candidatos na web")
    args = parser.parse_args()

    if args.search:
        return discover()

    try:
        data = load_data(DATA_FILE)
        errors = validate_data(data)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERRO: não foi possível validar a base: {exc}")
        return 1
    if errors:
        print("Validação reprovada:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Validação concluída com sucesso.")
    print(f"Região: {data['region']}/{data['uf']}")
    print(f"Estabelecimentos na base: {len(data['establishments'])}")
    print("Nenhum arquivo foi alterado.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
