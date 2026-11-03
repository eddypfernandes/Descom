# Scripts do DESCOM

Os scripts de descoberta e triagem recebem a chave da Região Administrativa cadastrada em `config/regions.json`.

## Execução

Descoberta:

```bash
python scripts/main.py --discover --region nucleo-bandeirante
python scripts/main.py --discover --region riacho-fundo-i
```

Triagem:

```bash
python scripts/triage.py --region nucleo-bandeirante
python scripts/triage.py --region riacho-fundo-i
```

Validação:

```bash
python scripts/main.py --validate --region nucleo-bandeirante
python scripts/main.py --validate --region riacho-fundo-i
```

A configuração geográfica, os identificadores OSM, os centros iniciais do mapa e o estado de ativação ficam centralizados em `config/regions.json`. Cada região mantém seus próprios arquivos em `data/<chave-da-regiao>/`.

A descoberta usa dados abertos do OpenStreetMap. A triagem é heurística e não confirma existência, funcionamento ou titularidade. Nenhum registro é publicado ou importado automaticamente.
