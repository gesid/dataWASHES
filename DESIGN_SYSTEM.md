# DESIGN SYSTEM — WASHES (Site Oficial)

> **Fonte analisada:** https://washescommunity.github.io/website/
> **Stack detectada:** SPA React 18 + Vite (build de produção), estilizado com **Tailwind CSS** (compilado), **MUI Timeline** (programação do evento) e **react-icons / Font Awesome** (ícones sociais). A tipografia é **Sofia Sans** (fonte variável, pesos `1..1000`).
>
> Este documento **não copia código** do site. Ele traduz o Design System observado no bundle compilado (CSS + JS) em tokens, componentes e diretrizes reaproveitáveis, e termina com um comparativo entre o site oficial e o dashboard atual do dataWASHES.

---

## 1. Foundations

### 1.1 Colors

A paleta do site é composta por **cores de marca oficiais** aplicadas via valores arbitrários do Tailwind + neutros do Tailwind default.

#### Cores de marca (oficiais)

| Nome | HEX | RGB | Uso observado |
|---|---|---|---|
| `--color-magenta` | `#E72B78` | `rgb(231 43 120)` | **Primária/CTA.** Texto de destaque, fundo de elementos ativos, primeira faixa de gradiente de seção, barra de contagem |
| `--color-magenta-hover` | `#EC4899` | `rgb(236 72 153)` | Hover de elementos magenta (overlay de card em grupo) |
| `--color-cyan` | `#36BCEE` | `rgb(54 188 238)` | Secundária. Fundos, hover de links na navbar, faixa de gradiente, avatar social (`bg-cyan-400`) |
| `--color-cyan-bright` | `#22D3EE` | `rgb(34 211 238)` | Variação ciano (Tailwind `cyan-400`) |
| `--color-cyan-gradient` | `#22CBE4` | `rgb(34 203 228)` | `from` de gradiente vertical |
| `--color-green` | `#66C75C` | `rgb(102 199 92)` | Sucesso/status. Barra de contagem, faixa de gradiente |
| `--color-green-light` | `#74C76B` | `rgb(116 199 107)` | `from` de gradiente, hover de texto, fundo alternativo |
| `--color-navy` | `#003358` | `rgb(0 51 88)` | **Títulos/"headings"** e CTA sólido (destaque máximo) |
| `--color-teal` | `#0D6080` | `rgb(13 96 128)` | Subtítulos/títulos de seção com contraste |
| `--color-steel` | `#2A5D82` | `rgb(42 93 130)` | Fundo/borda de cabeçalhos de accordion e acentos intermediários |
| `--color-ink` | `#1C1D21` | `rgb(28 29 33)` | **Footer** (fundo escuro) |

#### Neutros

| Nome | HEX | RGB | Uso |
|---|---|---|---|
| `--surface` | `#FFFFFF` | `rgb(255 255 255)` | Navbar, cards, fundo de seções |
| `--text-strong` | `#2F2F2F` | `rgb(47 47 47)` | Texto de corpo principal |
| `--text-body` | `#1F2937` | `rgb(31 41 55)` | Tailwind `gray-800` (títulos de card de equipe) |
| `--text-secondary` | `#6B7280` | `rgb(107 114 128)` | Tailwind `gray-500` |
| `--text-secondary-2` | `#4B5563` | `rgb(75 85 99)` | Tailwind `gray-600` |
| `--text-muted` | `#6C757D` | `rgb(108 117 125)` | Metadados discretos |
| `--text-zinc` | `#27272A` | `rgb(39 39 42)` | Tailwind `zinc-800` |
| `--border-subtle` | `#2F2F2F3B` | `rgba(47 47 47 .23)` | Borda de pills/botões |
| `--border-soft` | `#2F2F2F` | `rgb(47 47 47)` | Bordas de campos/inputs (1px) |
| `--hover-surface` | `#DADAD4BE` | `rgba(218 218 218 .75)` | Hover de pills nos breakpoints grandes |

#### Gradientes

| Gradiente | Stops | Uso |
|---|---|---|
| Vertical colorido | `from-50%` `#22CBE4` / `#E72B78` / `#74C76B` → transparente | Faixas decorativas verticais do Hero |
| Horizontal | `from-40%` `white` → transparente | Vinheta sobre banner no rodapé do hero |

> Regra de contraste: o magenta e o navy são reservados para texto **grande/largo** (`font-bold`, ≥ 28px) ou elementos sólidos; o texto de corpo usa `#2F2F2F`; o texto secundário usa `gray-500/#6C757D`.

