# DESCOM — Dossiê funcional e técnico

**Projeto:** GUIA COMERCIAL  
**Agente:** DESCOM — Desbravador Comercial  
**Repositório:** `eddypfernandes/Descom`  
**Status deste documento:** especificação de referência aprovada para orientar as próximas etapas.  
**Importante:** este documento registra decisões e requisitos. Itens classificados como planejados ainda não estão implementados.

---

## 1. Propósito e princípios

O DESCOM será a central de descoberta, revisão geográfica, investigação de dados públicos, aprovação, importação e apoio à prospecção comercial do GUIA COMERCIAL.

Princípio operacional:

> O DESCOM executa as tarefas; o painel coordena; o usuário supervisiona e decide; o GUIA COMERCIAL mantém a base comercial definitiva.

Princípios obrigatórios:

- Preservar o layout aprovado do painel geográfico.
- Não publicar nem importar automaticamente registros brutos.
- Não inventar dados, endereços, contatos ou coordenadas.
- Registrar fonte, data de coleta e grau de confiança das informações.
- Preservar revisões e histórico entre coletas, localidades, sessões e dispositivos.
- Evitar duplicidades entre regiões e execuções.
- Separar dados encontrados publicamente dos dados fornecidos pelo proprietário.
- Respeitar LGPD, licenças, termos de uso e limites das fontes consultadas.
- Não expor tokens ou credenciais no navegador.
- Alterar somente o escopo solicitado, sem descaracterizar funcionalidades aprovadas.

## 2. Modelo de negócio

1. O DESCOM descobre estabelecimentos usando fontes públicas permitidas.
2. Os registros passam por revisão humana.
3. Estabelecimentos aprovados podem compor a vitrine gratuita do Guia, com dados públicos e opção de reivindicação.
4. O proprietário pode reivindicar o perfil, confirmar sua relação com o negócio e fornecer dados complementares.
5. A contratação de plano recorrente habilita serviços e recursos comerciais adicionais.
6. O Guia mantém separados os dados públicos encontrados pelo DESCOM e os dados declarados pelo proprietário.

O DESCOM não deve afirmar que um estabelecimento é recém-inaugurado apenas por ser novo para o robô ou para a base de descobertas.

## 3. Stack e ambiente

- Coletor e rotinas de processamento: Python.
- Fonte inicial de descoberta: OpenStreetMap / Overpass.
- Executor inicial: GitHub Actions.
- Painel administrativo no site: ASP Clássico, HTML5 e Bootstrap 5.3.3.
- Mapa: Leaflet 1.9.4.
- Banco comercial definitivo: MS Access, integrado ao GUIA COMERCIAL.
- Arquivos JSON são utilizados atualmente para resultados de descoberta e triagem.

Não contratar APIs pagas nesta etapa sem decisão expressa. Não usar Gemini nem Tavily. Não automatizar scraping do Google Maps ou contornar controles de acesso. O uso de fontes adicionais deverá respeitar seus termos e condições.

## 4. Localidades: abrangência e configuração geográfica

Há duas responsabilidades distintas:

- `/includes/localidades.txt`: define as localidades que fazem parte da abrangência comercial do Guia.
- `config/regions.json`: mantém a configuração técnica que permite ao DESCOM pesquisar cada localidade.

Adicionar uma localidade ao TXT **não** significa que ela já esteja pronta para coleta. Para pesquisar uma região, o DESCOM precisa de sua configuração geográfica, incluindo identificadores de área/relação quando disponíveis, limites ou área de pesquisa, coordenadas centrais e zoom inicial do mapa.

### 4.1 Fluxo aprovado para ativar uma nova localidade

1. O usuário adiciona a localidade a `/includes/localidades.txt`.
2. O painel lê o TXT e identifica que a localidade ainda não possui configuração correspondente.
3. O painel exibe a localidade como **Aguardando configuração** e oferece a ação **Configurar localidade**.
4. Ao clicar, o DESCOM procura a referência geográfica da localidade em fonte apropriada e permitida.
5. O painel apresenta a área geográfica encontrada para conferência.
6. O usuário confirma ou corrige a seleção.
7. Após confirmação, o sistema grava a configuração em `config/regions.json`.
8. A localidade passa a ser exibida como **Configurada**, ficando disponível para a operação **Descobrir empresas**.

A configuração é uma operação administrativa, normalmente realizada uma única vez por localidade, podendo ser refeita se os limites precisarem de correção. A descoberta é uma operação recorrente e separada.

**Não iniciar descoberta enquanto a localidade não estiver configurada e confirmada.** A interface deve distinguir claramente: configurada, aguardando configuração e eventual erro de configuração.

