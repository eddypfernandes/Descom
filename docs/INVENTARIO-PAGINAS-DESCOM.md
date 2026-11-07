# Inventário técnico de páginas e arquivos — DESCOM
Atualização: 07/11/2026

> Documento de continuidade obrigatório durante a fase de desenvolvimento. Serve para evitar reabrir chats, repetir cópia de código e perder o vínculo entre páginas, funções e fluxo operacional.
>
> **Importante:** este inventário distingue arquivos informados/confirmados no contexto de desenvolvimento de arquivos cujo conteúdo foi efetivamente consultado no repositório. A existência de uma página no ambiente local não significa automaticamente que seu código esteja versionado no GitHub.

## 1. Painel DESCOM — páginas e componentes

| Arquivo/caminho | Responsabilidade | Situação conhecida |
|---|---|---|
| `/admin/descom/areas.asp` | Central operacional: cadastro modal de localidades, seleção, identificação territorial OSM/Nominatim, mapa Leaflet, aprovação da área, consulta de estabelecimentos, marcadores/lista sincronizados e acesso à descoberta. | Código integral fornecido pelo usuário em 07/11/2026; versão-base atual de refinamentos. Não afirmar teste integral. |
| `/admin/descom/iniciar.asp` | Inicia o processo de descoberta para a localidade selecionada; acionado por `areas.asp`. | Rotina existente a preservar; detalhes internos pendentes de inventário de código. |
| `/admin/descom/importar.asp` | Recebe resultados e importa estabelecimentos em lotes para o Access, com identificadores e evidências. | Importador funcional; importação de Taguatinga (EXEC_ID 26) validada em 43 lotes: 633 processados, 632 novos, 1 existente, 0 erros. |
| `/admin/descom/descobrir.asp` | Tela anterior de seleção de áreas e acionamento de descoberta/importação. | Existente, mas não é a central operacional desejada; manter sem reconstruir enquanto não houver necessidade. |
| `/admin/descom/localidades.asp` | Cadastro anterior de localidades. | Existente; cadastro principal foi incorporado ao modal de `areas.asp`. Não remover sem verificar dependências. |
| `/admin/descom/conexao_descom.asp` | Include de conexão com banco SYS_DESCOM. | Include de conexão utilizado pelo painel. |
| `/admin/descom/config_github.asp` | Configura integração/credenciais/parametrização GitHub do painel. | Arquivo conhecido; preservar configuração e não expor segredos no dossiê. |
| `/admin/bd/SYS_DESCOM.mdb` | Banco operacional Access do DESCOM. | Fonte persistente do painel; não recriar. |
| `/admin/descom/areas.asp` — AJAX `cadastrar_localidade` | Cadastra localidade via modal e retorna JSON; atualiza dropdown no navegador. | Implementado no código-base compartilhado. |
| `/admin/descom/areas.asp` — AJAX `listar_estabelecimentos` | Consulta estabelecimentos com evidências/execuções ligadas à localidade e devolve JSON. | Implementado no código-base compartilhado; mapa ainda precisa de validação visual. |
| `/admin/descom/areas.asp` — formulário `salvar` | Persiste área aprovada em `geo_areas`. | Implementado no código-base compartilhado; evolução de estados pendente. |

## 2. Bibliotecas e tecnologias da central

- ASP Clássico / VBScript.
- Microsoft Access (SYS_DESCOM).
- Bootstrap 5.3.3.
- Leaflet 1.9.4.
- OpenStreetMap como camada cartográfica.
- Nominatim para identificação de limites administrativos.
- JavaScript Fetch/AJAX para cadastro e consulta.
- JSON para comunicação entre ASP e navegador.

## 3. Dependências funcionais

`areas.asp` → `iniciar.asp` → coleta/execução GitHub → `importar.asp` → tabelas de estabelecimentos, identificadores e evidências → consulta AJAX em `areas.asp` → mapa + lista.

A página central não deve duplicar o pipeline de descoberta nem a lógica do importador.

## 4. Banco operacional — principais relações usadas pela interface

- `geo_localidades.LOC_ID` → `int_execucoes.LOC_ID`.
- `geo_areas.AREA_ID` → `int_execucoes.AREA_ID`.
- `int_execucoes.EXEC_ID` → `int_evidencias.EXEC_ID`.
- `cad_estabelecimentos.EST_ID` → `int_evidencias.EST_ID`.
- `cad_estabelecimentos.EST_ID` → `cad_identificadores.EST_ID`.

A consulta atual da lista de empresas parte de `cad_estabelecimentos`, relaciona `int_evidencias` e `int_execucoes`, e filtra `int_execucoes.LOC_ID`. Antes de modificar a consulta, verificar se a seleção precisa considerar área, execução mais recente ou status — não alterar sem decisão e teste.

## 5. Registro de páginas futuras — ainda não implementadas

| Página/componente | Objetivo | Estado |
|---|---|---|
| Modal de localidades (dentro de `areas.asp`) | Listar localidades com rolagem e permitir edição/exclusão segura. | Cadastro atual existe; lista/edição/exclusão ainda são refinamentos. |
| Modal de investigação de empresa | Mostrar spinner, mensagens e estado de enriquecimento de dados públicos. | Planejado. |
| Página/formulário de cadastro comercial | Receber dados enriquecidos e permitir revisão/preenchimento. | Integração futura; não confundir descoberta com publicação. |
| `home_empresa.asp` | Exibir empresas elegíveis no Guia Comercial. | Integração futura com `cad_estabelecimentos`, sujeita a critérios de validação/publicação. |

## 6. Política obrigatória para manter este inventário

Sempre que uma página for criada, alterada ou validada, registrar aqui:

1. caminho exato;
2. finalidade e responsabilidade;
3. includes, páginas chamadas e endpoints AJAX;
4. tabelas/consultas que utiliza;
5. campos/IDs de formulário e contratos JSON relevantes;
6. estado: deliberado, implementado, testado ou publicado;
7. última alteração e próximo refinamento.

Não é necessário colar o código completo no dossiê a cada mudança pequena. Registrar o resumo técnico, contratos e decisões; o código-fonte versionado deve permanecer no repositório/ambiente apropriado. Se o código não estiver no GitHub, deixar isso explícito e não inventar um link ou presumir sincronização.