---

### 1.2 Typography

#### Família
- **`Sofia Sans`** (variável, `wght 1..1000`, itálico disponível) — aplicada a **todos** os elementos via `* { font-family: "Sofia Sans", sans-serif; }`.
- Carregada com `font-optical-sizing: auto` e `font-style: normal`.
- Import: `https://fonts.googleapis.com/css2?family=Sofia+Sans:ital,wght@0,1..1000;1,1..1000&display=swap`

Interessante: os **números/estatísticas e labels** herdam a mesma família (não há fonte mono ou numérica separada).

#### Pesos

| Peso | Classe |
|---|---|
| 300 | `font-light` |
| 500 | `font-medium` |
| 600 | `font-semibold` |
| 700 | `font-bold` (dominante em títulos) |

#### Escala tipográfica (rem/px)

| Token sugerido | Classe(s) | Tamanho | Line-height |
|---|---|---|---|
| `--font-hero` | `lg:text-7xl md:text-6xl text-4xl` | 4.5rem / 3.75rem / 2.25rem | 1 |
| `--font-display` | `text-5xl` | 3rem | 1 |
| `--font-section` | `[28px]` → `lg:[32px]` | 28px → 32px | — |
| `--font-title-lg` | `lg:text-4xl text-3xl` | 2.25rem / 1.875rem | 2.5/2.25rem |
| `--font-title` | `text-2xl` (`md:text-6xl` em hero) | 1.5rem | 2rem |
| `--font-subtitle` | `text-xl` / `lg:text-2xl` | 1.25rem / 1.5rem | 1.75/2rem |
| `--font-body` | `text-lg` | 1.125rem | 1.75rem |
| `--font-body-md` | `text-base` / `sm:text-base` | 1rem | 1.5rem |
| `--font-small` | `text-sm` | 0.875rem | 1.25rem |
| `--font-caption` | `text-[10px]` | 10px | — |

Tratamento de hero: títulos com `leading-none`; descrições longas com `leading-9` (2.25rem) e `text-justify`.

---

### 1.3 Elevation

| Token | Shadow | Uso |
|---|---|---|
| `--shadow-sm` | — | (não usado no bundle) |
| `--shadow-md` | `0 4px 6px -1px rgb(0 0 0 /.1), 0 2px 4px -2px rgb(0 0 0 /.1)` | Cards, navbar, accordion fechado |
| `--shadow-lg` | `0 10px 15px -3px rgb(0 0 0 /.1), 0 4px 6px -4px rgb(0 0 0 /.1)` | Rodapé do accordion expandido |
| `--shadow-2xl` | `0 25px 50px -12px rgb(0 0 0 /.25)` | **Hover** de cards de edições |
| `--shadow-card-photo` | `4px 6px 6px 0px rgba(0,0,0,.18)` | Tiles do feed do Instagram |
| `--shadow-hero` | `0 35px 60px -15px rgba(0,0,0,.3)` | CTA sólido do hero |

---

### 1.4 Radius

| Token | Valor | Classe | Uso |
|---|---|---|---|
| `--radius-sm` | 4px | `rounded` | — |
| `--radius-md` | 8px | `rounded-lg` (Tailwind) | Tiles Instagram, chips |
| `--radius` | 10px | `rounded-[10px]` | Accordion (borda inferior) |
| `--radius-lg` | 12px | `rounded-xl` | Cards, accordion, avatar CTA |
| `--radius-xl` | 16px | `lg:rounded-2xl` | Cards em desktop |
| `--radius-full` | 9999px | `rounded-full` | Pills/botões e avatares `w-24 h-24` |

Padrão adotado: cantos arredondados **generosos** (10–16px) em cards; **pílulas completas** em botões pequenos.

---

### 1.5 Spacing

Escala derivada do Tailwind (mobile-first, base 0.25rem = 4px). Tokens:

| Token | Valor | Tokens | Valor |
|---|---|---|---|
| `--space-1` | 4px | `--space-6` | 24px |
| `--space-2` | 8px | `--space-7` | 28px |
| `--space-3` | 12px | `--space-8` | 32px |
| `--space-3.5` | 14px | `--space-10` | 40px |
| `--space-4` | 16px | `--space-12` | 48px |
| `--space-5` | 20px | `--space-14` | 56px |