A configuração geográfica deve ser conferida pelo usuário antes de ser gravada. Não presumir que uma correspondência de nome seja suficiente para identificar corretamente uma região.

## 5. Descoberta de estabelecimentos

Fluxo:

1. Abrir o painel.
2. Selecionar uma localidade configurada.
3. Clicar em **Descobrir empresas**.
4. O DESCOM executa a coleta para aquela localidade.
5. O painel apresenta os resultados no mapa e na lista de estabelecimentos.

A descoberta e a investigação aprofundada de um estabelecimento são operações distintas.

A cobertura do OpenStreetMap varia conforme o mapeamento comunitário. Ausência no resultado não comprova inexistência. Nodes e centros de ways/relations devem ser diferenciados; centros de áreas podem ser aproximados.

## 6. Painel geográfico e interação

O layout atual do painel foi aprovado e deve ser preservado. A evolução deve acrescentar comportamento sem redesenhar ou descaracterizar a interface.

O painel deve manter mapa, marcadores, busca, filtros, cartões e links de referência.

### 6.1 Seleção de marcador

Ao clicar em um marcador:

- Exibir os dados do estabelecimento selecionado.
- Destacar o marcador selecionado.
- Manter os demais marcadores visíveis.
- Não filtrar a lista para um único estabelecimento de forma que elimine o contexto geográfico.
- Permitir selecionar outros pontos sem perder o contexto.

Busca e filtros podem alterar temporariamente os resultados visíveis, mas não podem apagar registros nem estados de revisão.

## 7. Estados de revisão e histórico geográfico

O mapa deve funcionar como histórico geográfico persistente, e não como simples fotografia da última coleta.

Estados previstos por estabelecimento:

| Estado | Significado |
|---|---|
| Pendente | Descoberto, ainda sem confirmação manual |
| Confirmado | Existência e localização conferidas manualmente |
| Rejeitado | Registro rejeitado para a finalidade do Guia |
| Verificado | Dados complementares investigados e aprovados |
| Importado | Cadastro gravado na base comercial do Access |

“Confirmado” e “Verificado” são estados diferentes: confirmar trata da existência/localização; verificar trata do enriquecimento e da aprovação dos dados complementares.

Requisitos:

- Reabrir uma localidade deve recuperar suas marcações anteriores.
- Alternar entre localidades não pode perder o histórico de nenhuma delas.
- Novas coletas não podem sobrescrever revisões anteriores.
- Estados devem sobreviver ao fechamento do navegador e funcionar entre dispositivos.
- Registrar identificador persistente, localidade, fonte, datas e histórico de alterações.
- Evitar duplicidade entre localidades e execuções, sem presumir que nomes iguais representam a mesma empresa.
- Manter contadores por localidade e visão consolidada.

O `localStorage` atualmente utilizado no painel é apenas local ao navegador e não atende ao requisito de persistência definitiva. Deve ser substituído ou complementado por armazenamento persistente no servidor. O Access será a referência dos cadastros importados; descobertas ainda não importadas precisam de armazenamento persistente de trabalho (staging), com histórico.

## 8. Investigação aprofundada — “Buscar mais detalhes”

Cada estabelecimento selecionável deverá oferecer a ação **Buscar mais detalhes**.

A investigação poderá procurar, em fontes públicas acessíveis e permitidas:

- Endereço e referências de localização.
- Telefone e WhatsApp comercial publicado.
- E-mail comercial.
- Site oficial.
- Redes sociais públicas.
- Horários de funcionamento.
- Outras informações úteis ao cadastro comercial.

Cada dado candidato deverá conter, quando disponível:

- Valor encontrado.
- Tipo de informação.
- Fonte e URL.
- Data da coleta.
- Grau de confiança.
- Observações ou divergências.

Não associar automaticamente informações de homônimos. Não presumir que um telefone, perfil social ou endereço pertence ao estabelecimento sem evidência suficiente. Dados ausentes devem permanecer ausentes.

## 9. Fila persistente de investigações

O usuário deve poder solicitar a investigação de um estabelecimento e continuar trabalhando no mapa enquanto a tarefa é executada.

Cada tarefa deverá possuir:

- Identificador próprio.
- Estabelecimento relacionado.
- Data de solicitação.
- Estado: aguardando, em execução, concluída, falhou ou cancelada.
- Tentativas e registro de erros/logs.
- Resultado persistido.
- Proteção contra solicitações duplicadas indevidas.

O processamento pode ser sequencial ou ter concorrência limitada. O painel não pode ficar bloqueado aguardando a conclusão.

