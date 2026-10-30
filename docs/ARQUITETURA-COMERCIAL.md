# Arquitetura do módulo Comercial — Guia Comercial

**Status:** planejamento estrutural  
**Projeto:** Guia Comercial — início pelo Núcleo Bandeirante/DF  
**Stack de produção:** HTML5, Bootstrap 5.3.3, ASP Clássico e Microsoft Access  
**Protótipo atual:** HTML + JavaScript + JSON no GitHub Pages

## 1. Objetivo

O módulo Comercial será o produto de descoberta e divulgação de empresas do Guia Comercial. Ele terá três áreas integradas:

1. **Público:** pesquisa e descoberta de estabelecimentos.
2. **Comerciante:** gestão da própria presença comercial e da assinatura.
3. **Administração:** gestão editorial, cadastros, planos, cobranças e indicadores.

O catálogo público é a porta de entrada. A receita recorrente virá dos recursos e serviços oferecidos ao comerciante.

## 2. Mapa de páginas

### Área pública — /comercial/

| Página | Responsabilidade |
|---|---|
| `index.asp` | Catálogo, pesquisa, categorias, ordenação e paginação |
| `empresa.asp?id=` | Perfil público individual do estabelecimento |
| `categoria.asp? id=` | Listagem filtrada por categoria |
| `busca.asp?q=` | Resultados de pesquisa |
| `anuncie.asp` | Apresentação das modalidades comerciais |
| `planos.asp` | Comparação de planos e recursos |
| `contato.asp` | Canal de contato comercial |

### Área do comerciante — /comercial/cliente/

| Página | Responsabilidade |
|---|---|
| `index.asp` | Visão geral e indicadores da conta |
| `acesso.asp` | Entrada e recuperação de acesso |
| `estabelecimento.asp` | Dados, endereço e contatos |
| `apresentacao.asp` | Descrição, fotos e apresentação |
| `divulgacao.asp` | Recursos promocionais disponíveis |
| `reputacao.asp` | Avaliações e respostas |
| `resultados.asp` | Visualizações e interações |
| `assinatura.asp` | Plano, situação e histórico |
| `pagamentos.asp` | Cobranças e comprovantes |

### Administração — /admin/comercial/

| Página | Responsabilidade |
|---|---|
| `index.asp` | Painel geral |
| `estabelecimentos.asp` | Cadastro, revisão, confirmação e publicação |
| `comerciantes.asp` | Contas e vínculos com estabelecimentos |
| `categorias.asp` | Categorias e organização |
| `planos.asp` | Planos, preços e recursos |
| `assinaturas.asp` | Contratos, vencimentos e situação |
| `financeiro.asp` | Receitas, cobranças e inadimplência |
| `anuncios.asp` | Destaques e campanhas |
| `avaliacoes.asp` | Moderação de avaliações |
| `relatorios.asp` | Indicadores e relatórios |

## 3. Estrutura sugerida de arquivos

```text
/comercial/
  index.asp
  empresa.asp
  categoria.asp
  busca.asp
  anuncie.asp
  planos.asp
  /cliente/
    index.asp
    acesso.asp
    estabelecimento.asp
    apresentacao.asp
    divulgacao.asp
    reputacao.asp
    resultados.asp
    assinatura.asp
    pagamentos.asp
  /includes/
    topo.asp
    menu.asp
    busca.asp
    filtros.asp
    card_estabelecimento.asp
    paginacao.asp
    rodape.asp
    conexao.asp
    funcoes.asp
  /css/
    estilos.css
  /js/
    comercial.js

/admin/comercial/
  index.asp
  estabelecimentos.asp
  comerciantes.asp
  categorias.asp
  planos.asp
  assinaturas.asp
  financeiro.asp
  anuncios.asp
  avaliacoes.asp
  relatorios.asp
  /includes/
  /css/
  /js/
```

A estrutura é uma referência de implementação. Os arquivos serão criados por etapa, conforme cada tela for necessária; não criar páginas vazias antecipadamente.

## 4. Ciclo de vida do estabelecimento

1. **Descoberto:** registro coletado pelo DESCOM, ainda não confirmado.
2. **Em análise:** dados aguardam revisão e tratamento de inconsistências.
3. **Publicado:** cadastro aprovado para aparecer no catálogo.
4. **Reivindicado:** comerciante solicitou vínculo com o estabelecimento.
5. **Confirmado:** vínculo e informações do responsável foram verificados.
6. **Completo:** comerciante complementou a apresentação e os dados disponíveis.

A descoberta automática nunca equivale à confirmação do comerciante. O sistema deve preservar a origem, as fontes, as datas e o nível de confiança dos dados.

## 5. Planos e monetização

Os planos devem ser configuráveis no painel administrativo. Não fixar preços, limites ou permissões diretamente nas páginas.

Modalidades iniciais a avaliar:

- **Gratuito:** presença básica no catálogo.
- **Essencial:** perfil ampliado e informações adicionais.
- **Profissional:** ferramentas adicionais de apresentação e divulgação.
- **Destaque:** exposição promocional em espaços definidos do Guia.

A matriz definitiva de recursos, preços, limites e regras será aprovada antes da implementação das assinaturas.

## 6. Indicadores comerciais

Registrar eventos de forma consistente para permitir relatórios confiáveis, por exemplo:

- visualização do perfil;
- clique em telefone ou WhatsApp;
- acesso ao site;
- consulta de endereço ou rota;
- interação com campanha ou destaque.

Relatórios devem distinguir visualizações de ações efetivas. Não apresentar números estimados como resultados reais.

## 7. Diretrizes técnicas

- Bootstrap 5.3.3 como base visual; priorizar componentes nativos.
- Produção em ASP Clássico e Microsoft Access, conforme arquitetura do Guia.
- Cada include responsável por dados abre e fecha seu próprio recordset.
- Página pai sem recordsets.
- Consultas parametrizadas e validação de entradas.
- Controle de acesso no servidor; esconder links não é controle de segurança.
- Senhas armazenadas com hash apropriado; nunca em texto puro.
- Separar dados descobertos pelo DESCOM de declarações feitas pelo comerciante.
- Manter histórico de alterações importantes, assinaturas e operações financeiras.
- Não integrar cobrança real antes de definir provedor, fluxo de conciliação e regras de cancelamento.

## 8. Ordem de execução

1. Consolidar o catálogo público e a leitura do JSON.
2. Definir e implementar o perfil individual do estabelecimento.
3. Implementar solicitação de vínculo e confirmação do comerciante.
4. Construir autenticação e área do comerciante.
5. Definir matriz de planos e recursos.
6. Implementar assinaturas e controle financeiro.
7. Implementar métricas e relatórios.
8. Finalizar painel administrativo e rotinas de operação.

## 9. Limites do protótipo atual

O GitHub Pages atual é um ambiente de demonstração estática. Ele permite validar interface e leitura do JSON, mas não substitui o ambiente de produção ASP/Access. Autenticação, persistência, pagamentos, permissões e operações administrativas deverão ser implementados no servidor de hospedagem.

**Regra de evolução:** preservar as telas aprovadas e implementar somente a etapa em andamento, sem antecipar funcionalidades que dependam de decisões ainda não tomadas.