**Padrões observados**
- Gap de grid entre cards: `gap-4` (16px) a `gap-20` (80px); seções maiores `lg:gap-20`/`lg:gap-32`.
- Padding de container: `px-4`/`px-5` (16–20px lateral).
- Espaçamento vertical de seções: `my-10` (40px), `my-16`/`my-20`, `lg:my-24` (96px).
- Navbar vertical: `py-3` (12px); Footer: `py-6` (24px).

---

### 1.6 Grid & Layout

- **Container central:** `container mx-auto` com `max-width` progressivo por breakpoint (640/768/1024/1280/1536px). Telas grandes usam `max-w-screen-xl` (1280px) e `max-w-screen-2xl` (1536px).
- **Gradis:** construídos com `flex` + `flex-wrap` e `justify-*` (`justify-center`, `justify-evenly`, `justify-around`) — grid explícito Tailwind `grid` é pouco usado; a distribuição é feita por flexbox responsivo.
- Padrões de colunas: `lg:w-1/2`, `lg:w-1/3`, 2–3 cards por linha; feed Instagram em 1–5 tiles assimétricos.
- **Breakpoints**

| Token | px | Sufixo |
|---|---|---|
| `--bp-sm` | 640px | `sm:` |
| `--bp-md` | 768px | `md:` |
| `--bp-lg` | 1024px | `lg:` |
| `--bp-xl` | 1280px | `xl:` |
| `--bp-2xl` | 1536px | `2xl:` |

Regras importantes: direção empilha em mobile (`flex-col`) e vira linha em `lg:flex-row`; navbar desktop aparece só em `lg:flex`; menu mobile some em `lg:hidden`.

---

## 2. Components

### 2.1 Navbar

- **Aparência:** barra fixa no topo (`fixed top-0 left-0 w-full`), fundo **branco**, `z-50`, sombra `shadow-md`.
- **Propriedades:** container `mx-auto px-4 py-3 flex justify-between items-center`; logo (`h-8`, `mr-2`) + wordmark **WASHES** (`text-2xl font-medium`).
- **Links:** namespaces em **CAIXA ALTA** (`HOME`, `QUEM SOMOS`, `WASHES {ano}`, `EDIÇÕES ANTERIORES`, `DATAWASHES` — externo). Desktop: `hidden lg:flex space-x-8`; item ativo/ênfase em magenta; hover de texto com ciano.
- **Estados:** item ativo → magenta; hover → ciano (`#36BCEE`).
- **Mobile:** botão hamburger (`lg:hidden`, ícone 24px); abre overlay **fullscreen branco** (`fixed inset-0 bg-white flex flex-col items-center justify-center z-40`) com botão fechar `absolute top-4 right-4`.
- **Variável:** `--navbar-bg: #FFFFFF; --navbar-shadow: var(--shadow-md);`

### 2.2 Footer

- **Aparência:** fundo **`#1C1D21`** (`bg-[#1C1D21]`), texto branco, centralizado (`flex flex-col items-center`), `py-6`, `w-full`.
- **Propriedades:** logo `h-12 mb-4`; linha de ícones sociais `flex space-x-6 mb-4` (X, Instagram, LinkedIn, GitHub); copyright `© 2025 WASHES. Todos os direitos reservados.`.
- **Estados:** links/ícones sociais `text-white`; ícones `size:24` de cor branca (sem hover explícito fo no bundle).
- **Variáveis:** `--footer-bg: #1C1D21; --footer-text: #FFFFFF;`

### 2.3 Botões / Pills

Dois padrões dominantes:

1. **Pill outline** (botão padrão)
   - Classe: `rounded-full border border-[#2f2f2f3b] py-2 px-4 sm:w-auto w-full flex items-center justify-center gap-2`
   - Desktop: `lg:border-none lg:hover:bg-[#dadadabe]`
   - Hover global: `hover:-translate-y-1 hover:scale-100 duration-300 transition ease-in-out`
   - Estados: default transparente com borda sutil; hover eleva (`-translate-y-4px`) + escala 100% + fundo acinzentado.
2. **CTA sólido**
   - `bg-[#2A5D82]` (accordion) ou `bg-[#003358]` (hero) + `text-white` + `rounded-xl`
   - Hero CTA com `shadow-[0_35px_60px_-15px_rgba(0,0,0,.3)]`.

**Variáveis:** `--btn-radius: 9999px; --btn-padding: 8px 16px; --btn-hover-translate: -4px;`

### 2.4 Cards

