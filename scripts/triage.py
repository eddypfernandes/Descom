"""Triagem heurística das descobertas OSM; não valida nem publica negócios."""
from __future__ import annotations
import json, re, unicodedata
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data" / "nucleo-bandeirante"
DISCOVERY = BASE / "descobertas.json"
LEGACY = BASE / "estabelecimentos.json"
OUTPUT = BASE / "triagem.json"

def norm(value):
    value = unicodedata.normalize("NFKD", str(value or "").casefold())
    value = "".join(c for c in value if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", value).strip()

def read(path):
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not isinstance(data.get("establishments"), list):
        raise ValueError(f"Estrutura inválida: {path.name}")
    return data

def classify(item, duplicate_names, legacy_names):
    tags = item.get("osm_tags") or {}
    name = str(item.get("name") or "").strip()
    key = norm(name)
    reasons = []
    flags = []
    category = "candidato_comercial"
    decision = "revisao_manual"
    confidence = "media"

    if tags.get("government") or tags.get("office") == "government":
        category = "orgao_publico"
        decision = "fora_da_vitrine_comercial"
        confidence = "alta"
        reasons.append("Marcado como órgão ou administração pública no OSM.")
    elif tags.get("amenity") == "place_of_worship":
        category = "instituicao_religiosa"
        decision = "fora_da_vitrine_comercial"
        confidence = "alta"
        reasons.append("Marcado como local de culto no OSM.")
    elif tags.get("amenity") in {"school", "language_school", "college", "university"}:
        category = "instituicao_educacional"
        decision = "revisao_de_escopo"
        confidence = "media"
        reasons.append("Instituição educacional; confirmar se entra na proposta da vitrine comercial.")
    elif tags.get("note") and any(x in norm(tags.get("note")) for x in ("desativado", "fechado", "closed")):
        category = "possivelmente_inativo"
        decision = "reter_ate_confirmacao"
        confidence = "media"
        reasons.append("A própria tag do OSM indica possível desativação.")
    elif ";" in name or len(name) > 90 or any(x in key for x in ("lista para o site", "regioes administrativas", "oferta de cursos")):
        category = "registro_suspeito"
        decision = "reter_ate_confirmacao"
        confidence = "alta"
        reasons.append("Nome parece concatenado, título de conteúdo ou texto que não identifica um estabelecimento.")
    elif tags.get("amenity") == "marketplace":
        category = "mercado_ou_feira"
        decision = "revisao_de_escopo"
        confidence = "media"
        reasons.append("Mercado/feira pode ser local coletivo, não uma empresa individual.")
    elif tags.get("amenity") == "building" and not (tags.get("shop") or tags.get("office") or tags.get("craft")):
        category = "local_sem_atividade_comercial_clara"
        decision = "reter_ate_confirmacao"
        confidence = "baixa"
        reasons.append("Tag não confirma atividade comercial.")
    else:
        reasons.append("Tags comerciais ou de serviço no OSM; identidade e funcionamento ainda não foram verificados.")

    if key in duplicate_names:
        flags.append("nome_repetido_nas_descobertas")
        reasons.append("Há outro registro com o mesmo nome normalizado; verificar se são unidades distintas ou duplicidade.")
    if key and key in legacy_names:
        flags.append("possivel_coincidencia_base_historica")
        reasons.append("Nome igual encontrado na base histórica; confirmar se é a mesma unidade.")
    if not item.get("address", {}).get("street"):
        flags.append("sem_logradouro")
    if not item.get("address", {}).get("number"):
        flags.append("sem_numero")
    contacts = item.get("contacts") or {}
    if not contacts.get("phone"):
        flags.append("sem_telefone")
    if not contacts.get("website"):
        flags.append("sem_site")
    if item.get("location", {}).get("coordinate_method") == "way_or_relation_center":
        flags.append("coordenada_de_centro_aproximado")
    location = item.get("location") or {}
    if location.get("latitude") is None or location.get("longitude") is None:
        flags.append("sem_coordenadas")
    if not item.get("location", {}).get("latitude") or not item.get("location", {}).get("longitude"):
        flags.append("sem_coordenadas")

    if flags and decision == "revisao_manual":
        confidence = "baixa"
    if "possivel_coincidencia_base_historica" in flags:
        decision = "revisar_possivel_duplicidade"

    return {
        "id": item.get("id"),
        "external_id": item.get("external_id"),
        "name": name,
        "source_category": item.get("category"),
        "triage_category": category,
        "decision": decision,
        "confidence": confidence,
        "reasons": reasons,
        "flags": flags,
        "address": item.get("address"),
        "contacts": contacts,
        "location": item.get("location"),
        "source_url": ((item.get("sources") or [{}])[0]).get("url"),
        "osm_tags": tags,
        "publication_allowed": False
    }

def main():
    discoveries = read(DISCOVERY)
    legacy = read(LEGACY) if LEGACY.exists() else {"establishments": []}
    items = discoveries["establishments"]
    counts = defaultdict(int)
    names = defaultdict(int)
    for item in items:
        names[norm(item.get("name"))] += 1
    duplicate_names = {k for k, v in names.items() if k and v > 1}
    legacy_names = {norm(x.get("name")) for x in legacy["establishments"] if x.get("name")}
    records = []
    for item in items:
        record = classify(item, duplicate_names, legacy_names)
        records.append(record)
        counts[record["decision"]] += 1
    records.sort(key=lambda x: (x["decision"], norm(x["name"])))
    output = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "region": discoveries.get("region"),
        "uf": discoveries.get("uf"),
        "source": "OpenStreetMap",
        "attribution": "© OpenStreetMap contributors",
        "license": "Open Database License (ODbL)",
        "method": "Triagem heurística por tags, nome, campos disponíveis e comparação literal com a base histórica.",
        "limitations": [
            "A triagem não confirma existência, funcionamento, endereço ou titularidade.",
            "Nome igual não prova duplicidade; unidades diferentes podem compartilhar nome.",
            "Nome diferente não prova que os registros sejam empresas distintas.",
            "Coordenadas de way/relation podem representar centro aproximado.",
            "Nenhum registro é publicado ou importado automaticamente."
        ],
        "source_file": "descobertas.json",
        "total_records": len(records),
        "decision_counts": dict(counts),
        "records": records
    }
    OUTPUT.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Triagem gerada: {len(records)} registros")
    for key, value in sorted(counts.items()):
        print(f"{key}: {value}")

if __name__ == "__main__":
    main()