Fechar o navegador ou retornar em outro dia não pode apagar a fila nem seus resultados. Não usar artifacts temporários do GitHub Actions como armazenamento definitivo.

## 10. Revisão dos resultados da investigação

Ao concluir uma investigação, o painel deverá apresentar os dados encontrados, suas fontes e possíveis divergências.

O usuário poderá aprovar, corrigir ou rejeitar cada informação. Os dados aprovados compõem o cadastro verificado; os rejeitados devem permanecer rastreáveis no histórico, sem serem utilizados como dados válidos.

Somente estabelecimentos aprovados e aptos poderão ser enviados à importação.

## 11. Importação para o MS Access

A ação **Importar estabelecimentos aprovados** deverá:

1. Selecionar apenas registros aprovados.
2. Validar campos e estados obrigatórios.
3. Verificar duplicidades com a base comercial e com registros já importados.
4. Gravar os dados no Access.
5. Registrar o resultado da operação.
6. Atualizar o estado para **Importado** somente após confirmação da gravação.

A operação deverá ser transacional ou idempotente, evitando gravações parciais e duplicadas. Falhas devem ser registradas e permitir recuperação segura.

Nenhuma descoberta bruta ou registro apenas pendente poderá ser importado automaticamente.

## 12. Indicadores

O painel deverá exibir contadores, por localidade e de forma consolidada, incluindo:

- Descobertos.
- Pendentes.
- Confirmados.
- Rejeitados.
- Verificados.
- Importados.

Os números exibidos deverão vir dos registros persistidos. Exemplos numéricos em documentos ou conversas não são métricas reais.

## 13. Prospecção comercial

Funcionalidade futura aprovada como parte da visão do DESCOM.

O módulo deverá apoiar o relacionamento com proprietários de estabelecimentos, sem disparos indiscriminados.

Estados previstos:

- Não abordado.
- Primeiro contato.
- Em negociação.
- Reivindicado.
- Cliente.
- Sem interesse.

Registrar data, canal, observações e próximo acompanhamento. Respeitar LGPD, finalidade e regras aplicáveis ao contato comercial.

A reivindicação do cadastro deverá permitir que o proprietário confirme sua relação com o estabelecimento e complemente informações. Dados fornecidos pelo proprietário devem permanecer identificados e separados dos dados coletados publicamente.

## 14. Arquitetura operacional pretendida

O painel no site será a interface central de operação. O usuário não deverá precisar navegar pelo GitHub Actions para executar tarefas rotineiras.

Responsabilidades:

| Componente | Responsabilidade |
|---|---|
| Painel Bootstrap + Leaflet | Mapa, busca, filtros, revisão e acompanhamento |
| ASP Clássico | Autenticação, autorização, validação e comunicação servidor-servidor |
| DESCOM Python | Descoberta, configuração assistida e investigação |
| GitHub Actions ou executor equivalente | Execução dos trabalhos em segundo plano |
| Armazenamento persistente | Fila, resultados, estados e histórico |
| MS Access | Base comercial definitiva dos registros importados |

O GitHub Actions é um executor assíncrono, não um serviço de resposta instantânea. A arquitetura deverá tolerar espera, falhas, limites e novas tentativas.

Credenciais devem permanecer no servidor ou em secrets apropriados. Nunca expor token do GitHub no JavaScript/browser. Implementar autenticação, autorização, validação de parâmetros, proteção contra CSRF e contra repetição indevida de comandos.

## 15. Fluxo operacional completo

1. Abrir o painel.
2. Selecionar localidade.
3. Se ainda não configurada, executar **Configurar localidade**, conferir a área e confirmar.
4. Clicar em **Descobrir empresas**.
5. Interagir com mapa, busca, filtros e cartões.
6. Selecionar estabelecimento sem ocultar os demais marcadores.
7. Clicar em **Buscar mais detalhes**.
8. Acompanhar a fila enquanto continua trabalhando.
9. Consultar resultados, fontes e divergências.
10. Aprovar, corrigir ou rejeitar informações.
11. Selecionar estabelecimentos aptos.
12. Clicar em **Importar estabelecimentos aprovados**.
13. Validar e gravar no Access.
14. Atualizar estados, histórico e indicadores.
15. Consultar o resumo da operação.

O mapa e o histórico permanecem preservados ao encerrar uma ou várias operações.

## 16. Estado atual: construído versus planejado

### Já existente no repositório (conforme o estado conhecido do projeto)

