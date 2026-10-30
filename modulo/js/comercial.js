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

      return '<div class="col-12 col-lg-4">' +
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


  let instanciaCarousel;

  function quantidadePorSlide() {
    return window.innerWidth >= 992 ? 3 : 1;
  }

  function renderizarCarousel(registros) {
    if (instanciaCarousel) {
      instanciaCarousel.dispose();
      instanciaCarousel = null;
    }
    if (!carouselConteudo || !contadorCarousel) return;

    const cards = (Array.isArray(registros) ? registros : []).slice(0, 10);
    const porSlide = quantidadePorSlide();
    contadorCarousel.textContent = cards.length + " de 10 registros";

    if (cards.length === 0) {
      carouselConteudo.innerHTML = '<div class="alert alert-light mb-0">Aguardando os primeiros registros da pesquisa.</div>';
      return;
    }

    const grupos = [];
    for (let i = 0; i < cards.length; i += porSlide) {
      grupos.push(cards.slice(i, i + porSlide));
    }

    const slides = grupos.map((grupo, indice) => {
      const cardsHtml = grupo.map((item, posicao) => {
        const descricao = item.description || "Descrição ainda não disponível.";
        const regiao = item.address && item.address.neighborhood
          ? item.address.neighborhood + " · DF"
          : "Região em identificação";
        const numero = String(indice * porSlide + posicao + 1).padStart(2, "0");
        const imagemUrl = item.image && item.image.url;
        const imagem = imagemUrl
          ? '<img class="descom-card-imagem" src="' + textoSeguro(imagemUrl) + '" alt="' + textoSeguro(item.name || "Imagem do estabelecimento") + '" loading="lazy">'
          : '<div class="descom-card-imagem descom-card-imagem-vazia" aria-hidden="true"></div>';

        return '<div class="col-12 col-sm-6 col-lg-4">' +
          '<article class="descom-card h-100">' +
            imagem +
            '<div class="descom-card-topo">' +
              '<span class="descom-card-numero">' + numero + '</span>' +
              '<span class="descom-card-status">Em análise</span>' +
            '</div>' +
            '<div class="descom-card-corpo">' +
              '<p class="descom-card-categoria">' + textoSeguro(item.category || "Categoria não identificada") + '</p>' +
              '<h3 class="descom-card-titulo">' + textoSeguro(item.name || "Nome não identificado") + '</h3>' +
              '<p class="descom-card-descricao">' + textoSeguro(descricao) + '</p>' +
            '</div>' +
            '<div class="descom-card-rodape">' +
              '<span>' + textoSeguro(regiao) + '</span>' +
            '</div>' +
          '</article>' +
        '</div>';
      }).join("");

      return '<div class="carousel-item' + (indice === 0 ? ' active' : '') + '">' +
        '<div class="row g-3">' + cardsHtml + '</div>' +
      '</div>';
    }).join("");

    const controles = grupos.length > 1
      ? '<div class="descom-carousel-controles">' +
          '<button class="descom-carousel-seta" type="button" data-bs-target="#carouselEmpresas" data-bs-slide="prev" aria-label="Registros anteriores">←</button>' +
          '<button class="descom-carousel-seta" type="button" data-bs-target="#carouselEmpresas" data-bs-slide="next" aria-label="Próximos registros">→</button>' +
        '</div>'
      : "";

    carouselConteudo.innerHTML =
      '<div id="carouselEmpresas" class="carousel slide" data-bs-ride="carousel" data-bs-interval="5000" data-bs-pause="false">' +
        '<div class="carousel-inner">' + slides + '</div>' +
        controles +
      '</div>';

    const elementoCarousel = document.getElementById("carouselEmpresas");
    if (elementoCarousel && grupos.length > 1) {
      instanciaCarousel = new bootstrap.Carousel(elementoCarousel, {
        interval: 5000,
        pause: false,
        ride: "carousel",
        touch: true,
        wrap: true
      });
      instanciaCarousel.cycle();
    }
  }

  let temporizadorRedimensionamento;
  window.addEventListener("resize", function () {
    window.clearTimeout(temporizadorRedimensionamento);
    temporizadorRedimensionamento = window.setTimeout(function () {
      renderizarCarousel(estabelecimentos);
    }, 180);
  });

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
      renderizarCarousel(estabelecimentos);
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