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
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "DESCOM/0.1 (+https://github.com/eddypfernandes/Descom)",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    candidates = []
    for item in payload.get("results", []):
        url = item.get("url")
        title = item.get("title")
        if not url or not title:
            continue
        candidates.append({
            "title": title,
            "url": url,
            "description": item.get("content"),
            "source": "Tavily Search API",
        })
    return candidates
