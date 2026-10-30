(function () {
  "use strict";

  const arquivoDados = "data/nucleo-bandeirante/estabelecimentos.json";
  const lista = document.getElementById("lista-estabelecimentos");
  const busca = document.getElementById("busca-estabelecimentos");
  const filtro = document.getElementById("filtro-categoria");
  const contador = document.getElementById("contador-estabelecimentos");
  const aviso = document.getElementById("aviso-demonstracao");
  const estadoVazio = document.getElementById("estado-vazio");
  const carouselConteudo = document.getElementById("carousel-empresas-conteudo");
  const contadorCarousel = document.getElementById("contador-carousel");

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


  function renderizarCarousel(cards) {
    if (!carouselConteudo || !contadorCarousel) return;
    const validos = Array.isArray(cards) ? cards : [];
    contadorCarousel.textContent = validos.length + (validos.length === 1 ? " empresa" : " empresas");

    if (validos.length < 10) {
      carouselConteudo.innerHTML = '<div class="alert alert-light border mb-0">O DESCOM ainda está reunindo empresas verificáveis para completar os 10 cards. Nenhuma empresa foi inventada.</div>';
      return;
    }

    const grupos = [];
    for (let i = 0; i < validos.length; i += 3) grupos.push(validos.slice(i, i + 3));
    const slides = grupos.map((grupo, indice) => {
      const cardsHtml = grupo.map(item => {
        const endereco = enderecoTexto(item.address);
        return '<div class="col-12 col-md-4"><article class="cartao-estabelecimento h-100 p-3">' +
          '<p class="cartao-categoria mb-2">' + textoSeguro(item.category || "Comércio e serviços") + '</p>' +
          '<h3 class="h5 mb-2">' + textoSeguro(item.name || "Empresa") + '</h3>' +
          '<p class="small texto-suave mb-2">' + textoSeguro(endereco) + '</p>' +
          '<p class="small texto-suave mb-0">' + textoSeguro(item.description || "Informações públicas em processo de organização.") + '</p>' +
          '</article></div>';
      }).join("");
      return '<div class="carousel-item' + (indice === 0 ? ' active' : '') + '"><div class="row g-3">' + cardsHtml + '</div></div>';
    }).join("");

    carouselConteudo.innerHTML =
      '<div id="carouselEmpresas" class="carousel slide" data-bs-ride="false">' +
        '<div class="carousel-inner">' + slides + '</div>' +
        '<div class="d-flex justify-content-end gap-2 mt-3">' +
          '<button class="btn btn-outline-secondary rounded-circle" type="button" data-bs-target="#carouselEmpresas" data-bs-slide="prev" aria-label="Empresas anteriores"><span aria-hidden="true">&lsaquo;</span></button>' +
          '<button class="btn btn-outline-secondary rounded-circle" type="button" data-bs-target="#carouselEmpresas" data-bs-slide="next" aria-label="Próximas empresas"><span aria-hidden="true">&rsaquo;</span></button>' +
        '</div>' +
      '</div>';
  }

  async function carregarCarousel() {
    try {
      const resposta = await fetch("carousel/empresas-carousel.json", { cache: "no-store" });
      if (!resposta.ok) throw new Error("Arquivo do carousel indisponível.");
      const dados = await resposta.json();
      renderizarCarousel(dados.cards);
    } catch (erro) {
      if (carouselConteudo) carouselConteudo.innerHTML = '<div class="alert alert-light border mb-0">O carousel será exibido assim que a primeira coleta do DESCOM for publicada.</div>';
      if (contadorCarousel) contadorCarousel.textContent = "Aguardando coleta";
    }
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