- Coletor Python baseado em OpenStreetMap / Overpass.
- Configuração técnica de regiões em `config/regions.json`.
- Workflow GitHub Actions com operações de validação, descoberta e triagem.
- Rotina de triagem.
- Arquivos JSON de descobertas e triagem por região.
- Painel geográfico estático com Bootstrap e Leaflet.
- Busca, filtros, cartões, marcadores e links de referência.
- Marcações de revisão no navegador via `localStorage`, com exportação JSON.
- Configuração e coletas iniciais para Núcleo Bandeirante e Riacho Fundo I.

### Ainda planejado / a implementar

- Leitura dinâmica de `/includes/localidades.txt` pelo painel hospedado.
- Identificação visual de localidades sem configuração.
- Ação **Configurar localidade**, com busca geográfica, conferência humana e gravação em `config/regions.json`.
- Bloqueio de descoberta até a confirmação da configuração geográfica.
- Seleção de marcador sem ocultar os demais pontos.
- Persistência centralizada e cumulativa de estados e histórico.
- Identificadores persistentes e prevenção de duplicidade entre localidades/coletas.
- Integração do painel hospedado com o executor.
- Fila persistente de tarefas e resultados.
- Investigador de dados públicos.
- Revisão individual dos dados investigados.
- Importação segura e idempotente para Access.
- Indicadores consolidados.
- Módulo de prospecção comercial.

A lista de itens existentes é um registro do estado conhecido do projeto e deverá ser conferida no código antes de cada implementação. Não equivale a uma certificação de testes em produção.

## 17. Sequência sugerida de implementação

A ordem técnica poderá ser refinada após inspeção do código, mas deve respeitar as dependências:

1. Inspecionar e documentar contratos atuais de dados, IDs e arquivos.
2. Integrar o painel ao TXT de localidades e exibir estado de configuração.
3. Implementar configuração geográfica assistida e confirmação humana.
4. Ajustar seleção do mapa para preservar os demais marcadores.
5. Definir armazenamento persistente, modelo de dados e histórico.
6. Integrar painel, ASP e executor com segurança.
7. Implementar fila persistente.
8. Implementar investigação e revisão dos resultados.
9. Implementar importação segura para Access.
10. Implementar indicadores e prospecção comercial.

Nenhuma etapa deverá quebrar o layout aprovado ou eliminar dados/histórico existentes.

## 18. Critérios de aceite essenciais

- Localidade no TXT sem configuração aparece como **Aguardando configuração**.
- A configuração geográfica exige conferência e confirmação humana.
- Não é possível iniciar descoberta em localidade não configurada.
- Depois de configurada, a localidade pode ser descoberta sem repetir a configuração.
- Clicar em marcador não remove os demais pontos do mapa.
- Histórico permanece após nova coleta, fechamento do navegador e troca de dispositivo.
- Uma tarefa de investigação permanece na fila mesmo se o usuário sair do painel.
- Cada informação investigada apresenta fonte e data, quando disponíveis.
- Nenhum registro é importado sem aprovação.
- Importações repetidas não criam duplicatas.
- Falhas ficam registradas e não marcam registros como importados.
- O layout aprovado permanece visualmente preservado.

---

**Regra de manutenção deste dossiê:** decisões aprovadas devem ser registradas aqui antes de mudanças relevantes. Ao concluir uma implementação, atualizar a seção de estado atual, distinguindo claramente implementado, testado e publicado. Nunca marcar como concluído algo que tenha sido apenas planejado ou revisado estaticamente.


---

# ADENDO DE CONTINUIDADE — 04/11/2026

Este adendo prevalece sobre descrições anteriores de interface e sequência de implementação quando houver divergência. O histórico abaixo foi mantido para preservar decisões anteriores; o estado real está discriminado entre implementado, configurado e pendente.

## A. Direção de interface atual

Foi criada uma nova central administrativa independente em `docs/central/index.html`. Ela passa a ser a nova direção visual do painel DESCOM/ADÃO. Os arquivos anteriores foram preservados:

- `docs/revisao/index.html`: painel de revisão/geografia anteriormente aprovado; não substituir nem alterar sem necessidade concreta.
- `docs/revisao/operacao.html`: prévia operacional anterior, mantida como referência.
- `docs/central/index.html`: nova central administrativa, com Bootstrap 5.3.3 e Leaflet 1.9.4.

A nova central apresenta navegação por áreas, indicadores, seleção de localidade, mapa, busca, filtros e listagem de estabelecimentos. Consulta os JSON públicos existentes no repositório para descobertas e triagem. É uma interface de prévia conectada aos arquivos públicos, não uma aplicação operacional integrada ao Access.

A publicação foi adicionada ao workflow existente `.github/workflows/modulo-pages.yml`, copiando `docs/central/` para `site/central/`. O endereço esperado é `/Descom/central/`. A configuração do workflow foi commitada; a publicação efetiva no Pages ainda precisa ser confirmada no histórico de execução do GitHub Actions.

