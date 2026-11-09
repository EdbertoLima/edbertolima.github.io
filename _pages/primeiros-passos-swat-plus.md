---
title: "Primeiros passos com o SWAT+: o que todo iniciante precisa saber"
excerpt: "Um guia prático para começar a modelar bacias hidrográficas com o SWAT+, baseado no minicurso que ministrei na SNCT 2026 do IFBA, em Vitória da Conquista."
tags:
  - SWAT+
  - modelagem hidrológica
  - QGIS
  - português
toc: true
toc_sticky: true
lang: pt-BR
permalink: /primeiros-passos-swat-plus/
read_time: true
---

**Versão em português** do post [First steps with SWAT+](/swat-plus-first-steps/) (original em inglês).
{: .notice--info}

Nos dias 14 e 15 de outubro de 2026, das 8h às 12h, ministrei o minicurso **"Introdução ao
SWAT+ para iniciantes"** na Semana Nacional de Ciência e Tecnologia (SNCT 2026) do IFBA, campus
Vitória da Conquista: 8 horas, em duas manhãs, para estudantes e profissionais sem experiência prévia com o SWAT. Este texto
reúne os principais pontos abordados no curso e dicas para continuar aprendendo depois dele. É um
bom ponto de partida para quem está começando: indica o caminho e as dificuldades mais frequentes
nos primeiros passos com o SWAT+.

<figure>
  <img src="/assets/images/posts/swat-course-snct-2026.jpg" alt="Participantes do minicurso de SWAT+ no laboratório de geoprocessamento do IFBA, com o instrutor na tela de projeção">
  <figcaption>Turma do minicurso MC07 na SNCT 2026 do IFBA, em Vitória da Conquista. Ministrei o curso remotamente, da Áustria (na projeção).</figcaption>
</figure>

## O que é o SWAT+

O **SWAT+** (*Soil and Water Assessment Tool Plus*) é um modelo hidrológico de bacia
hidrográfica **contínuo** (passo de tempo diário), **semidistribuído** e **baseado em processos**: a maior
parte dos parâmetros deriva do solo, do uso e cobertura da terra e do relevo e tem significado
físico, embora alguns componentes sejam empíricos (por exemplo, o método da Curva-Número para o
escoamento superficial). O
modelo estima vazão, balanço hídrico, produção de sedimentos e transporte de nutrientes, e permite
avaliar cenários de manejo, de uso da terra e de mudanças climáticas.

<figure>
  <img src="/assets/images/posts/usgs-ciclo-da-agua.jpg" alt="Diagrama do ciclo da água do USGS em português, com reservatórios e fluxos de água">
  <figcaption>O ciclo da água. Fonte: <a href="https://www.usgs.gov/special-topics/water-science-school/o-ciclo-da-agua-water-cycle-portuguese">USGS Water Science School</a>, tradução de Marcio Baldissera Cure (UFSC); domínio público.</figcaption>
</figure>

