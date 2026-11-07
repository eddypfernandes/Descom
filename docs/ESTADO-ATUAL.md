# DESCOM — Estado atual e continuidade técnica

**Atualizado em:** 04/11/2026 — revisão após criação da nova central  
**Repositório:** `eddypfernandes/Descom`  
**Último commit de referência antes desta atualização:** `b8474deb72fc6da85713bab1f4643ab953b93c52`

Este documento registra o estado confirmado do repositório. Requisitos não são tratados como implementação.

## Preservação

- `docs/revisao/index.html`: painel geográfico/revisão já aprovado. **Não alterar sem autorização específica.**
- Dados existentes em `data/`: preservados; não limpar nem sobrescrever em uma reconstrução.
- Scripts Python e documentação existentes: aproveitar como base.
- `docs/revisao/operacao.html`: prévia visual anterior, preservada como referência.
- `docs/central/index.html`: nova central administrativa DESCOM, criada separadamente. Interface responsiva com navegação, indicadores, mapa, filtros e listagem alimentados pelos JSON públicos do repositório. Não substitui os painéis anteriores.
- Banco Access: usuário confirmou como aprovadas as 11 tabelas e os relacionamentos apresentados.
- Conexão ASP: usuário confirmou como aprovada a conexão `connAdao` com ACE OLEDB 12.0 e caminho `/bd/descom.accdb`.
- `.github/workflows/modulo-pages.yml`: publicação ajustada para incluir `docs/central/` em `site/central/`, preservando o módulo comercial já publicado. O endereço previsto é `/Descom/central/`; a conclusão da publicação precisa ser confirmada no GitHub Pages.

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


## Registro de continuidade — 07/11/2026 (importação Taguatinga e diagnóstico do mapa)

### Resultado confirmado da descoberta e importação

- Localidade: Taguatinga/DF.
- Execução GitHub: `327c619084c441afa619a66f4fbbb585`.
- Identificador operacional da execução: `EXEC_ID = 26`.
- Arquivo de resultados: `data/jobs/327c619084c441afa619a66f4fbbb585.json`.
- O arquivo contém **633 estabelecimentos**. A contagem inicial de 139 mencionada durante o diagnóstico estava incorreta e fica substituída por esta contagem confirmada.
- Importação concluída em **43 lotes** de até 15 registros (42 lotes de 15 e o último com 3).
- Resultado final retornado pelo importador: **633 processados, 632 novos, 1 existente, 0 erros**.
- O registro existente é o estabelecimento já gravado no teste individual. A verificação pelo identificador OSM evitou duplicação.
- O modal do painel foi observado pelo usuário atualizando o progresso dos lotes sem erro.

### Correções confirmadas no importador Classic ASP

- O contrato real de entrada de `/admin/descom/importar.asp` usa o campo POST **`linhas`**, não `dados`.
- Cada linha contém 17 campos separados por tabulação, nesta ordem: `EXEC_ID`, tipo OSM, ID OSM, nome, categoria, rua, número, bairro, telefone, e-mail, site, latitude, longitude, URL OSM, tags JSON, localidade e UF.
- A função `SQLNumero` foi corrigida para converter coordenadas decimais para o formato numérico SQL aceito pelo Access. Após a correção, latitude e longitude passaram a ser gravadas e o INSERT foi concluído.
- O JSON de origem fornece `address` como objeto em alguns registros. A montagem dos lotes deve extrair rua, número e bairro desse objeto antes de montar os campos tabulados; não converter o objeto diretamente para texto (o que gera `[object Object]`).
- A resposta de finalização foi corrigida para emitir booleanos JSON válidos (`true`/`false`), em vez dos literais localizados do VBScript (`Verdadeiro`/`Falso`).
- O INSERT em `cad_estabelecimentos` foi diagnosticado com SQL real e passou a funcionar no teste individual e na importação completa.

### Situação da interface e do mapa

- A importação dos 633 registros para o banco operacional foi concluída sem erros.
- O usuário confirmou que a consulta ao banco retorna latitude e longitude para os estabelecimentos.
- **Ainda não está confirmado que os 633 registros sejam entregues ao JavaScript nem que os marcadores sejam criados/exibidos pelo Leaflet.** O mapa ainda não foi validado com esses registros importados.
- A interface atual não oferece uma função visual para recuperar uma execução anterior do GitHub e importar seus resultados. A importação desta execução foi concluída por código executado no Console do navegador; isso é procedimento de diagnóstico pontual, não fluxo operacional aceitável.
- Requisito imediato: implementar na interface DESCOM uma área de execuções/resultados anteriores e ação de importação com progresso por lotes, contadores e tratamento de falhas, sem exigir Console.

### Próximas etapas confirmadas

1. Inspecionar o código atualizado de `/admin/descom/descobrir.asp` e identificar a consulta que fornece os estabelecimentos ao mapa.
2. Verificar a cadeia completa: consulta Access → resposta ASP/JSON → JavaScript → criação dos marcadores Leaflet.
3. Exibir no mapa os estabelecimentos importados de Taguatinga, mantendo lista e marcadores sincronizados e preservando o layout aprovado.
4. Implementar a recuperação/importação de execuções anteriores pela interface, sem Console.
5. Importar os resultados já existentes do Núcleo Bandeirante pelo painel, sem repetir a descoberta, depois que o fluxo de interface estiver pronto.

Não repetir a descoberta de Taguatinga nem reexecutar a importação dos 633 registros. Os dados já foram importados. Não alterar o banco ou a rotina de importação sem necessidade demonstrada.
