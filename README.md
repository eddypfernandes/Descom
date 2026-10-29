# DESCOM — Desbravador Comercial

Agente autônomo de pesquisa, coleta, organização e atualização de informações públicas sobre estabelecimentos comerciais.

## Objetivo

Construir uma base organizada de estabelecimentos para alimentar o módulo comercial do GUIA COMERCIAL, começando pelo Núcleo Bandeirante (DF) e avançando gradualmente para outras regiões administrativas.

## Escopo inicial

- Pesquisar estabelecimentos em fontes públicas adequadas.
- Coletar e padronizar informações comerciais.
- Identificar e tratar registros duplicados.
- Validar dados de endereço e localização sempre que possível.
- Registrar fontes, datas e grau de confiança dos dados.
- Gerar arquivos estruturados para consumo pelo site.

## Princípios

- Não inventar nem completar informações sem fonte.
- Diferenciar dados coletados pelo agente de dados declarados ou confirmados pelo comerciante.
- Registrar a origem e a data de coleta das informações.
- Respeitar termos de uso das fontes, direitos de imagem e legislação aplicável.
- Não armazenar segredos, tokens ou dados pessoais desnecessários neste repositório.

## Estrutura

- `docs/`: documentação e decisões do projeto.
- `data/`: arquivos de dados gerados pelo agente.
- `scripts/`: código de coleta, tratamento e validação.
- `.github/workflows/`: futuras automações do GitHub Actions.

## Situação atual

Repositório inicial preparado. A estratégia de pesquisa, o formato definitivo dos dados e as automações serão definidos antes da implementação.