#### Card de edição (evento)
- Aparência: `rounded-xl shadow-md` em coluna (`flex flex-col gap-5`), `relative bg-white`, `mx-2 my-7 pb-2 text-center`.
- Mídia: `rounded-t-xl max-h-[170px] w-[350px]`, imagem banner.
- Hover: `lg:hover:-translate-y-1.5 lg:hover:shadow-2xl` (+ overlay do grupo em `group-hover:bg-pink-500`).
- Rodapé do card: link "Anais" com `underline` e semântica de subtítulo.

#### Card de pessoa (equipe)
- `w-[300px] h-[320px] p-5 bg-white rounded-xl shadow-md overflow-hidden border`
- Avatar `w-24 h-24 rounded-full`; nome `text-xl font-bold text-gray-800`; função `text-gray-500`; bio `mt-2 break-words`.
- Redes sociais do card: `flex space-x-4 mt-4`, ícones com `hover:text-blue-500`.

#### Tile de feed Instagram
- `rounded-lg shadow-[4px_6px_6px_0px_rgba(0,0,0,0.18)]`; em `lg:` → `lg:rounded-2xl`.

**Variáveis:** `--card-bg:#FFFFFF; --card-radius:12px; --card-shadow:var(--shadow-md); --card-hover-shadow:var(--shadow-2xl);`

### 2.5 Badges / Indicadores

- Barras de progresso/contagem de datas: `h-1` com `bg-[#E72B78]`, `bg-[#36BCEE]`, `bg-[#66C75C]` (três faixas de cores — magenta, ciano, verde).
- Pastilhas de data/status ("Em Breve", "Datas Importantes") usando pills outline.
- **Variáveis:** `--badge-success:#66C75C; --badge-active:#E72B78;`

### 2.6 Hero

- Containers full-bleed: `w-full h-[450px] lg:h-[700px]` + `relative overflow-hidden`, banner `bg-cover bg-center`.
- Título: `text-[#003358] font-bold text-4xl md:text-6xl lg:text-7xl` (`leading-none`).
- Faixas decorativas verticais: `bg-gradient-to-b from-[#22CBE4|#E72B78|#74C76B] from-50%` com `lg:md:w-10 w-5 h-full z-20`.
- Vinheta inferior: `bg-gradient-to-r from-white from-40%` + `max-h-24 absolute bottom-[50px]`.

### 2.7 Accordion (Chamada de Trabalhos)

- Cabeçalho: `cursor-pointer w-full bg-[#2A5D82] border border-[#2A5D82] rounded-xl flex text-white`.
- Painel: `bg-white px-6 rounded-b-[10px] shadow-md w-full` + `transition-all ease-in-out overflow-hidden origin-top`.
- Estados: fechado `max-h-0`; expandido anima `duration-500` crescendo a altura; transição com `transition-all`.

### 2.8 Timeline (programação — MUI)

- Componente **MUI Timeline** (`MuiTimeline`, `MuiTimelineItem/Separator/Connector/Dot/Content`) para horários e sessões.
- Visual: dots, conectores e conteúdo tipográfico proprio do MUI, fundido ao tema Sofia Sans.

### 2.9 Links

- Links de conteúdo: com `underline` (ex.: "Anais").
- Hover de texto: `hover:text-[#36BCEE]`, `hover:text-[#74C76B]`, `hover:text-blue-500` (canais sociais) e `hover:text-white`.
- Links externos sempre com `target="_blank" rel="noopener noreferrer"`.

### 2.10 Inputs

- Campos de formulário/disponíveis no bundle: borda `border-black border` de **1px**, largura total (`w-full`), alinhamento à esquerda; botões de envio com `border-black border px-8 py-4`.
- Formulários ricos (submissão, dados) usam inputs **MUI** (`TextField`, `Select`, etc.).

### 2.11 Ícones

- **Font Awesome (via react-icons)** renderizados inline, tamanho `24` (`size:24`): X (Twitter), Instagram, LinkedIn, GitHub, hamburguer/fechar (menu mobile).
- Avatares sociais em círculo `w-10 h-10 rounded-full bg-cyan-400`.
- **Variáveis:** `--icon-size: 24px;`

### 2.12 Hover & Animações

