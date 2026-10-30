# Módulo comercial — ambiente de desenvolvimento

Esta pasta contém a página provisória para desenvolver e homologar a apresentação comercial do GUIA COMERCIAL.

## Objetivo

Desenvolver e testar a interface no GitHub antes da adaptação para o include ASP Classic `/novo/includes/home_comercial.asp`.

## Tecnologias

- HTML5
- Bootstrap 5.3.3
- CSS
- JavaScript

## Dados

A página consome a base oficial em:

`../data/nucleo-bandeirante/estabelecimentos.json`

A base permanece sob responsabilidade do DESCOM. Não inserir dados fictícios nela.

## Testes

A página deve ser aberta por hospedagem HTTP, como GitHub Pages. O carregamento por `file://` pode bloquear a leitura do JSON pelo navegador.

## Estado

Primeira estrutura visual e leitura da base implementadas. O JSON oficial está vazio neste momento; a interface informa essa condição e apresenta o estado vazio.