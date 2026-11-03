# DESCOM — Desbravador Comercial

Agente próprio de descoberta, organização e validação de informações públicas sobre estabelecimentos comerciais.

## Objetivo

Construir uma base organizada para alimentar o módulo comercial do GUIA COMERCIAL, começando pelo Núcleo Bandeirante (DF) e avançando gradualmente para outras regiões administrativas.

## Operação atual

- Descoberta automatizada de estabelecimentos mapeados no OpenStreetMap, por região administrativa e categorias comerciais.
- Captura de nome, categoria, endereço, contatos públicos e coordenadas quando disponíveis na fonte.
- Identificador estável baseado no identificador do elemento no OpenStreetMap.
- Comparação inicial com a base histórica para sinalizar possíveis coincidências.
- Registro de fonte, data de descoberta e nível de validação.
- Geração de data/nucleo-bandeirante/descobertas.json.

O coletor não usa Gemini, Tavily, Google Places API ou chave paga. A consulta ao Overpass é um serviço público de leitura do OpenStreetMap, sem chave de API; está sujeita a limites de disponibilidade e uso.

## Limitações importantes

- A cobertura do OpenStreetMap varia conforme a região e o trabalho de mapeamento comunitário. A ausência de um estabelecimento no resultado não significa que ele não exista.
- A descoberta no OSM não comprova que o negócio seja novo ou recém-inaugurado; significa que é novo para a base de descobertas do DESCOM.
- Coordenadas de pontos (nodes) e centros de áreas (ways/relations) são identificadas separadamente. Centros de áreas podem ser aproximados.
- Todos os registros começam pendentes ou parciais e exigem conferência antes da publicação.
- O Google Maps pode ser consultado manualmente como referência visual. O DESCOM não automatiza a extração do Google Maps nem copia seus dados.

## Licença e atribuição

Os dados derivados do OpenStreetMap são disponibilizados sob a Open Database License (ODbL). A atribuição © OpenStreetMap contributors e a referência à ODbL devem ser mantidas. Consulte https://www.openstreetmap.org/copyright.

## Estrutura

- docs/: decisões e documentação.
- data/nucleo-bandeirante/estabelecimentos.json: base histórica anterior, preservada.
- data/nucleo-bandeirante/descobertas.json: novas descobertas do coletor OSM.
- carousel/: dados destinados ao carrossel, não alimentados automaticamente por descobertas pendentes.
- scripts/main.py: coleta e validação.
- .github/workflows/: automações do GitHub Actions.

## Execução

- python scripts/main.py --discover: consulta o OpenStreetMap e atualiza as descobertas.
- python scripts/main.py --validate: valida o arquivo de descobertas.

A rotina inicial é manual pelo GitHub Actions. Agendamento automático só será ativado depois da avaliação dos primeiros resultados.