| Interação | Definição |
|---|---|
| Durações | `150ms` (padrão), `300ms`, `500ms` |
| Easing | `cubic-bezier(.4,0,.2,1)` (`ease-in-out`) |
| Elevação de card | `translateY(-4px)`; `lg:-translate-y-1.5` (~ -6px) |
| Card de edição | `-translate-y-1.5` + `shadow-2xl` + overlay magenta |
| Pill | `-translate-y-1` + `scale-100` + fundo `#dadadabe` |
| Accordion | `max-h` animada `500ms` com `origin-top` |
| Cursor | `cursor-pointer` em elementos clicáveis |

---

## 3. Variáveis CSS (geradas)

Conjunto consolidado (proposta de tokens, derivado da análise):

```css
:root{
  /* ── Brand ── */
  --color-primary:        #E72B78;
  --color-primary-hover:  #EC4899;
  --color-secondary:      #36BCEE;
  --color-secondary-dim:  #22D3EE;
  --color-secondary-fade: #22CBE4;
  --color-success:        #66C75C;
  --color-success-light:  #74C76B;
  --color-navy:           #003358;
  --color-teal:           #0D6080;
  --color-steel:          #2A5D82;
  --color-ink:            #1C1D21;

  /* ── Surfaces & Text ── */
  --surface:              #FFFFFF;
  --surface-dark:         #1C1D21;
  --text-strong:          #2F2F2F;
  --text-body:            #1F2937;
  --text-secondary:       #6B7280;
  --text-muted:           #6C757D;
  --text-on-dark:         #FFFFFF;

  /* ── Borders ── */
  --border-subtle:        #2F2F2F3B;
  --border-soft:          #2F2F2F;
  --border-hover:         #DADAD4BE;

  /* ── Typography ── */
  --font-family:          "Sofia Sans", sans-serif;
  --font-hero:            4.5rem;   /* lg: 72px; md: 60px */
  --font-display:         3rem;
  --font-section:         32px;     /* mobile 28px */
  --font-title:           1.5rem;
  --font-subtitle:        1.125rem;
  --font-body:            1rem;
  --font-caption:         10px;
  --font-weight-light:    300;
  --font-weight-medium:   500;
  --font-weight-semibold: 600;
  --font-weight-bold:     700;

  /* ── Elevation ── */
  --shadow-md:   0 4px 6px -1px rgb(0 0 0 /.1), 0 2px 4px -2px rgb(0 0 0 /.1);
  --shadow-lg:   0 10px 15px -3px rgb(0 0 0 /.1), 0 4px 6px -4px rgb(0 0 0 /.1);
  --shadow-2xl:  0 25px 50px -12px rgb(0 0 0 /.25);
  --shadow-photo: 4px 6px 6px 0px rgb(0 0 0 /.18);
  --shadow-hero: 0 35px 60px -15px rgb(0 0 0 /.3);

  /* ── Radius ── */
  --radius-sm:    4px;
  --radius-md:    8px;
  --radius-lg:    12px;
  --radius-xl:    16px;
  --radius-full:  9999px;

  /* ── Spacing (base 4px) ── */
  --space-1: 4px;  --space-2: 8px;  --space-3: 12px;
  --space-4: 16px; --space-5: 20px; --space-6: 24px;
  --space-8: 32px; --space-10: 40px; --space-14: 56px;

  /* ── Grid / Breakpoints ── */
  --bp-sm: 640px; --bp-md: 768px; --bp-lg: 1024px;
  --bp-xl: 1280px; --bp-2xl: 1536px;
  --container-sm: 640px; --container-md: 768px; --container-lg: 1024px;
  --container-xl: 1280px; --container-2xl: 1536px;

  /* ── Motion ── */
  --duration-fast: 150ms; --duration-base: 300ms; --duration-slow: 500ms;
  --ease: cubic-bezier(.4,0,.2,1);
}
```

---

## 4. Diferenças entre o site oficial e o dashboard atual

> Dashboard atual do dataWASHES (`/dashboard` + landing `/`): paleta oficial **já parcialmente aplicada** (magenta `#E72B78`, ciano `#36BCEE`, navy `#003358`, verde `#66C75C`, teal `#0D6080`, ink `#1C1D21`, `Sofia Sans` em títulos + `system-ui` em corpo/tabelas, KPI cards com glassmorphism, paleta Chart.js oficial).

### 4.1 Alta prioridade

