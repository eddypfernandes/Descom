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


---

# ADENDO DE CONTINUIDADE — 07/11/2026 (política de refinamento e fluxo operacional mestre)

Este registro prevalece sobre qualquer orientação histórica que sugira reconstrução, substituição de painel ou reinício do projeto. A partir deste marco, o trabalho seguirá por **refinamentos pontuais sobre o que já existe e funciona**.

## 1. Diretriz obrigatória de desenvolvimento

- **Não reconstruir o DESCOM.**
- **Não reiniciar etapas concluídas nem destruir/recriar estruturas existentes.**
- Preservar integralmente funcionalidades, dados, rotinas, integrações e decisões já validadas.
- Implementar somente melhorias pontuais, correções comprovadamente necessárias e refinamentos de interface ou fluxo.
- Antes de propor alteração em banco, consultar a estrutura real já documentada e o código em uso. Não criar tabela, cadastro ou relacionamento duplicado.
- Não substituir uma rotina funcional por outra apenas por preferência de arquitetura.
- Uma melhoria só será considerada concluída depois de implementada e validada no ambiente correspondente. Requisito deliberado não equivale a funcionalidade implementada.

## 2. Base operacional atual a preservar

O painel operacional em uso é ASP Clássico, Bootstrap 5.3.3, Access e Leaflet 1.9.4. O arquivo central em evolução é /admin/descom/areas.asp, conectado pelo include /admin/descom/conexao_descom.asp ao banco operacional SYS_DESCOM no caminho já definido pelo projeto.

A versão de areas.asp fornecida pelo usuário em 07/11/2026 contém e deve preservar:

- Cadastro AJAX de localidades pelo modal, com atualização imediata do dropdown.
- Identificação do limite administrativo por Nominatim/OpenStreetMap.
- Exibição da geometria no Leaflet.
- Confirmação e gravação da área em geo_areas.
- Consulta AJAX dos estabelecimentos relacionados à localidade.
- Marcadores no mapa e lista de estabelecimentos.
- Sincronização de seleção entre marcador e item da lista.
- Ação de início da descoberta reutilizando iniciar.asp.
- Listagem de áreas já cadastradas.
- Importador existente em /admin/descom/importar.asp, cuja importação de Taguatinga foi validada.

Estruturas operacionais identificadas no código e no banco atual: geo_localidades, geo_areas, cad_estabelecimentos, cad_identificadores, int_execucoes, int_evidencias, int_tarefas, rev_decisoes, int_importacoes e demais tabelas já existentes no SYS_DESCOM. A estrutura real deve ser consultada antes de qualquer alteração. Não confundir essa base operacional com o banco comercial histórico SYS_RADAR.mdb.

A tabela cad_estabelecimentos, já criada e utilizada na importação do DESCOM, também poderá servir como fonte para o módulo home_empresa.asp do Guia Comercial. Essa integração é uma possibilidade aprovada como direção de uso, mas não significa publicação automática: descoberta, enriquecimento, validação e publicação comercial continuam sendo etapas distintas.

## 3. Fluxo operacional mestre aprovado — da localidade ao enriquecimento

O fluxo abaixo representa a experiência desejada para o administrador master. Ele foi deliberado e aprovado como referência funcional; os itens ainda não implementados permanecem explicitamente planejados.

### Etapa A — Cadastro e gestão de localidades

1. O administrador master entra no site e acessa a aba Comercial/painel DESCOM.
2. No primeiro uso, o dropdown de localidades pode estar vazio. Os controles de confirmação e descoberta permanecem indisponíveis enquanto não houver localidade selecionada e área aprovada.
3. O link **Adicionar local** fica imediatamente acima do dropdown.
4. O link abre um modal no qual o administrador informa somente o nome da cidade/região e a sigla da UF.
5. O modal também apresenta uma lista rolável das localidades cadastradas.
6. Selecionar um item da lista permitirá editar ou excluir a localidade, conforme regras de integridade e dependências.
7. A exclusão não poderá apagar em cascata áreas, execuções, evidências ou estabelecimentos históricos. Antes de implementar exclusão, definir bloqueio/arquivamento e mensagens quando existirem dependências. Não excluir fisicamente dados históricos por conveniência.
8. Após salvar, o modal atualiza a lista e o dropdown da página principal sem redirecionar. A nova localidade pode ficar selecionada automaticamente.

