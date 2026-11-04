# DESCOM — Estado atual e continuidade técnica

**Atualizado em:** 04/11/2026  
**Repositório:** `eddypfernandes/Descom`  
**Commit de referência:** `5b0bb4ecd28cf7fc4bf82cea2b0f32b66bdd2ea5`

Este documento registra o estado confirmado do repositório. Requisitos não são tratados como implementação.

## Preservação

- `docs/revisao/index.html`: painel geográfico/revisão já aprovado. **Não alterar sem autorização específica.**
- Dados existentes em `data/`: preservados; não limpar nem sobrescrever em uma reconstrução.
- Scripts Python e documentação existentes: aproveitar como base.
- `docs/revisao/operacao.html`: prévia visual anterior, preservada como referência.
- `docs/central/index.html`: nova central administrativa DESCOM, criada separadamente. Interface responsiva com navegação, indicadores, mapa, filtros e listagem alimentados pelos JSON públicos do repositório. Não substitui os painéis anteriores.

## O que existe e foi confirmado no GitHub

- `.github/workflows/descom.yml`: workflow manual `workflow_dispatch`, com ações separadas `validate`, `discover`, `triage` e `geography`; grava JSON no repositório via commit.
- `scripts/main.py`: coleta OSM/Overpass, mantém descobertas anteriores por identificador OSM, valida estrutura e grava `descobertas.json` atomicamente. Não publica nem importa.
- `scripts/triage.py`: classificação heurística, flags e decisões de revisão; saída `triagem.json`. Não confirma funcionamento nem identidade comercial.
- `scripts/geography.py`: pesquisa Nominatim e gera candidatos geográficos pendentes. Não aprova nem ativa automaticamente regiões.
- `config/regions.json`: Núcleo Bandeirante, Riacho Fundo I e Taguatinga habilitados.
- `data/taguatinga/descobertas.json` e `triagem.json`: base de Taguatinga existente (647 registros na coleta anteriormente confirmada). A nova central consulta os arquivos de descobertas e triagem por localidade.
- `docs/revisao/index.html`: página de revisão com mapa, filtros e marcações locais; a seleção atual de marcador filtra a lista e deve ser ajustada no futuro para preservar contexto.
- `/admin/adao/` e `/admin/bd/descom.accdb`: existem no ambiente local do usuário, mas não estão versionados neste repositório. Não foram auditados neste turno.
- Não existe endpoint ASP↔GitHub confirmado neste repositório.

## Lacunas reais

1. Cadastro de localidade no Access não atualiza ainda `config/regions.json` nem aciona investigação.
2. Aprovação geográfica no painel não está integrada à ativação técnica.
3. Descoberta e triagem são comandos separados no workflow.
4. Resultado das Actions não retorna ao Access automaticamente.
5. Painel ASP não comanda nem acompanha a execução GitHub.
6. “Buscar mais detalhes” por empresa e revisão persistente no servidor ainda não estão integrados.
7. Importação idempotente de aprovados para o Guia Comercial ainda não foi implementada.
8. A nova central ainda não dispara operações reais; os comandos permanecem desabilitados até a integração autenticada com ASP e GitHub Actions.

## Direção técnica consolidada

- A nova central em `docs/central/index.html` é a direção visual aprovada para o centro de comando. A implementação operacional final será servida pelo ambiente ASP; GitHub Pages é apenas prévia de interface.
- `descom.accdb` mantém localidades, solicitações, resultados e decisões operacionais.
- GitHub Actions executa tarefas Python; não acessa diretamente o arquivo Access do IIS.
- O usuário confirmou como aprovadas as 11 tabelas Access e a conexão `connAdao` baseada em ACE OLEDB 12.0. Não reabrir essa verificação nem criar tabelas duplicadas.
- Preferir um fluxo integrado de descoberta + triagem e uma integração central autenticada, com retorno idempotente ao servidor.
- Nenhum registro bruto pode ser importado/publicado sem aprovação humana.
- Não apagar dados históricos. Qualquer limpeza futura exige cópia/arquivo e confirmação de integridade.

## Próxima ação objetiva

Próxima etapa: integrar a central administrativa ao ambiente ASP e conectar, por uma integração autenticada única, o painel ao GitHub Actions e o retorno das execuções ao Access. A estrutura das 11 tabelas e a conexão foram consideradas aprovadas pelo usuário. Preservar os dados e os painéis anteriores.