| # | Aspecto | Site oficial | Dashboard atual | Ação sugerida |
|---|---|---|---|---|
| A1 | **Navbar** | Branca, `fixed top-0`, `shadow-md`, `z-50`, logo + wordmark, links em caixa alta | Escura `#1C1D21`, sticky, sem wordmark | Alinhar navbar à identidade oficial (branca) mantendo a legibilidade do logo; usar `shadow-md` e links caixa alta |
| A2 | **Hero** | Full-bleed com banner fotográfico + faixas verticais gradiente (`#22CBE4`/`#E72B78`/`#74C76B`) + título navy gigante + vinheta branca | Gradiente navy→ciano com glows radiais, card centralizado | Adotar layout de banner de largura total e faixas coloridas da marca |
| A3 | **Scope de tipografia** | `Sofia Sans` (variável 1–1000) em **todos** os elementos, `font-optical-sizing:auto` | `Sofia Sans` estática (400–900) só em títulos/KPI/badges; corpo `system-ui` | Decidir: (a) aplicar Sofia Sans global (100% fiel ao site oficial) ou (b) manter híbrido por legibilidade |

### 4.2 Média prioridade

| # | Aspecto | Site oficial | Dashboard atual | Ação sugerida |
|---|---|---|---|---|
| M1 | **Botões/pills** | Pills `rounded-full` com borda `#2f2f2f3b`, hover `-translate-y-1`+`scale-100`+`#dadadabe` | Botões `rounded-sm/8px`, mágenta sólido | Padronizar pills arredondadas com padding `8px 16px` e animação de hover |
| M2 | **Sombras** | Escala Tailwind (`md/lg/2xl`) + sombras custom | Sombras próprias leves (`box-shadow` custom 1–8px) | Mapear `--shadow-*` para a escala oficial |
| M3 | **Hover de links** | Ciano `#36BCEE`, verde `#74C76B`, `underline` | Teal `#0D6080` → magenta | Usar ciano/verde nos hovers e `underline` em links de conteúdo |
| M4 | **Altura/tamanho de títulos de seção** | `28px → 32px` bold navy ou `#0D6080`, subtítulos `#2F2F2F` `leading-9` | `1.6rem` bold navy | Substituir escala de seção pela escala oficial (`--font-section`) |
| M5 | **Cards (gerais)** | `rounded-xl` + `shadow-md`, hover `-translate-y`+`shadow-2xl`, sem glassmorphism | KPI cards com **glassmorphism** (backdrop blur + bordas translúcidas) | Considerar cards sólidos oficiais para consistência; se manter glass, conter nos KPIs |

### 4.3 Baixa prioridade

| # | Aspecto | Site oficial | Dashboard atual | Ação sugerida |
|---|---|---|---|---|
| B1 | **Radius** | `rounded`/`xl`/`2xl`/`full` (4/8/12/16/9999px) | Tokens próprios 8/12/16px | Unificar para a escala `--radius-*` |
| B2 | **Ícones** | Font Awesome `size:24` inline + avatares ciano | SVG inline stroke (lucide-like), `stroke-width 2` | Não é bloqueante; alinhar tamanho/estilo se desejado |
| B3 | **Grade/layout** | `container` até 1280/1536px, flex grids | `max-width: 1200px`, grid CSS explícito | Alinhar container a `--container-xl` (1280px) |
| B4 | **Timeline** | MUI Timeline na programação | Gráficos/elementos próprios | Aplicável só se reusarmos a seção de programação |
| B5 | **Spacing** | Escala 4px (Tailwind) rebatizada | Valores isolados em `:root` | Consolidar tokens `--space-*` |
| B6 | **Footer** | `#1C1D21`, central, logo + 4 redes sociais (X, IG, LinkedIn, GitHub) | `#1C1D21`, links de texto (GitHub, SOL, WASHES) | Adicionar ícones sociais oficiais (X/Instagram/LinkedIn/GitHub) |

---

## 5. Checklist de adoção no dataWASHES

- [ ] Substituir scale de tipografia por `--font-*` do site oficial.
- [ ] Definir `--color-*`, `--radius-*`, `--space-*`, `--shadow-*`, `--duration-*` num único `:root` compartilhado.
- [ ] Decidir navbar única (branca oficial) para landing e dashboard.
- [ ] Padronizar pills (`rounded-full`) e hovers com `-translate-y-1`/`scale-100`.
- [ ] Usar `underline` em links de conteúdo e hover ciano/verde.
- [ ] Alinhar H1/H2/seção à escala `28px→32px` navy.
- [ ] Revisar WCAG: manter contraste ≥ 3:1 (texto grande) e ≥ 4.5:1 (texto normal) ao substituir `gray-500/#6C757D` por tons mais escuros.