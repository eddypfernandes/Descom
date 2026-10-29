# Validação e confiabilidade dos dados — DESCOM

**Status:** critérios iniciais  
**Escopo:** avaliar a qualidade das informações coletadas e definir quando um registro pode ser considerado verificado.

## 1. Princípio

O DESCOM não deve confundir informação encontrada com informação confirmada. Cada campo precisa ter uma fonte identificável, e o estado geral do estabelecimento deve refletir a qualidade das evidências disponíveis.

A validação é gradual: um registro pode ser útil mesmo quando ainda não está completo. Informações ausentes devem permanecer como desconhecidas, sem serem preenchidas por suposição.

## 2. Estados de validação

O campo `validation.status` definido no formato JSON deve utilizar:

- `verified`: identidade do estabelecimento e informações essenciais confirmadas por evidências confiáveis e coerentes.
- `partial`: estabelecimento identificado, mas um ou mais dados essenciais ainda não foram confirmados ou apresentam lacunas.
- `pending`: evidências insuficientes, conflitantes ou ainda não avaliadas.
- `inactive`: há evidência confiável de que o estabelecimento encerrou as atividades ou deixou de operar naquele endereço.

Um registro `inactive` não deve ser apagado automaticamente. Sua permanência ajuda a evitar que seja redescoberto como novo em pesquisas futuras.

## 3. Níveis de confiança

O campo `validation.confidence` deve utilizar:

- `high`: evidências diretas, atuais e coerentes, preferencialmente provenientes de fonte oficial do estabelecimento ou fonte pública institucional confiável.
- `medium`: informações coerentes sustentadas por fontes públicas identificáveis, mas sem confirmação direta suficiente.
- `low`: informação isolada, incompleta, antiga ou com incerteza relevante.

O nível de confiança complementa o estado de validação. Não substitui a análise dos campos individuais nem deve ser usado isoladamente para afirmar que todos os dados estão corretos.

## 4. Avaliação por informação

Sempre que possível, a origem e a data de verificação devem ser associadas ao dado correspondente por meio das fontes registradas.

### Identidade e nome comercial
Confirmar que a fonte se refere ao estabelecimento ou à unidade física identificada. Nome encontrado apenas em menção indireta não é suficiente para confirmação plena.

### Endereço
Priorizar página oficial, cadastro público pertinente ou fonte que identifique claramente a unidade. Endereço aproximado ou referência de mapa sem confirmação deve permanecer com validação parcial ou pendente.

### Telefone e WhatsApp
Registrar somente contatos divulgados publicamente para atendimento do estabelecimento. A existência do número em uma página não comprova, por si só, que ele continua ativo.

### Site e perfis públicos
Verificar se a página pertence ao estabelecimento e se identifica a unidade ou marca de maneira consistente. Não tratar páginas de terceiros como canais oficiais.

### Coordenadas
Usar coordenadas associadas ao endereço correto. Proximidade do ponto no mapa é indício, não confirmação isolada de endereço ou identidade.

### Situação de funcionamento
Não classificar um estabelecimento como inativo apenas por ausência de atualização, falta de resposta, horário não confirmado ou página fora do ar. Exigir evidência razoável de encerramento ou mudança.

## 5. Hierarquia orientativa de fontes

A força da fonte depende do dado que está sendo avaliado. Como orientação geral:

1. Site ou canal oficial do próprio estabelecimento, quando claramente identificado.
2. Cadastro ou publicação de órgão público competente, para os dados que esse órgão efetivamente atesta.
3. Associação comercial ou entidade institucional identificável.
4. Diretório ou plataforma pública que identifique claramente o estabelecimento e a unidade.
5. Publicação pública de terceiros, notícias ou redes sociais, como evidência complementar.

Uma fonte oficial pode estar desatualizada. A data, a coerência com outras fontes e o tipo de informação continuam relevantes.

## 6. Critério mínimo para o estado verificado

O DESCOM só deve utilizar `verified` quando:

- a identidade do estabelecimento e da unidade estiver suficientemente clara;
- houver evidência confiável para o nome comercial e o endereço;
- não existirem divergências relevantes sem resolução;
- as fontes e datas de consulta estiverem registradas;
- a classificação não depender de informação presumida.

A ausência de telefone, site, imagem ou coordenadas não impede, por si só, a verificação da identidade e do endereço. Esses campos podem permanecer como `null`.

## 7. Atualidade das informações

Cada nova consulta deve atualizar `dates.last_checked_at`, mesmo quando não houver alteração nos dados.

A data `dates.last_updated_at` só muda quando o conteúdo do registro for efetivamente alterado. A data `dates.first_seen_at` nunca deve ser redefinida por uma atualização.

Informações antigas não devem ser tratadas automaticamente como falsas, mas sua atualidade precisa ser considerada antes de classificá-las como verificadas.

## 8. Conflitos e revisão

Quando duas fontes confiáveis apresentarem dados incompatíveis:

- não escolher automaticamente uma delas;
- preservar as fontes e os valores relevantes para análise;
- manter o registro como `pending` ou `partial`, conforme o caso;
- registrar a divergência em `validation.notes`;
- reavaliar quando houver evidência adicional.

O agente não deve apagar ou sobrescrever silenciosamente informações cuja divergência ainda não foi resolvida.

## 9. Limites da validação

A validação do DESCOM se refere à consistência das informações públicas coletadas. Ela não representa certificação de qualidade, recomendação comercial, avaliação de reputação, licença de funcionamento ou garantia de que o negócio está aberto naquele exato momento.

A presença na base pública não significa que o estabelecimento seja cliente, tenha autorizado publicidade ou tenha reivindicado seu cadastro.

## 10. Fora do escopo desta etapa

Este documento não define ainda pontuação matemática, prazos fixos de expiração, consultas automáticas a serviços pagos ou revisão humana em painel. Esses mecanismos só serão avaliados quando houver necessidade operacional comprovada.
