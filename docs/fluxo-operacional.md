# Fluxo operacional do DESCOM

**Status:** fluxo inicial definido  
**Primeira área de atuação:** Núcleo Bandeirante — DF  
**Saída principal:** data/nucleo-bandeirante/estabelecimentos.json

## 1. Objetivo

Estabelecer a ordem de trabalho do DESCOM, desde a preparação de uma pesquisa até a gravação da base consolidada. O fluxo deve seguir os critérios definidos nos documentos de estratégia, formato JSON, organização dos arquivos, identificação, deduplicação e validação.

## 2. Sequência de execução

### Etapa 1 — Definir o recorte da pesquisa

Selecionar a Região Administrativa e o grupo de atividades a pesquisar.

Na primeira etapa do projeto, o recorte territorial é o Núcleo Bandeirante. A pesquisa deve avançar por grupos de atividades para facilitar o acompanhamento da cobertura e reduzir repetições.

### Etapa 2 — Identificar fontes adequadas

Selecionar fontes públicas pertinentes ao tipo de informação procurada.

Antes de consultar uma fonte, respeitar seus termos de uso, limites de acesso e condições de reutilização. Não contornar autenticação, bloqueios ou proteções técnicas.

### Etapa 3 — Coletar candidatos

Registrar os estabelecimentos encontrados e as informações efetivamente disponíveis.

Cada candidato deve manter referência à fonte e à data da consulta. Campos não encontrados permanecem desconhecidos; não completar dados por inferência.

### Etapa 4 — Normalizar informações

Preparar cópias normalizadas dos campos necessários à comparação, como nome, telefone, endereço e URL.

A normalização não deve apagar o valor original nem a referência à fonte.

### Etapa 5 — Comparar com a base existente

Comparar cada candidato com os registros já existentes na base da mesma Região Administrativa, usando os critérios do documento docs/identificacao-deduplicacao.md.

O resultado da comparação deve ser um destes:

- correspondência confirmada;
- possível duplicidade;
- registro distinto.

Possíveis duplicidades não devem ser mescladas nem excluídas automaticamente.

### Etapa 6 — Validar as informações

Avaliar identidade, nome, endereço, contatos, localização e situação de funcionamento de acordo com o documento docs/validacao-confiabilidade.md.

Atribuir o estado de validação e o nível de confiança compatíveis com as evidências. Divergências relevantes devem permanecer registradas e sem resolução automática.

### Etapa 7 — Consolidar o registro

Para um novo estabelecimento, criar um ID estável e definir dates.first_seen_at com a data da primeira identificação.

Para uma correspondência confirmada, atualizar o registro existente, preservando o ID e dates.first_seen_at. Atualizar dates.last_checked_at a cada conferência e dates.last_updated_at somente quando houver alteração efetiva.

Acrescentar as novas fontes e não apagar informações válidas apenas porque uma fonte recente não as informa.

### Etapa 8 — Verificar a integridade do arquivo

Antes de gravar a saída:

- confirmar que o JSON é válido e está em UTF-8;
- conferir a presença dos campos obrigatórios e os tipos de dados definidos em docs/formato-dados-json.md;
- verificar que os IDs são únicos dentro da base;
- verificar que não foram criadas duplicidades confirmadas;
- confirmar que datas originais foram preservadas nas atualizações;
- garantir que valores desconhecidos estejam representados por null e listas vazias por [];
- confirmar que não foram incluídos dados fictícios, segredos ou informações pessoais desnecessárias.

Se a validação estrutural falhar, não substituir o arquivo consolidado por uma saída inválida.

### Etapa 9 — Gravar a base consolidada

Gravar o resultado em data/nucleo-bandeirante/estabelecimentos.json, mantendo um único arquivo consolidado por Região Administrativa.

Não criar um arquivo novo por execução. Não publicar registros que não tenham passado pelas verificações estruturais mínimas.

### Etapa 10 — Registrar o resultado da execução

Informar, no resumo da execução:

- Região Administrativa e grupo pesquisado;
- fontes consultadas;
- quantidade de candidatos identificados;
- novos registros incluídos;
- registros existentes atualizados;
- possíveis duplicidades encaminhadas para revisão;
- registros sem alteração;
- falhas, divergências e limitações encontradas.

O resumo deve permitir entender o que foi feito sem exigir a leitura de todos os registros.

## 3. Regras que nunca devem ser violadas

1. Não inventar nem completar informações por suposição.
2. Não apagar ou mesclar registros ambíguos automaticamente.
3. Não alterar o ID nem a data de primeira identificação em atualizações.
4. Não descartar a proveniência das informações.
5. Não classificar um negócio como inativo sem evidência suficiente.
6. Não confundir cadastro público com cliente ou assinante do GUIA COMERCIAL.
7. Não coletar além do necessário nem contornar restrições das fontes.
8. Não substituir uma base válida por um arquivo estruturalmente inválido.

## 4. Limites da primeira implementação

O primeiro desenvolvimento deverá executar o fluxo para o Núcleo Bandeirante e produzir o arquivo JSON consolidado.

Não fazem parte desta primeira implementação:

- painel administrativo ou interface de revisão;
- reivindicação de cadastro pelo comerciante;
- gestão de assinaturas ou relacionamento comercial;
- importação para MS Access;
- publicação automática no site;
- expansão simultânea para várias Regiões Administrativas;
- pontuação complexa ou inteligência artificial adicional sem necessidade demonstrada.

## 5. Critério de conclusão de uma execução

Uma execução é concluída com sucesso quando a pesquisa realizada é registrada, os candidatos são comparados e avaliados, a saída passa pelas verificações estruturais e o arquivo consolidado é gravado sem perda das informações e datas que precisam ser preservadas.

Se houver falha que impeça a gravação segura, a execução deve informar o problema e manter intacta a última versão válida da base.