O SWAT+ é uma reestruturação completa do SWAT 2012, desenvolvida pelo USDA-ARS e pela Texas A&M
University ([Bieger et al., 2017](https://doi.org/10.1111/1752-1688.12482)). A maior parte das equações que descrevem os
processos vem do SWAT 2012 (Neitsch et al., 2011); muda a forma como a bacia é organizada:

| Aspecto | SWAT 2012 | SWAT+ |
| --- | --- | --- |
| Interface SIG | ArcSWAT (ArcGIS, licença paga) ou QSWAT | QSWAT+ (QGIS, gratuito) |
| Banco de dados | Microsoft Access | SQLite |
| Conexão entre unidades | Arquivo `fig.fig`, de estrutura fixa | Arquivos de conexão (`.con`), flexíveis |
| Discretização espacial | Bacia, sub-bacias e HRUs | Bacia, sub-bacias, unidades de paisagem (LSUs), HRUs e corpos d'água |
| Manejo | Operações agendadas por data ou por unidades de calor | Também por tabelas de decisão |
| Calibração | Altera os arquivos de entrada | O arquivo `calibration.cal` aplica as alterações sem modificar os originais |

A unidade básica de cálculo continua sendo a **unidade de resposta hidrológica** (HRU, de
*hydrologic response unit*): uma combinação única de unidade de paisagem, uso da terra, tipo de
solo e classe de declividade. A HRU não é uma área geograficamente contínua; ela corresponde ao
conjunto de todas as células que têm a mesma combinação.

## Três programas, um modelo

A primeira fonte de confusão é que o SWAT+ é, na prática, um conjunto de três programas:

| Componente | Função |
| --- | --- |
| **QSWAT+** (complemento do QGIS) | Prepara a parte espacial: delimita a bacia, gera as LSUs e as HRUs e visualiza os resultados. **Não é o modelo.** |
| **SWAT+ Editor** | Importa os dados climáticos, define o período de simulação, as opções e as saídas, escreve os arquivos de entrada e executa o modelo |
| **SWAT+** (executável) | O modelo propriamente dito: lê os arquivos de texto da pasta `TxtInOut` e grava as saídas |

Os três são instalados pelo [instalador oficial do SWAT+](https://swatplus.gitbook.io/docs/installation).
O código-fonte do modelo está arquivado no Zenodo (Arnold et al., 2026).
Use o **QGIS LTR de 64 bits**, versão testada pelos desenvolvedores, e marque, durante a
instalação, o download do gerador climático global.

## Dados de entrada: o que é necessário e onde obter no Brasil

Um modelo básico requer cinco conjuntos de dados, **todos no mesmo sistema de coordenadas
projetado (em metros)**:

| Dado | Finalidade | Fontes para o Brasil |
| --- | --- | --- |
| Modelo digital de elevação (MDE) | Rede de drenagem, sub-bacias e declividade | [ANADEM](https://doi.org/10.3390/rs16132321), Copernicus GLO-30, SRTM 30 m, TOPODATA (INPE) |
| Uso e cobertura da terra | Tipo de vegetação, Curva-Número (CN) e manejo de cada HRU | [MapBiomas](https://brasil.mapbiomas.org/) (coleções anuais, 30 m) |
| Solos | Camadas, textura, água disponível, condutividade hidráulica | Mapas pedológicos do IBGE e da Embrapa; SoilGrids para complementar propriedades |
| Clima diário | Precipitação, temperatura, radiação solar, umidade relativa e vento | INMET (BDMEP), Hidroweb (ANA), grade BR-DWGD, CHIRPS, ERA5 |
| Vazão observada | Avaliação, calibração e validação | Hidroweb / SNIRH (ANA) |

Para a delimitação da bacia, prefira um **modelo digital de terreno** como o ANADEM
([Laipelt et al., 2024](https://doi.org/10.3390/rs16132321)), que reduz o viés da vegetação do Copernicus GLO-30: modelos
de superfície, como o SRTM e o Copernicus, incluem parte da altura do dossel, o que pode deslocar a rede
de drenagem em áreas florestadas.

Na prática, o dado mais difícil de montar é quase sempre a **tabela de atributos dos solos**
(*usersoil*): profundidade, densidade do solo, água disponível e condutividade hidráulica saturada
de cada horizonte.

Dois cuidados evitam boa parte dos erros:

- O QSWAT+ considera que **todas as células têm a mesma área**. Um MDE em coordenadas geográficas
  (graus) precisa ser reprojetado antes do uso; no Brasil, utilize SIRGAS 2000 / UTM no fuso da
  bacia ou, para bacias que atravessam fusos, uma projeção equivalente (de áreas iguais).
- Nomes de pastas e arquivos **sem espaços, acentos ou caracteres especiais**.

**Lições de uma aplicação real com dados brasileiros:**

- **Vazão do Hidroweb:** utilize apenas a série consistida (nível de consistência 2) e verifique o
  *status* de cada dia (1 real, 2 estimado, 3 duvidoso, 4 régua seca). Em algumas estações, há anos inteiros apenas com
  valores estimados; avalie o desempenho do modelo nos dias com dado real. O
  [CAMELS-BR](https://doi.org/10.5194/essd-12-2075-2020) é uma boa referência para verificação
  cruzada.
- **Os metadados das estações nem sempre são confiáveis:** áreas de drenagem podem estar
  incorretas e coordenadas antigas podem estar arredondadas. Compare a área informada com a da bacia
  delimitada.
- **A precipitação em grade do BR-DWGD** ([Xavier et al., 2022](https://doi.org/10.1002/joc.7731)),
  nesse projeto, concordou com os pluviômetros em totais e na distribuição temporal, mas apresentou dias com chuva
  fraca em excesso e poucos eventos intensos. Com o método da Curva-Número, isso reduz o
  escoamento superficial simulado, e a calibração acaba mascarando o problema. Antes de usar a
  grade, compare a frequência de dias chuvosos e de eventos intensos com estações pluviométricas
  da ANA.
- **As janelas de semeadura do Zoneamento Agrícola de Risco Climático (ZARC)** indicam os períodos
  aceitos pelo seguro agrícola, não a prática observada. Para as datas efetivas de semeadura,
  consulte o acompanhamento de safra da Conab; para avaliar o crescimento das culturas, compare a
  produtividade simulada com a Produção Agrícola Municipal (PAM/IBGE).

## Checklist antes de abrir o QSWAT+

Meia hora de verificação nesta etapa economiza horas depois:

- [ ] MDE, uso da terra e solos estão no mesmo sistema de coordenadas projetado
- [ ] A unidade vertical do MDE é o metro
- [ ] Os mapas de uso e de solos cobrem toda a bacia, sem falhas (*NoData*)
- [ ] Todo valor do raster de uso tem correspondência na tabela de uso; uma classe desconhecida
      deve interromper o processamento, e não ser convertida em pastagem por padrão
- [ ] Todo valor do raster de solos tem correspondência na tabela de solos, e todo solo consta
      no *usersoil*
- [ ] O exutório está sobre a rede de drenagem gerada (ou a menos de 300 m dela)
- [ ] A série climática cobre o período de simulação mais o período de aquecimento
- [ ] As coordenadas das estações estão em graus decimais, com sinal negativo para Sul e Oeste
- [ ] Um projeto de exemplo reaproveitado não traz um arquivo `calibration.cal` esquecido

## O fluxo de trabalho em seis etapas

1. **Criar o projeto** no QSWAT+ (botão SWAT+ no QGIS, *New Project*).
2. **Delimitar a bacia:** carregar o MDE, definir os limiares de área de contribuição para canais
   e cursos d'água (limiares menores geram mais sub-bacias e um modelo mais lento) e indicar o
   exutório. Defina os limiares de forma consciente, pois os valores padrão dependem do tamanho do
   MDE, e **confira cada exutório**: verifique quantos pontos foram ajustados à rede de drenagem e
   compare a área de drenagem delimitada com a da estação fluviométrica (como regra prática, uma razão fora do
   intervalo de 0,8 a 1,25 indica ponto mal posicionado).
3. **Gerar as unidades de paisagem:** separar planície de inundação e encosta (o método de
   inversão do MDE, *DEM inversion*, com os valores padrão, é um bom ponto de partida).
4. **Gerar as HRUs:** informar os mapas de uso e de solos com suas tabelas de correspondência e as
   classes de declividade, e eliminar as combinações pouco representativas (por exemplo, 10% para
   uso, solo e declividade). Compare a área de cada uso **antes e depois** da filtragem: o filtro
   pode eliminar silenciosamente usos minoritários, como pastagem ou silvicultura. Para
   preservá-los, use a opção *Exempt landuses*.
5. **Configurar o modelo no SWAT+ Editor:** importar o gerador climático e os dados observados,
   definir o período de simulação e o **período de aquecimento** (*warm-up*, de 1 a 3 anos) e
   selecionar as saídas.
6. **Executar e verificar:** uma simulação concluída com sucesso termina com a mensagem
   *Execution successfully completed* no arquivo `simulation.out`. Em seguida, use o **SWAT+
   Check**, que aponta valores suspeitos (mas não indica, por si só, que o modelo está errado).

Para aprender, comece pelos dados de exemplo da bacia do Robit (Etiópia), incluídos no instalador:
assim é possível separar problemas do software de problemas dos próprios dados.

## Erros comuns e onde verificar

| Sintoma | Causa provável |
| --- | --- |
| O exutório não é ajustado à drenagem (*0 snapped*) | Ponto distante da rede ou limiar de área de contribuição alto demais |
| Erro na leitura do uso ou dos solos | Valor do raster ausente na tabela de correspondência, ou mapas em projeções diferentes |
| Não há precipitação em nenhuma sub-bacia | Coordenadas das estações fora da bacia (sinal da latitude ou da longitude) |
| Quase todo o escoamento é superficial | Valores de CN altos demais ou grupo hidrológico do solo incorreto |
| As culturas não se desenvolvem | Manejo não atribuído ou semeadura fora do período simulado |
| A simulação é interrompida logo no início | Série climática que não cobre o período, ou arquivo referenciado ausente |
| A simulação termina "com sucesso", mas os resultados não fazem sentido | O SWAT+ ignora silenciosamente nomes desconhecidos e arquivos climáticos ausentes: procure "not found" no arquivo `diagnostics.out` |
| O escoamento de base desaparece nas estiagens | Limiar de armazenamento para o escoamento de retorno do aquífero (`flo_min`) alto demais |

## Antes de calibrar: o balanço hídrico faz sentido?

Um modelo com um hidrograma bem ajustado e um balanço hídrico incoerente acerta pelos motivos
errados. Antes de comparar a vazão simulada com a observada, abra o arquivo `basin_wb_aa.txt`
(médias anuais da bacia) e verifique:

- **Fechamento do balanço (perfil do solo):** precipitação ≈ evapotranspiração + escoamento superficial +
  escoamento lateral + percolação + variação do armazenamento.
- **Razão ET/P** compatível com o clima da região (evapotranspiração maior que a precipitação é
  sinal de alerta, a menos que irrigação ou água subterrânea supram a diferença).
- **Partição do escoamento:** numa bacia perene, com aquífero, um escoamento quase todo superficial
  indica valores de CN altos demais.
- **Vegetação:** biomassa próxima de zero em HRUs agrícolas indica problema no manejo.
- **Coerência física:** a evapotranspiração das florestas em geral deve superar a das lavouras, e a
  produtividade simulada deve ser próxima da registrada na PAM para o município.
- **Unidades de planície e de encosta:** quando elas são usadas, o escoamento da encosta que chega
  à planície pode ser contabilizado duas vezes em `surq_gen`, no arquivo `basin_wb`. Feche o balanço
  com as saídas de HRU, aquífero e canal, e confirme esse comportamento na versão do SWAT+ que
  estiver usando.

Só então vem a calibração: primeiro a **calibração suave** (*soft calibration*: ajustar as
componentes do balanço hídrico a valores regionais de referência), depois a **calibração rígida**
(*hard calibration*: ajustar a série simulada à vazão observada) e, por fim, a **validação** em um
período independente. Para vazões mensais, [Moriasi et al. (2007)](https://doi.org/10.13031/2013.23153)
consideram satisfatórios NSE > 0,50, |PBIAS| < 25% e RSR ≤ 0,70. Esses limiares são uma
convenção, útil para comparar simulações, e não uma prova de que o modelo atende ao objetivo do
estudo. A eficiência de Nash-Sutcliffe (NSE) e a de Kling-Gupta
([KGE; Gupta et al., 2009](https://doi.org/10.1016/j.jhydrol.2009.08.003)) são dominadas pelas
vazões altas; por isso, avalie também assinaturas hidrológicas: curva de permanência, Q95, índice
de escoamento de base (BFI) e regime mensal. Calibre também o crescimento das culturas e a
evapotranspiração antes da vazão: a calibração das culturas altera os resultados simulados de
água, sedimentos e nutrientes ([Piniewski et al., 2026](https://doi.org/10.1016/j.envsoft.2025.106794)).

## Para continuar aprendendo

- A [página oficial do SWAT+](https://swat.tamu.edu/software/plus/) e a
  [documentação](https://swatplus.gitbook.io/docs/installation), com a descrição de cada arquivo
  de entrada e de saída.
- O tutorial do QSWAT+ e o manual do SWAT+ Editor, instalados junto com o programa.
- O grupo de usuários do SWAT+ e as conferências anuais do SWAT.
- Depois do primeiro modelo: tabelas de decisão para o manejo, calibração automática e cenários
  de uso da terra e de clima.
- **Um fluxo de trabalho completo com o SWAT+:** a [documentação do estudo de caso CS10 do
  OPTAIN](https://moritzshore.github.io/optain-cs10/), de Moritz Shore e colaboradores, descreve a
  construção reprodutível de um modelo SWAT+ para a bacia de Kråkstad (Noruega): preparação dos
  dados, configuração, manejo, verificação, calibração suave e rígida e cenários de uso da terra,
  de clima e de medidas de conservação. Ainda está em elaboração, mas é um excelente guia para as
  etapas que vêm depois do primeiro modelo.
- **O projeto OPTAIN:** [site do projeto](https://www.optain.eu/) e
  [comunidade no Zenodo](https://zenodo.org/communities/optain-h2020-project/), com protocolos,
  relatórios e dados. Destacam-se o
  [protocolo de modelagem com SWAT+](https://doi.org/10.5281/zenodo.7463395) aplicado em 14 bacias
  agrícolas europeias (Schürz et al., 2022), o
  [protocolo comum de otimização](https://doi.org/10.5281/zenodo.11473793) de medidas de retenção
  de água e nutrientes (Strauch e Schürz, 2024) e o [protocolo de modelagem em escala de parcela
  com o SWAP](https://doi.org/10.5281/zenodo.7907114) (Farkas et al., 2023), bons exemplos de como documentar um estudo de modelagem.
- **Pacotes R do fluxo de trabalho do OPTAIN:** [SWATprepR](https://biopsichas.github.io/SWATprepR/)
  (preparação dos dados de entrada), [SWATfarmR](https://chrisschuerz.github.io/SWATfarmR/)
  (calendários de manejo) e [SWATrunR](https://chrisschuerz.github.io/SWATrunR/) (execução e
  calibração do SWAT+ no R; antigo SWATplusR). Há também um
  [fluxo em R para gerar a entrada do SWATfarmR](https://doi.org/10.5281/zenodo.17531016) a partir
  de rotações de culturas por talhão (Strauch, 2025). O SWATbuildR e o SWATdoctR também fazem
  parte do fluxo, mas têm acesso restrito.
- **Calibrar as culturas, e não apenas a vazão:** [Piniewski et al. (2026)](https://doi.org/10.1016/j.envsoft.2025.106794)
  apresentam um procedimento de calibração do crescimento e da produtividade das culturas no SWAT+
  e seu efeito sobre a água, os sedimentos e os nutrientes simulados em dez bacias europeias.

## Referências

- Arnold, J. G., Čerkasova, N., White, M., et al. (2026). *Soil and Water Assessment Tool Plus
  (SWAT+)* [Software]. Zenodo. [doi:10.5281/zenodo.14983533](https://doi.org/10.5281/zenodo.14983533)
- Bieger, K., Arnold, J. G., Rathjens, H., White, M. J., Bosch, D. D., Allen, P. M., Volk, M., &
  Srinivasan, R. (2017). Introduction to SWAT+, a completely restructured version of the Soil and
  Water Assessment Tool. *Journal of the American Water Resources Association, 53*(1), 115-130.
  [doi:10.1111/1752-1688.12482](https://doi.org/10.1111/1752-1688.12482)
- Chagas, V. B. M., et al. (2020). CAMELS-BR: hydrometeorological time series and landscape
  attributes for 897 catchments in Brazil. *Earth System Science Data, 12*(3), 2075-2096.
  [doi:10.5194/essd-12-2075-2020](https://doi.org/10.5194/essd-12-2075-2020)
- Farkas, C., Shore, M., Cüceloglu, G., Czelnai, L., Nemes, A., Szabó, B., Čerkasova, N.,
  Idzelyté, R., & Weiland, S. (2023). *SWAP field-scale modelling protocol*. OPTAIN project
  deliverable. Zenodo. [doi:10.5281/zenodo.7907114](https://doi.org/10.5281/zenodo.7907114)
- Gupta, H. V., Kling, H., Yilmaz, K. K., & Martinez, G. F. (2009). Decomposition of the mean
  squared error and NSE performance criteria: implications for improving hydrological modelling.
  *Journal of Hydrology, 377*(1-2), 80-91.
  [doi:10.1016/j.jhydrol.2009.08.003](https://doi.org/10.1016/j.jhydrol.2009.08.003)
- Laipelt, L., Comini de Andrade, B., Collischonn, W., de Amorim Teixeira, A., Paiva, R. C. D.,
  & Ruhoff, A. (2024). ANADEM: A digital terrain model for South America. *Remote Sensing,
  16*(13), 2321. [doi:10.3390/rs16132321](https://doi.org/10.3390/rs16132321)
- Moriasi, D. N., Arnold, J. G., Van Liew, M. W., Bingner, R. L., Harmel, R. D., & Veith, T. L.
  (2007). Model evaluation guidelines for systematic quantification of accuracy in watershed
  simulations. *Transactions of the ASABE, 50*(3), 885-900.
  [doi:10.13031/2013.23153](https://doi.org/10.13031/2013.23153)
- Neitsch, S. L., Arnold, J. G., Kiniry, J. R., & Williams, J. R. (2011). *Soil and Water
  Assessment Tool Theoretical Documentation, Version 2009*. Texas A&M University.
- Piniewski, M., Čerkasova, N., Plunge, S., Strauch, M., Schürz, C., et al. (2026). Enhanced crop
  calibration for SWAT+: evaluating water, sediment and nutrient impacts across ten European
  catchments. *Environmental Modelling & Software, 196*, 106794.
  [doi:10.1016/j.envsoft.2025.106794](https://doi.org/10.1016/j.envsoft.2025.106794)
- Schürz, C., Čerkasova, N., Farkas, C., Nemes, A., Plunge, S., Strauch, M., Szabó, B., &
  Piniewski, M. (2022). *SWAT+ modeling protocol for the assessment of water and nutrient
  retention measures in small agricultural catchments*. OPTAIN project deliverable. Zenodo.
  [doi:10.5281/zenodo.7463395](https://doi.org/10.5281/zenodo.7463395)
- Strauch, M. (2025). *R workflow to generate SWATfarmR input* (v1.0) [Software]. Zenodo.
  [doi:10.5281/zenodo.17531016](https://doi.org/10.5281/zenodo.17531016)
- Strauch, M., & Schürz, C. (2024). *Common optimisation protocol*. Deliverable D5.1 of the EU
  Horizon 2020 project OPTAIN. Zenodo.
  [doi:10.5281/zenodo.11473793](https://doi.org/10.5281/zenodo.11473793)
- Xavier, A. C., Scanlon, B. R., King, C. W., & Alves, A. I. (2022). New improved Brazilian daily
  weather gridded data (1961-2020). *International Journal of Climatology, 42*(16), 8390-8404.
  [doi:10.1002/joc.7731](https://doi.org/10.1002/joc.7731)