## B. Banco operacional e conexão ASP — aprovados pelo usuário

O usuário forneceu e confirmou a estrutura do banco Access `descom.accdb`, com estas 11 tabelas:

1. `tb_localidades`
2. `tb_regioes_tecnicas`
3. `tb_estabelecimentos`
4. `tb_coletas`
5. `tb_revisoes`
6. `tb_fontes_dados`
7. `tb_investigacoes`
8. `tb_fila_tarefas`
9. `tb_historico_status`
10. `tb_importacoes`
11. `tb_prospeccao`

Os índices únicos e relacionamentos apresentados pelo usuário fazem parte da estrutura aprovada. Não recriar tabelas, não propor banco paralelo e não reabrir a auditoria estrutural sem evidência concreta de problema.

A conexão Classic ASP informada utiliza `ADODB.Connection`, `Microsoft.ACE.OLEDB.12.0`, caminho resolvido por `Server.MapPath("/bd/descom.accdb")` e objeto global `connAdao`. O usuário declarou a conexão e o banco corretos. Considerá-los base aprovada para a implementação.

## C. Arquitetura operacional definida

- **Painel:** nova central administrativa como interface de operação do ADÃO.
- **Classic ASP/IIS:** camada de servidor para autenticação, autorização, comandos, validação e acesso ao Access.
- **Access:** persistência operacional nas 11 tabelas aprovadas.
- **GitHub Actions:** executor assíncrono das rotinas Python já existentes.
- **Python/JSON:** coleta, geografia e triagem; os JSON versionados continuam preservados como dados e trilha de execução enquanto a integração é construída.

O navegador nunca receberá token do GitHub. A comunicação com Actions deverá ocorrer pelo servidor ASP, com segredo mantido exclusivamente no servidor. O runner do GitHub não acessará diretamente o arquivo Access local do IIS. O retorno deverá ser enviado de volta ao ASP por mecanismo autenticado ou obtido pelo ASP de forma segura.

## D. Estado real após a criação da nova central

### Implementado no repositório
- Nova interface em `docs/central/index.html`.
- Consulta dos arquivos `descobertas.json` e `triagem.json` por localidade para exibir os dados disponíveis.
- Mapa Leaflet, busca, filtros, indicadores e listagem.
- Preservação dos painéis anteriores e dos dados existentes.
- Workflow Pages ajustado para incluir a pasta `docs/central/` na publicação.

### Existente anteriormente e mantido
- Workflow `.github/workflows/descom.yml` com ações de validação, descoberta, triagem e geografia.
- `scripts/main.py`, `scripts/triage.py` e `scripts/geography.py`.
- Configurações em `config/regions.json`.
- Arquivos JSON por localidade, incluindo a base já coletada de Taguatinga.
- Banco Access e painel Classic ASP no ambiente local do usuário (não versionados neste repositório).

### Ainda não implementado / não confirmado
- Publicação efetiva da nova central no GitHub Pages (workflow configurado; execução ainda não confirmada).
- Comandos reais no painel para iniciar descoberta e outras tarefas.
- Integração ASP → GitHub Actions autenticada.
- Retorno de status e resultados das Actions ao ASP.
- Gravação idempotente dos resultados nas tabelas Access.
- Fila operacional persistente e acompanhamento de tarefas pelo painel.
- Investigação aprofundada de estabelecimentos e persistência de fontes.
- Revisão humana persistente no servidor.
- Importação idempotente para a base do Guia Comercial.

## E. Próxima entrega técnica — sem reiniciar o projeto

A próxima entrega é a integração vertical mínima e funcional, nesta ordem:

1. Instalar a nova central no ambiente ASP, mantendo a interface e adaptando somente os caminhos/contratos necessários.
2. Criar uma única camada ASP autenticada para receber comandos do painel e acionar o workflow existente.
3. Registrar a solicitação e a execução nas tabelas operacionais já existentes.
4. Fazer o executor devolver o resultado ao servidor ASP de forma autenticada.
5. Persistir estabelecimentos e histórico no Access sem duplicar registros.
6. Atualizar a central para exibir estado real da execução e dados persistidos.
7. Testar o ciclo completo em uma localidade já habilitada antes de expandir.

Não criar outro painel, outro banco, tabelas adicionais ou workflows redundantes. Não limpar JSONs nem recomeçar coleta. Não declarar o ciclo completo até que uma execução real seja disparada pelo painel, retorne ao ASP, grave no Access e apareça novamente na interface.

