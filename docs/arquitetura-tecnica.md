# Arquitetura técnica inicial — DESCOM

**Status:** arquitetura inicial  
**Tecnologias:** Python, GitHub Actions e JSON  
**Primeiro território:** Núcleo Bandeirante — DF

## 1. Decisão técnica

O DESCOM será desenvolvido inicialmente em Python e executado pelo GitHub Actions. A base consolidada será armazenada em JSON no próprio repositório.

Essa combinação evita a necessidade de servidor próprio, banco de dados ou infraestrutura adicional nesta fase.

## 2. Responsabilidades

- **Python:** organizar a execução, processar candidatos, normalizar campos, comparar registros e validar a base.
- **GitHub Actions:** executar o programa manualmente durante os testes. O agendamento automático só será ativado depois que a coleta estiver validada.
- **JSON:** armazenar os estabelecimentos consolidados por Região Administrativa.
- **GitHub:** versionar código, documentação, dados e histórico de alterações.

## 3. Organização prevista do código

```text
Descom/
├── .github/
│   └── workflows/
│       └── descom.yml
├── data/
│   └── nucleo-bandeirante/
│       └── estabelecimentos.json
├── docs/
├── scripts/
│   ├── main.py
│   ├── config.py
│   ├── models.py
│   ├── normalize.py
│   ├── deduplicate.py
│   └── validate.py
└── requirements.txt
```

A estrutura poderá ser ajustada quando a primeira rotina real demonstrar necessidade. Não criar módulos sem função concreta.

## 4. Primeira fase de implementação

A primeira fase terá execução manual e controlada:

1. carregar as configurações da pesquisa;
2. ler a base JSON existente ou iniciar uma base vazia válida;
3. receber candidatos de fontes explicitamente permitidas;
4. normalizar e comparar os candidatos;
5. validar a estrutura e os campos;
6. gravar a base consolidada somente se todas as verificações passarem;
7. apresentar um resumo da execução.

A primeira versão não fará raspagem indiscriminada de sites nem tentará contornar limitações de acesso. Cada fonte terá método de consulta compatível com seus termos, condições e disponibilidade técnica.

## 5. Segurança de gravação

O programa deve validar o conteúdo antes de substituir a base. A gravação deverá ser feita de forma segura, evitando deixar um arquivo parcial caso a execução seja interrompida.

Se a validação falhar, a última versão válida deverá permanecer intacta.

## 6. Execução e publicação

Durante o desenvolvimento, o workflow será acionado manualmente. Não haverá agendamento recorrente nem publicação automática no site até que:

- as fontes estejam definidas e avaliadas;
- a qualidade da coleta seja verificada;
- deduplicação e atualização tenham sido testadas;
- a saída JSON esteja estável.

## 7. Pesquisa web e provedor

A descoberta inicial utiliza a Brave Search API por HTTPS, diretamente pela biblioteca padrão do Python (urllib). As consultas são segmentadas pelos nove grupos de atividade definidos em docs/estrategia-pesquisa.md e direcionadas ao Brasil, em português, com recorte textual do Núcleo Bandeirante/DF.

A credencial deve existir exclusivamente como GitHub Actions Secret com o nome BRAVE_API_KEY. Nunca inserir a chave no código, nos arquivos JSON, nos logs ou no repositório.

A pesquisa gera discovery-results.json como artefato temporário para revisão (retenção de sete dias). Os resultados contêm título, URL e descrição fornecida pelo mecanismo de busca. São candidatos de pesquisa, não cadastros verificados: não entram automaticamente em estabelecimentos.json e não alteram a base oficial.

A execução manual do workflow oferece duas ações: validate e search. A ação search exige o Secret BRAVE_API_KEY. A ação validate não depende dele.

A Brave informa preço de US$ 5 por mil consultas e crédito mensal de US$ 5 no plano Search. A ativação do serviço exige cadastro e cartão. Consultar os termos vigentes do provedor antes de ampliar volume ou reutilizar conteúdo em publicação.

## 8. Dependências

A implementação prioriza a biblioteca padrão do Python. A integração atual não exige pacote externo.

## 9. Fora do escopo inicial

Não implementar nesta fase painel administrativo, banco de dados, API pública, integração com MS Access, publicação no IIS, assinatura comercial ou expansão simultânea para várias regiões.
