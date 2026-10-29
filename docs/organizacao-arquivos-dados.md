# Organização dos arquivos de dados — DESCOM

**Status:** proposta inicial  
**Escopo:** organização dos arquivos gerados pelo agente

## 1. Princípio

Manter a organização simples: um arquivo principal de estabelecimentos por Região Administrativa (RA), reunindo todas as categorias daquela região.

Não separar os estabelecimentos em arquivos por categoria. A categoria já é um campo de cada registro e poderá ser usada pelo site para filtros, buscas e módulos.

## 2. Estrutura inicial

Para a primeira etapa, dedicada ao Núcleo Bandeirante:

```text
data/
└── nucleo-bandeirante/
    └── estabelecimentos.json
```

O arquivo `estabelecimentos.json` seguirá integralmente a estrutura definida em `docs/formato-dados-json.md`.

Quando outra RA entrar no projeto, será criada uma pasta própria:

```text
data/
├── nucleo-bandeirante/
│   └── estabelecimentos.json
├── candangolandia/
│   └── estabelecimentos.json
└── riacho-fundo/
    └── estabelecimentos.json
```

Os exemplos de outras regiões representam apenas a expansão futura; não significam que essas regiões já estejam em coleta.

## 3. Regras de organização

1. Cada RA terá um único arquivo consolidado de estabelecimentos.
2. Todas as categorias da RA ficarão no mesmo arquivo.
3. Cada registro manterá seu identificador estável.
4. Atualizações substituirão o conteúdo consolidado da RA, preservando os registros e datas originais conforme as regras do formato JSON.
5. O agente não deverá criar um novo arquivo por execução.
6. O nome da pasta será uma versão simplificada da RA, sem acentos e com palavras separadas por hífen.
7. O nome do arquivo principal será sempre `estabelecimentos.json`.

## 4. Histórico de execução

Nesta etapa, não será criado um histórico separado de arquivos, cópias datadas ou snapshots a cada execução. O próprio registro mantém as datas de identificação e verificação, e os metadados do arquivo informam quando ele foi gerado.

O histórico de alterações do repositório GitHub já oferece rastreabilidade das versões publicadas. Uma estrutura adicional de logs poderá ser definida futuramente se a operação demonstrar essa necessidade.

## 5. Consumo pelo GUIA COMERCIAL

O site poderá consultar o arquivo da RA desejada e aplicar filtros por categoria, situação de validação ou outros campos disponíveis.

A estrutura não determina ainda como será feita a importação para o MS Access nem a frequência de atualização do site. Essas decisões ficam para uma etapa posterior.

## 6. Primeira entrega

A primeira saída estruturada do DESCOM deverá ser:

`data/nucleo-bandeirante/estabelecimentos.json`

O arquivo só deverá ser preenchido com registros coletados e avaliados pelo agente. Não utilizar dados fictícios como conteúdo operacional.