### Etapa B — Identificação e aprovação territorial

1. Ao selecionar uma localidade, o sistema consulta o serviço geográfico e identifica o limite administrativo.
2. O polígono é desenhado e enquadrado no mapa.
3. Antes da primeira descoberta, o mapa pode estar sem marcadores: isso é o estado esperado de uma área ainda não investigada.
4. O administrador confere o limite e pode ajustar a geometria/abrangência quando a ferramenta de edição estiver disponível.
5. O controle **Confirmar área** aparece somente quando existe uma geometria válida ainda não aprovada.
6. Ao confirmar, a área é persistida e seu estado passa a aprovada. O controle de confirmação deixa de aparecer.
7. A área aprovada deve ser recuperada do banco nas visitas seguintes. Uma nova consulta automática ao Nominatim não pode sobrescrever silenciosamente a geometria aprovada.

### Etapa C — Descoberta de estabelecimentos

1. Depois da aprovação, aparece **Descobrir empresas** somente se não houver descoberta concluída para o contexto operacional selecionado.
2. A descoberta reutiliza o mecanismo e os endpoints já existentes, inclusive iniciar.asp e o importador funcional, sem reconstruir o pipeline.
3. A interface apresenta feedback de execução; se o processo terminar rapidamente, o estado final deve ser mostrado sem exigir que o usuário veja obrigatoriamente uma animação.
4. Os registros são associados à localidade, à área e à execução, com identificadores de origem para evitar duplicidade.
5. Ao concluir, o mapa apresenta os marcadores e a lista lateral apresenta os mesmos estabelecimentos.

### Etapa D — Mapa e lista sincronizados

1. Em desktop, o mapa deve ocupar a maior parte da largura e a lista ficar em coluna lateral; em telas pequenas, mapa e lista ficam empilhados.
2. O mapa deve ter altura confortável e a lista deve possuir rolagem própria, sem alongar indefinidamente a página.
3. Clicar em um item da lista seleciona/destaca o marcador correspondente e centraliza o mapa.
4. Clicar em um marcador seleciona o item correspondente e o leva à área visível da lista, preferencialmente ao topo do painel rolável.
5. A seleção de um estabelecimento não deve remover os demais marcadores nem perder o contexto da região.
6. Os dois componentes devem operar sobre os mesmos registros persistidos, não sobre listas independentes.

### Etapa E — Buscar mais detalhes

1. Cada estabelecimento poderá oferecer **Buscar mais detalhes**, tanto no item da lista quanto no popup do marcador.
2. A ação sempre deve carregar o identificador do estabelecimento efetivamente selecionado.
3. ADÃO executará investigação de fontes públicas permitidas para localizar dados complementares, como nome empresarial/fantasia, CNPJ quando disponível, endereço, telefone, e-mail, site e perfis públicos.
4. A operação deve informar andamento por modal com spinner e mensagens de estado, sem bloquear desnecessariamente a navegação.
5. Cada dado encontrado deve manter fonte/URL, data de coleta e grau de confiança quando disponíveis. Não associar dados de homônimos sem evidência suficiente.
6. A investigação não deve sobrescrever automaticamente dados já aprovados. Divergências e valores candidatos devem permanecer rastreáveis.

### Etapa F — Pré-preenchimento do cadastro comercial

1. Ao concluir a investigação, o painel poderá abrir a página de cadastro da empresa no Guia Comercial, com os campos disponíveis pré-preenchidos.
2. O administrador confere, corrige e decide quais dados serão efetivamente aceitos.
3. Descobrir um estabelecimento não equivale a cadastrá-lo/publicá-lo automaticamente no Guia.
4. A tabela cad_estabelecimentos pode alimentar home_empresa.asp como origem de estabelecimentos selecionados e validados, mediante regra de elegibilidade/publicação definida. Não exibir indiscriminadamente todos os registros brutos descobertos.

## 4. Máquina de estados e regras de visibilidade dos controles

