# Formato dos dados — DESCOM

**Status:** especificação inicial  
**Formato:** JSON  
**Versão do formato:** 1.0

## 1. Objetivo

Definir uma estrutura única para os registros de estabelecimentos identificados pelo DESCOM. O arquivo será produzido pelo agente e poderá ser consumido pelo site GUIA COMERCIAL, sem exigir banco de dados nesta etapa.

O formato deve permitir incluir novos registros e atualizar informações existentes sem perder a origem dos dados nem a data de entrada original.

## 2. Organização do arquivo

O arquivo principal será um objeto JSON com metadados e uma lista de estabelecimentos:

```json
{
  "schema_version": "1.0",
  "generated_at": "2026-10-29T12:00:00Z",
  "region": "Núcleo Bandeirante",
  "uf": "DF",
  "establishments": []
}
```

- `schema_version`: versão desta estrutura de dados.
- `generated_at`: data e hora da geração do arquivo, em ISO 8601.
- `region` e `uf`: recorte territorial representado.
- `establishments`: registros encontrados e mantidos na base.

## 3. Estrutura de cada estabelecimento

Exemplo ilustrativo. Os valores são fictícios e servem apenas para demonstrar a estrutura:

```json
{
  "id": "descom-000001",
  "name": "Comércio Exemplo",
  "category": "Alimentação",
  "description": null,
  "address": {
    "street": "Avenida Exemplo",
    "number": "100",
    "complement": null,
    "neighborhood": "Núcleo Bandeirante",
    "city": "Brasília",
    "state": "DF",
    "postal_code": null
  },
  "contacts": {
    "phone": null,
    "whatsapp": null,
    "website": null,
    "email": null,
    "public_profile": null
  },
  "location": {
    "latitude": null,
    "longitude": null
  },
  "image": {
    "url": null,
    "source_url": null,
    "permission_status": "not_available"
  },
  "sources": [
    {
      "url": "https://exemplo.com.br",
      "type": "official_website",
      "checked_at": "2026-10-29T12:00:00Z"
    }
  ],
  "dates": {
    "first_seen_at": "2026-10-29T12:00:00Z",
    "last_checked_at": "2026-10-29T12:00:00Z",
    "last_updated_at": "2026-10-29T12:00:00Z"
  },
  "validation": {
    "status": "pending",
    "confidence": "low",
    "notes": null
  },
  "data_origin": "descom",
  "merchant_claim": {
    "claimed": false,
    "verified": false,
    "declared_at": null
  }
}
```

## 4. Regras dos campos

- `id`: identificador interno estável. Não deve mudar quando o registro for atualizado.
- `name`: nome comercial identificado.
- `category`: categoria principal do estabelecimento.
- `description`: descrição pública, somente quando houver informação confiável; caso contrário, `null`.
- `address`: componentes do endereço. Campos desconhecidos permanecem `null`; não completar por suposição.
- `contacts`: somente canais de contato publicamente divulgados e pertinentes ao estabelecimento.
- `location`: coordenadas numéricas quando obtidas de fonte confiável; caso contrário, `null`.
- `image`: referência de imagem apenas quando a origem e a permissão de uso forem compatíveis. Sem imagem autorizada, manter `url` como `null`; o site exibirá seu placeholder HTML/Bootstrap.
- `sources`: uma ou mais fontes que sustentam as informações. Cada fonte registra URL, tipo e data da consulta.
- `dates.first_seen_at`: primeira identificação do estabelecimento pelo DESCOM. **Não deve ser alterada em atualizações**, pois será usada para ordenar os registros recentes.
- `dates.last_checked_at`: última conferência das informações.
- `dates.last_updated_at`: última alteração efetiva do registro na base.
- `validation.status`: usar `verified`, `partial`, `pending` ou `inactive`.
- `validation.confidence`: usar `high`, `medium` ou `low`.
- `data_origin`: identifica a origem predominante do cadastro. Inicialmente, usar `descom` para dados coletados pelo agente e `merchant` para dados declarados pelo comerciante.
- `merchant_claim`: registra eventual reivindicação do cadastro. Reivindicação não significa vínculo confirmado; `verified` só muda para `true` após validação do vínculo com o estabelecimento.

## 5. Regras de atualização e integridade

1. Atualizar um estabelecimento existente preservando seu `id` e `first_seen_at`.
2. Não substituir informação conhecida por valor vazio ou `null` sem motivo documentado.
3. Manter as fontes que sustentam os dados e registrar novas consultas.
4. Quando houver divergência entre fontes, não escolher um valor por suposição: manter a situação pendente de revisão.
5. Não eliminar automaticamente possíveis duplicidades. Registros ambíguos devem ser encaminhados para revisão.
6. Dados declarados pelo comerciante devem ser identificados como tais, sem apagar a proveniência dos dados coletados pelo DESCOM.
7. A presença de um estabelecimento na base pública não o transforma em cliente nem inicia assinatura ou relação comercial.

## 6. Convenções técnicas

- Codificação UTF-8.
- JSON válido, sem comentários ou vírgulas sobrando.
- Datas e horários em ISO 8601.
- Coordenadas como números; informações desconhecidas como `null`.
- Listas sem registros devem ser representadas por `[]`.
- Não inserir senhas, tokens, dados privados ou informações pessoais desnecessárias.

## 7. Fora do escopo desta etapa

Esta especificação não define ainda a rotina de coleta, a frequência de execução, a publicação automática, o painel administrativo ou o processo comercial de reivindicação. Esses pontos serão tratados separadamente, quando necessário.
