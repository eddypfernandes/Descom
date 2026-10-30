(function () {
  "use strict";

  const arquivoDados = "../data/nucleo-bandeirante/estabelecimentos.json";
  const lista = document.getElementById("lista-estabelecimentos");
  const busca = document.getElementById("busca-estabelecimentos");
  const filtro = document.getElementById("filtro-categoria");
  const contador = document.getElementById("contador-estabelecimentos");
  const aviso = document.getElementById("aviso-demonstracao");
  const estadoVazio = document.getElementById("estado-vazio");

  let estabelecimentos = [];

  function textoSeguro(valor) {
    return String(valor ?? "").replace(/[&<>"']/g, function (caractere) {
      return {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
      }[caractere];
    });
  }

  function enderecoTexto(endereco) {
    if (!endereco || typeof endereco !== "object") return "Endereço não informado";
    return [
      endereco.street,
      endereco.number,
      endereco.neighborhood
    ].filter(Boolean).join(", ") || "Endereço não informado";
  }

  function preencherCategorias() {
    const categorias = [...new Set(
      estabelecimentos.map(item => item.category).filter(Boolean)
    )].sort((a, b) => a.localeCompare(b, "pt-BR"));

    filtro.innerHTML = '<option value="">Todas as categorias</option>' +
      categorias.map(categoria =>
        '<option value="' + textoSeguro(categoria) + '">' + textoSeguro(categoria) + '</option>'
      ).join("");
  }

  function renderizar() {
    const termo = busca.value.trim().toLocaleLowerCase("pt-BR");
    const categoria = filtro.value;

    const encontrados = estabelecimentos.filter(item => {
      const correspondeCategoria = !categoria || item.category === categoria;
      const conteudo = [item.name, item.category, item.description, enderecoTexto(item.address)]
        .filter(Boolean).join(" ").toLocaleLowerCase("pt-BR");
      return correspondeCategoria && conteudo.includes(termo);
    });

    contador.textContent = encontrados.length + (encontrados.length === 1 ? " estabelecimento" : " estabelecimentos");
    estadoVazio.classList.toggle("d-none", encontrados.length > 0);

    lista.innerHTML = encontrados.map(item => {
      const imagem = item.image && item.image.url;
      const visual = imagem
        ? '<img class="img-fluid rounded cartao-imagem w-100" src="' + textoSeguro(imagem) + '" alt="">'
        : '<div class="cartao-imagem">Imagem não disponível</div>';

      return '<div class="col-12 col-sm-6 col-lg-4">' +
        '<article class="cartao-estabelecimento p-3">' +
          visual +
          '<div class="pt-3">' +
            '<p class="cartao-categoria mb-2">' + textoSeguro(item.category || "Categoria não informada") + '</p>' +
            '<h2 class="h5 mb-2">' + textoSeguro(item.name || "Estabelecimento sem nome") + '</h2>' +
            '<p class="small texto-suave mb-0">' + textoSeguro(enderecoTexto(item.address)) + '</p>' +
          '</div>' +
        '</article>' +
      '</div>';
    }).join("");
  }

  async function iniciar() {
    try {
      const resposta = await fetch(arquivoDados, { cache: "no-store" });
      if (!resposta.ok) throw new Error("Não foi possível carregar a base JSON.");

      const dados = await resposta.json();
      estabelecimentos = Array.isArray(dados.establishments) ? dados.establishments : [];

      if (estabelecimentos.length === 0) {
        aviso.classList.remove("d-none");
      }

      preencherCategorias();
      renderizar();
    } catch (erro) {
      contador.textContent = "Dados indisponíveis";
      lista.innerHTML = '<div class="col-12"><div class="alert alert-warning mb-0">Não foi possível carregar os dados do DESCOM. Verifique a publicação do arquivo JSON.</div></div>';
      console.error(erro);
    }
  }

  busca.addEventListener("input", renderizar);
  filtro.addEventListener("change", renderizar);
  iniciar();
})();