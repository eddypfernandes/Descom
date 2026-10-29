# Identificação e deduplicação de estabelecimentos — DESCOM

**Status:** critérios iniciais  
**Escopo:** identificar registros que representam o mesmo estabelecimento e evitar duplicidades na base.

## 1. Objetivo

Cada estabelecimento deve possuir um único registro principal na base da respectiva Região Administrativa. O DESCOM deve reconhecer quando fontes diferentes se referem ao mesmo local, sem juntar negócios distintos apenas porque têm nomes parecidos.

A deduplicação deve priorizar a precisão. Em caso de dúvida, preservar os registros e encaminhar a situação para revisão.

## 2. Identidade do registro

Cada estabelecimento recebe um identificador interno estável no campo `id`.

- O identificador é criado quando o registro é incluído pela primeira vez.
- Atualizações não podem gerar um novo identificador.
- Alterações de nome, telefone, endereço ou site não devem, isoladamente, provocar a troca do identificador.
- Um estabelecimento com filiais ou unidades em endereços diferentes deve ter um registro por unidade, quando cada local puder ser identificado individualmente.

## 3. Sinais usados na comparação

O DESCOM deve comparar os dados disponíveis, considerando principalmente:

1. **Identificadores oficiais ou próprios:** CNPJ divulgado publicamente ou identificador inequívoco da unidade, quando disponível e apropriado.
2. **Endereço:** logradouro, número, complemento e região administrativa.
3. **Telefone:** número normalizado, considerando DDD e variações de formatação.
4. **Site e presença pública:** domínio oficial e páginas que identifiquem claramente a mesma unidade.
5. **Nome comercial:** nome normalizado, desconsiderando diferenças simples de caixa, acentuação, pontuação e espaços.
6. **Localização:** coordenadas próximas, usadas como indício complementar, nunca como prova isolada.

Nenhum sinal isolado de semelhança deve ser tratado automaticamente como confirmação, exceto quando houver identificador inequívoco e correspondência consistente.

## 4. Normalização para comparação

Antes de comparar registros, o agente poderá normalizar os valores para análise:

- nomes em minúsculas, sem diferenças de acentuação, pontuação ou espaços repetidos;
- telefones somente com dígitos, preservando DDD;
- endereços com espaços e abreviações padronizados para comparação;
- URLs sem parâmetros de rastreamento, quando isso puder ser feito sem alterar o destino;
- coordenadas em formato numérico.

A normalização serve à comparação. O valor original encontrado na fonte deve continuar disponível no registro ou em sua proveniência, para evitar perda de informação.

## 5. Decisão de correspondência

Classificar cada comparação em uma destas situações:

- **Correspondência confirmada:** há identificador inequívoco compatível ou combinação forte de sinais, sem divergências relevantes. Atualizar o registro existente e acrescentar a nova fonte.
- **Possível duplicidade:** há semelhanças relevantes, mas faltam elementos para confirmar. Não mesclar nem excluir automaticamente; encaminhar para revisão.
- **Registros distintos:** há evidência de unidades, empresas ou estabelecimentos diferentes. Manter registros separados.

A decisão deve considerar a unidade física. Duas filiais da mesma marca em endereços diferentes não são duplicidades.

## 6. Atualização de registros correspondentes

Quando uma correspondência for confirmada:

1. manter o `id` existente;
2. preservar `dates.first_seen_at`;
3. atualizar apenas os campos sustentados por informação confiável mais recente;
4. acrescentar ou atualizar a fonte consultada;
5. atualizar `dates.last_checked_at`;
6. alterar `dates.last_updated_at` somente quando houver mudança efetiva nos dados;
7. registrar divergências que ainda precisem de revisão.

Não apagar dados válidos apenas porque uma nova fonte não os informa.

## 7. Casos que exigem cuidado

- **Mesmo nome, endereços diferentes:** tratar inicialmente como unidades distintas.
- **Mesmo endereço, nomes diferentes:** verificar se houve mudança de nome, ocupação do imóvel por outro negócio ou coexistência de estabelecimentos.
- **Mesmo telefone, nomes diferentes:** usar como indício, pois um contato pode atender mais de uma unidade ou marca.
- **Nome parecido, sem outros dados coincidentes:** não mesclar.
- **Mudança de endereço:** verificar se é o mesmo estabelecimento em novo local antes de atualizar o registro.
- **Negócio aparentemente encerrado:** não excluir. Alterar a situação somente quando houver evidência suficiente, mantendo o histórico de fontes e verificações.

## 8. Segurança e revisão

- Não contornar bloqueios, autenticação ou medidas técnicas das fontes para obter dados.
- Não usar dados pessoais sem necessidade para identificar um estabelecimento.
- Não expor CNPJ, telefone pessoal ou outros dados sensíveis sem pertinência e base adequada.
- Toda mesclagem deve manter as fontes que justificam os dados consolidados.
- Casos ambíguos permanecem pendentes até que exista evidência suficiente.

## 9. Resultado esperado

A base deve conter um registro por unidade comercial identificável, com identificador estável, fontes rastreáveis e o mínimo possível de duplicidades. A prioridade é evitar tanto registros repetidos quanto a fusão indevida de estabelecimentos diferentes.

## 10. Fora do escopo desta etapa

Este documento não define ainda algoritmo, pontuação automática, limiares numéricos, interface de revisão ou rotina de coleta. Esses mecanismos só devem ser implementados depois que os critérios conceituais forem validados.
