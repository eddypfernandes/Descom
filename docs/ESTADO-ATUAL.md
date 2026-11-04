# DESCOM — Estado atual e continuidade técnica

**Atualizado em:** 04/11/2026  
**Repositório:** `eddypfernandes/Descom`  
**Commit desta atualização:** `01561c146e387dfb877f6360e989cbde1f7ac89a`

Este documento registra o estado confirmado do repositório. Requisitos não são tratados como implementação.

## Preservação

- `docs/revisao/index.html`: painel geográfico/revisão já aprovado. **Não alterar sem autorização específica.**
- Dados existentes em `data/`: preservados; não limpar nem sobrescrever em uma reconstrução.
- Scripts Python e documentação existentes: aproveitar como base.
- `docs/revisao/operacao.html`: prévia visual independente, criada para validar a futura central de comando. Não substitui o painel aprovado e não se conecta ao Access nem dispara Actions.

## O que existe e foi confirmado no GitHub

- `.github/workflows/descom.yml`: workflow manual `workflow_dispatch`, com ações separadas `validate`, `discover`, `triage` e `geography`; grava JSON no repositório via commit.
- `scripts/main.py`: coleta OSM/Overpass, mantém descobertas anteriores por identificador OSM, valida estrutura e grava `descobertas.json` atomicamente. Não publica nem importa.
- `scripts/triage.py`: classificação heurística, flags e decisões de revisão; saída `triagem.json`. Não confirma funcionamento nem identidade comercial.
- `scripts/geography.py`: pesquisa Nominatim e gera candidatos geográficos pendentes. Não aprova nem ativa automaticamente regiões.
- `config/regions.json`: Núcleo Bandeirante, Riacho Fundo I e Taguatinga habilitados.
- `data/taguatinga/descobertas.json` e `triagem.json`: base de Taguatinga existente (647 registros na coleta anteriormente confirmada).
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
8. Prévia `operacao.html` é visual/demonstrativa; botão de descoberta não executa operação real.

## Direção técnica consolidada

- Painel ASP é o centro de comando e revisão humana.
- `descom.accdb` mantém localidades, solicitações, resultados e decisões operacionais.
- GitHub Actions executa tarefas Python; não acessa diretamente o arquivo Access do IIS.
- Integração deverá ser desenhada após auditoria dos ASPs e das 11 tabelas Access existentes. Não criar endpoint ou tabelas duplicadas antes dessa conferência.
- Preferir um fluxo integrado de descoberta + triagem e uma integração central autenticada, com retorno idempotente ao servidor.
- Nenhum registro bruto pode ser importado/publicado sem aprovação humana.
- Não apagar dados históricos. Qualquer limpeza futura exige cópia/arquivo e confirmação de integridade.

## Próxima ação objetiva

Auditar em conjunto, sem pedir testes repetitivos:
- ASPs usados por `/admin/adao/` e conexão Access;
- nomes/campos/relacionamentos das tabelas de `descom.accdb`;
- configuração atual do IIS/hosting necessária para chamadas HTTPS.

Depois disso, definir e implementar a integração única e testar no ambiente de desenvolvimento. A página `operacao.html` serve como referência visual; o painel ASP real será integrado sem substituir o layout aprovado.
