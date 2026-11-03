# Fonte de descoberta — primeira versão do DESCOM

**Decisão:** usar o OpenStreetMap por meio do Overpass API como fonte automatizada inicial, sem chave e sem cobrança por consulta. O Google Maps permanece como referência de conferência manual, sem raspagem automatizada.

## Por que esta escolha

O projeto não utilizará Google Places API nesta fase por envolver configuração de faturamento e cobrança por uso. Também não automatizará a extração do Google Maps, nem contornará autenticação, limites ou mecanismos de proteção.

O Overpass é um serviço público de consulta somente leitura aos dados do OpenStreetMap. Não exige chave de API, mas possui limites de capacidade e disponibilidade; o DESCOM deve executar consultas moderadas, identificando-se no User-Agent e evitando varreduras excessivas.

## O que a primeira versão faz

1. Consulta a área administrativa do Núcleo Bandeirante no OpenStreetMap (relação OSM 3359475).
2. Localiza elementos nomeados com tags comerciais e de serviços.
3. Captura nome, categoria, endereço, contatos e coordenadas existentes.
4. Mantém o identificador original do elemento OSM para atualizar o mesmo registro nas execuções seguintes.
5. Sinaliza possíveis coincidências exatas com a base histórica.
6. Gera data/nucleo-bandeirante/descobertas.json.
7. Mantém os resultados fora do carrossel até conferência.

## O que não afirma

- Não afirma que o estabelecimento foi inaugurado recentemente. first_seen_at significa primeira descoberta pelo DESCOM.
- Não afirma que todos os estabelecimentos da região estão mapeados.
- Não trata o centro de uma área (way/relation) como endereço exato da porta.
- Não publica automaticamente dados recém-descobertos.
- Não inventa endereço, telefone, imagem ou coordenadas ausentes.

## Licença

Os dados do OpenStreetMap estão sob ODbL. A utilização e a distribuição devem respeitar a licença, incluindo atribuição e obrigações aplicáveis a bases derivadas. A página oficial de direitos autorais e licença é https://www.openstreetmap.org/copyright. Para a atribuição em produtos públicos, consultar também https://osmfoundation.org/wiki/Attribution_Guidelines.

A base histórica estabelecimentos.json não é sobrescrita pelo novo coletor. As novas descobertas são mantidas em arquivo separado até a avaliação de cobertura, qualidade e compatibilidade de licenças.