Não tratar o processo como um único estado. O estado territorial e o estado da investigação são independentes, embora relacionados.

**Estado territorial:**
- Sem área identificada.
- Área identificada, aguardando confirmação.
- Área aprovada.

**Estado da investigação:**
- Não iniciada.
- Em andamento.
- Concluída.
- Falhou/cancelada, com possibilidade de nova tentativa controlada.

Comportamento esperado da interface:

| Estado real | Controles e conteúdo |
|---|---|
| Nenhuma localidade cadastrada | Link Adicionar local disponível; dropdown vazio; demais controles indisponíveis. |
| Localidade selecionada, sem área identificada | Mostrar mapa/feedback de identificação; não mostrar confirmação até existir geometria válida. |
| Geometria identificada, ainda não aprovada | Mostrar **Confirmar área**. |
| Área aprovada, investigação ainda não iniciada | Ocultar confirmação e salvar; mostrar **Descobrir empresas**. |
| Investigação em andamento | Mostrar estado/progresso; impedir disparos duplicados da mesma operação. |
| Investigação concluída com resultados | Ocultar controles iniciais de confirmação/descoberta; mostrar mapa, lista e ação de enriquecimento por estabelecimento. |
| Investigação falhou ou foi cancelada | Mostrar o estado e uma ação explícita de tentar novamente, sem apagar histórico nem registros já coletados. |

O sistema não deve oferecer ao usuário uma ação cuja etapa já foi concluída. A tela deve apresentar a próxima ação necessária, de acordo com os estados persistidos.

## 5. Refinamentos pontuais já identificados para areas.asp

- Remover o campo visual **Território identificado**, pois repete a localidade já escolhida no dropdown. A identificação geográfica permanece automática; somente o campo redundante será retirado.
- Manter o link **Adicionar local** acima do dropdown.
- Mover a lista de estabelecimentos para a lateral do mapa em desktop e empilhá-la abaixo do mapa em dispositivos móveis.
- Ajustar a altura do mapa e manter rolagem interna na lista.
- Tornar a confirmação e os botões de salvar/descobrir condicionais ao estado real da área e da investigação.
- Preservar IDs, contratos AJAX, SQL, rotinas ASP, importador e sincronização já existentes, salvo necessidade técnica demonstrada.
- A edição/exclusão de localidades será deliberada e implementada separadamente, depois de definir as regras de dependência e proteção dos dados.

Esses refinamentos foram aprovados como direção, mas **não devem ser marcados como implementados** até alteração e teste no arquivo real.

## 6. Próximo método de trabalho

1. Usar o areas.asp fornecido pelo usuário em 07/11/2026 como referência de código atual, sem pedir novamente o mesmo conteúdo enquanto estiver disponível no histórico.
2. Inspecionar o banco e as rotinas existentes antes de qualquer mudança de estado ou consulta.
3. Implementar uma melhoria pequena por vez.
4. Preservar o que já funciona; não reformatar ou reescrever blocos não relacionados ao pedido.
5. Testar o comportamento da etapa alterada antes de avançar.
6. Atualizar este dossiê com a mudança, indicando separadamente **deliberado**, **implementado**, **testado** e **publicado**.
7. Não declarar como concluída uma funcionalidade apenas porque foi desenhada ou descrita.

**Regra principal deste marco: refinamento contínuo, não reconstrução. O DESCOM já está em andamento; a prioridade é fazê-lo avançar com segurança.**


## Inventário de páginas e componentes (obrigatório durante desenvolvimento)

O inventário técnico de páginas foi criado em [docs/INVENTARIO-PAGINAS-DESCOM.md](INVENTARIO-PAGINAS-DESCOM.md). Ele registra caminho, responsabilidade, dependências, endpoints, tabelas, situação de implementação e refinamentos pendentes. Toda página nova ou alteração relevante deverá atualizar esse inventário.

O inventário distingue expressamente código compartilhado no chat/ambiente local de código efetivamente versionado no GitHub. Não presumir que páginas ASP estejam publicadas no repositório só porque existem no painel local. A partir deste marco, consultar o inventário antes de solicitar novamente códigos, caminhos ou informações já documentadas.
