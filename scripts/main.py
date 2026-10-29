"""Ponto de entrada inicial do DESCOM.

Nesta etapa, o programa apenas valida a base consolidada.
A coleta será adicionada depois da definição e aprovação das fontes.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "nucleo-bandeirante" / "estabelecimentos.json"


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
    if data.get("region") != "Núcleo Bandeirante":
        errors.append("region deve ser 'Núcleo Bandeirante'.")
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Rotina inicial do DESCOM")
    parser.add_argument(
        "--validate",
        action="store_true",
        help="valida a base JSON sem modificá-la",
    )
    args = parser.parse_args()

    if not args.validate:
        parser.error("Nesta versão, utilize --validate. A coleta ainda não foi ativada.")

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

    total = len(data["establishments"])
    print("Validação concluída com sucesso.")
    print(f"Região: {data['region']}/{data['uf']}")
    print(f"Estabelecimentos na base: {total}")
    print("Nenhum arquivo foi alterado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
