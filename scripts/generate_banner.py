#!/usr/bin/env python3
"""
Gerador do Banner Exuberante para o GitHub Profile (xoykor)
Lê assets/tux.svg e gera assets/profile-banner.svg com estética Sci-Fi/HUD,
tentáculos biomecânicos em camadas 3D, filtros neon e animações CSS nativas.
"""

import base64
import math
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
TUX_PATH = ROOT_DIR / "assets" / "tux.svg"
OUTPUT_SVG = ROOT_DIR / "assets" / "profile-banner.svg"

WIDTH = 1200
HEIGHT = 480


def load_tux_data_uri(svg_path: Path) -> str:
    """Embute o tux.svg em base64 para funcionar dentro da tag <img> do GitHub."""
    if svg_path.exists():
        raw_bytes = svg_path.read_bytes()
        b64 = base64.b64encode(raw_bytes).decode("utf-8")
        return f"data:image/svg+xml;base64,{b64}"
    return ""


def bezier_point(t: float, p0: tuple, p1: tuple, p2: tuple, p3: tuple) -> tuple:
    """Calcula um ponto (x, y) em uma curva de Bézier cúbica."""
    u = 1 - t
    x = (u**3) * p0[0] + 3 * (u**2) * t * p1[0] + 3 * u * (t**2) * p2[0] + (t**3) * p3[0]
    y = (u**3) * p0[1] + 3 * (u**2) * t * p1[1] + 3 * u * (t**2) * p2[1] + (t**3) * p3[1]
    return x, y


def bezier_tangent_angle(t: float, p0: tuple, p1: tuple, p2: tuple, p3: tuple) -> float:
    """Calcula o ângulo tangente (em graus) no ponto t da curva de Bézier."""
    u = 1 - t
    dx = 3 * (u**2) * (p1[0] - p0[0]) + 6 * u * t * (p2[0] - p1[0]) + 3 * (t**2) * (p3[0] - p2[0])
    dy = 3 * (u**2) * (p1[1] - p0[1]) + 6 * u * t * (p2[1] - p1[1]) + 3 * (t**2) * (p3[1] - p2[1])
    return math.degrees(math.atan2(dy, dx))


def build_tentacle(
    tid: str,
    p0: tuple,
    p1: tuple,
    p2: tuple,
    p3: tuple,
    thickness: float = 20,
    opacity: float = 1.0,
    pulse_delay: float = 0.0,
) -> str:
    """Gera um tentáculo mecânico segmentado com sombra, relevo metálico e pulso neon."""
    path_d = f"M {p0[0]:.1f},{p0[1]:.1f} C {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f}"

    # Pontos de brilho especular nos segmentos
    highlights = []
    steps = 14
    for i in range(1, steps):
        t = i / steps
        bx, by = bezier_point(t, p0, p1, p2, p3)
        angle = bezier_tangent_angle(t, p0, p1, p2, p3)
        rad = math.radians(angle - 90)
        hx = bx + math.cos(rad) * (thickness * 0.22)
        hy = by + math.sin(rad) * (thickness * 0.22)
        highlights.append(
            f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="1.6" fill="#e2f1ff" opacity="0.65" />'
        )

    highlights_svg = "\n        ".join(highlights)

    return f"""
      <g id="{tid}" opacity="{opacity}">
        <!-- Sombra 3D projetada -->
        <path d="{path_d}" fill="none" stroke="#02050a" stroke-width="{thickness + 8}" stroke-linecap="round" opacity="0.65" transform="translate(0, 8)" />
        <!-- Contorno escuro de blindagem -->
        <path d="{path_d}" fill="none" stroke="#081221" stroke-width="{thickness + 4}" stroke-linecap="round" />
        <!-- Corpo metálico base -->
        <path d="{path_d}" fill="none" stroke="url(#metalBody)" stroke-width="{thickness}" stroke-linecap="round" />
        <!-- Anéis de segmentação mecânica -->
        <path d="{path_d}" fill="none" stroke="#0b1729" stroke-width="{thickness}" stroke-linecap="butt" stroke-dasharray="4 22" />
        <!-- Trilha interna escura -->
        <path d="{path_d}" fill="none" stroke="#10233f" stroke-width="{thickness * 0.35:.1f}" stroke-linecap="round" />
        <!-- Feixe de energia ciano animado -->
        <path d="{path_d}" fill="none" stroke="#00e5ff" stroke-width="2.2" stroke-linecap="round" stroke-dasharray="14 90" class="energy-pulse" style="animation-delay: {pulse_delay}s;" filter="url(#cyanGlow)" />
        <!-- Pontos de reflexo metálico -->
        {highlights_svg}
      </g>
    """


def build_claw(x: float, y: float, angle: float, scale: float = 1.0, tool: str = "none") -> str:
    """Desenha a garra robótica articulada e a ferramenta acoplada na ponta."""
    tool_svg = ""
    if tool == "screwdriver":
        # Chave de fenda amarela/laranja apontando para baixo/esquerda + faíscas
        tool_svg = """
        <g transform="rotate(15) translate(16, 0)">
          <!-- Haste metálica -->
          <rect x="28" y="-2.2" width="38" height="4.4" rx="1.5" fill="#cbd5e1" stroke="#0f172a" stroke-width="1.5" />
          <polygon points="66,-2.2 75,-0.8 75,0.8 66,2.2" fill="#38bdf8" filter="url(#cyanGlow)" />
          <!-- Cabo isolado amarelo/âmbar -->
          <rect x="0" y="-8" width="30" height="16" rx="5" fill="url(#screwdriverGrad)" stroke="#0f172a" stroke-width="2" />
          <line x1="8" y1="-5" x2="22" y2="-5" stroke="#fef08a" stroke-width="1.8" stroke-linecap="round" opacity="0.8" />
          <line x1="8" y1="0" x2="22" y2="0" stroke="#78350f" stroke-width="1.8" stroke-linecap="round" opacity="0.5" />
          <!-- Faíscas de energia na ponta -->
          <circle cx="77" cy="0" r="2.5" fill="#00e5ff" class="spark-blink" filter="url(#cyanGlow)" />
        </g>
        """
    elif tool == "paper":
        # Folha de código / documento flutuante no topo direito
        tool_svg = """
        <g transform="rotate(20) translate(12, -18)" class="float-slow">
          <path d="M 0,0 L 36,-6 L 44,36 L 8,42 Z" fill="#f8fafc" stroke="#0f172a" stroke-width="2" filter="url(#cyanGlowSubtle)" />
          <path d="M 6,6 L 30,2 L 36,32 L 12,36 Z" fill="#e2e8f0" opacity="0.4" />
          <!-- Linhas de código estilizadas -->
          <line x1="8" y1="9" x2="22" y2="7" stroke="#0284c7" stroke-width="2.5" stroke-linecap="round" />
          <line x1="10" y1="16" x2="31" y2="13" stroke="#334155" stroke-width="2" stroke-linecap="round" />
          <line x1="11" y1="22" x2="27" y2="19" stroke="#00e5ff" stroke-width="2" stroke-linecap="round" />
          <line x1="13" y1="29" x2="33" y2="26" stroke="#334155" stroke-width="2" stroke-linecap="round" />
        </g>
        """
    elif tool == "bulb":
        # Lâmpada de ideia com brilho dourado intenso no canto inferior direito
        tool_svg = """
        <g transform="rotate(-15) translate(14, 0)">
          <!-- Halo de luz dourada -->
          <circle cx="34" cy="0" r="26" fill="url(#bulbHalo)" class="bulb-pulse" />
          <!-- Base de rosca metálica -->
          <rect x="8" y="-6" width="10" height="12" rx="2" fill="#94a3b8" stroke="#0f172a" stroke-width="1.8" />
          <line x1="11" y1="-6" x2="11" y2="6" stroke="#334155" stroke-width="1.5" />
          <line x1="15" y1="-6" x2="15" y2="6" stroke="#334155" stroke-width="1.5" />
          <!-- Bulbo de vidro iluminado -->
          <path d="M 18,-8 C 26,-16 46,-14 46,0 C 46,14 26,16 18,8 Z" fill="url(#bulbGlass)" stroke="#ca8a04" stroke-width="1.8" filter="url(#goldGlow)" />
          <!-- Filamento incandescente -->
          <path d="M 18,-2 L 28,-4 L 31,0 L 28,4 L 18,2" fill="none" stroke="#ffffff" stroke-width="1.5" stroke-linecap="round" />
        </g>
        """

    return f"""
      <g transform="translate({x:.1f}, {y:.1f}) rotate({angle:.1f}) scale({scale})">
        <!-- Garras mecânicas de 3 dedos -->
        <path d="M 0,-6 Q 14,-20 26,-12" fill="none" stroke="#64748b" stroke-width="4.5" stroke-linecap="round" />
        <path d="M 0,-6 Q 14,-20 26,-12" fill="none" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round" />
        <path d="M 2,0 L 24,0" fill="none" stroke="#64748b" stroke-width="4.5" stroke-linecap="round" />
        <path d="M 2,0 L 24,0" fill="none" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round" />
        <path d="M 0,6 Q 14,20 26,12" fill="none" stroke="#64748b" stroke-width="4.5" stroke-linecap="round" />
        <path d="M 0,6 Q 14,20 26,12" fill="none" stroke="#cbd5e1" stroke-width="2" stroke-linecap="round" />
        {tool_svg}
        <!-- Articulação / Punho com anel neon -->
        <circle cx="0" cy="0" r="12" fill="#091324" stroke="#00e5ff" stroke-width="2" filter="url(#cyanGlowSubtle)" />
        <circle cx="0" cy="0" r="6" fill="#334155" stroke="#00e5ff" stroke-width="1.2" />
        <circle cx="0" cy="0" r="2.2" fill="#00e5ff" />
      </g>
    """


def generate_banner() -> None:
    tux_uri = load_tux_data_uri(TUX_PATH)

    # Coordenadas do Núcleo Robótico (Direita)
    cx, cy = 875, 255

    # Definição dos 6 tentáculos: (id, p0, p1, p2, p3, espessura, opacidade, delay, ferramenta)
    tentacles_data = [
        # 1. Tentáculo de fundo (passa por trás do Tux)
        ("t-back-mid", (cx - 45, cy + 10), (690, 275), (550, 315), (435, 345), 17, 0.60, 0.8, "none"),
        # 2. Tentáculo superior direito (segurando o código/papel)
        ("t-top-right", (cx + 40, cy - 40), (960, 175), (1025, 130), (1070, 95), 18, 0.90, 0.3, "paper"),
        # 3. Tentáculo inferior direito (segurando a lâmpada)
        ("t-bot-right", (cx + 45, cy + 35), (965, 310), (1015, 360), (1055, 405), 18, 0.90, 1.4, "bulb"),
        # 4. Tentáculo superior esquerdo (curvado abaixo do subtítulo para NÃO cobrir o texto!)
        ("t-top-left", (cx - 35, cy - 42), (710, 155), (535, 185), (415, 205), 20, 0.95, 0.0, "none"),
        # 5. Tentáculo médio esquerdo (segurando a chave de fenda)
        ("t-mid-left", (cx - 50, cy - 18), (725, 200), (635, 225), (555, 265), 19, 1.00, 0.6, "screwdriver"),
        # 6. Tentáculo inferior esquerdo (passando abaixo dos pés do Tux)
        ("t-bot-left", (cx - 40, cy + 35), (675, 340), (505, 395), (345, 425), 20, 1.00, 1.1, "none"),
    ]

    back_tentacles_svg = []
    front_tentacles_svg = []

    for tid, p0, p1, p2, p3, thick, opac, delay, tool in tentacles_data:
        t_svg = build_tentacle(tid, p0, p1, p2, p3, thick, opac, delay)
        end_angle = bezier_tangent_angle(1.0, p0, p1, p2, p3)
        c_svg = build_claw(p3[0], p3[1], end_angle, scale=0.95, tool=tool)
        combined = t_svg + c_svg
        if tid == "t-back-mid":
            back_tentacles_svg.append(combined)
        else:
            front_tentacles_svg.append(combined)

    tux_element = (
        f'<image href="{tux_uri}" x="330" y="218" width="165" height="195" filter="url(#tuxRimLight)" />'
        if tux_uri
        else ""
    )

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="100%" height="100%">
  <defs>
    <!-- Gradiente de Fundo Sci-Fi Profundo -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#04070d" />
      <stop offset="50%" stop-color="#07101e" />
      <stop offset="100%" stop-color="#03060c" />
    </linearGradient>

    <!-- Halo Radial do Núcleo de IA -->
    <radialGradient id="coreAura" cx="73%" cy="53%" r="42%">
      <stop offset="0%" stop-color="#00e5ff" stop-opacity="0.22" />
      <stop offset="45%" stop-color="#0284c7" stop-opacity="0.08" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0" />
    </radialGradient>

    <!-- Halo Radial do Radar do Tux -->
    <radialGradient id="tuxAura" cx="34%" cy="66%" r="22%">
      <stop offset="0%" stop-color="#1d4ed8" stop-opacity="0.20" />
      <stop offset="65%" stop-color="#0f172a" stop-opacity="0.08" />
      <stop offset="100%" stop-color="#000000" stop-opacity="0" />
    </radialGradient>

    <!-- Gradiente Metálico dos Tentáculos -->
    <linearGradient id="metalBody" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#64748b" />
      <stop offset="50%" stop-color="#475569" />
      <stop offset="100%" stop-color="#1e293b" />
    </linearGradient>

    <!-- Gradientes das Ferramentas -->
    <linearGradient id="screwdriverGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#facc15" />
      <stop offset="55%" stop-color="#eab308" />
      <stop offset="100%" stop-color="#ca8a04" />
    </linearGradient>

    <radialGradient id="bulbGlass" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#ffffff" />
      <stop offset="45%" stop-color="#fef08a" />
      <stop offset="100%" stop-color="#f59e0b" />
    </radialGradient>

    <radialGradient id="bulbHalo" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#facc15" stop-opacity="0.45" />
      <stop offset="100%" stop-color="#facc15" stop-opacity="0" />
    </radialGradient>

    <!-- Grade Arquitetônica / HUD de Fundo -->
    <pattern id="hudGrid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#0ea5e9" stroke-width="0.6" stroke-opacity="0.10" />
      <circle cx="40" cy="40" r="0.8" fill="#38bdf8" fill-opacity="0.22" />
    </pattern>

    <!-- Filtros de Brilho Neon (Glow) -->
    <filter id="cyanGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <filter id="cyanGlowSubtle" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <filter id="goldGlow" x="-40%" y="-40%" width="180%" height="180%">
      <feGaussianBlur stdDeviation="5" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <!-- Contraluz Ciano (Rim Light) para integrar o Tux ao ambiente escuro -->
    <filter id="tuxRimLight" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="4" dy="-2" stdDeviation="3" flood-color="#00e5ff" flood-opacity="0.45" />
      <feDropShadow dx="0" dy="8" stdDeviation="6" flood-color="#000000" flood-opacity="0.75" />
    </filter>
  </defs>

  <style>
    .font-ui {{ font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, Helvetica, Arial, sans-serif; }}
    .font-mono {{ font-family: 'JetBrains Mono', 'Fira Code', Consolas, monospace; }}

    .energy-pulse {{
      animation: pulseFlow 3.2s linear infinite;
    }}
    .ring-cw {{
      transform-origin: {cx}px {cy}px;
      animation: spinCW 24s linear infinite;
    }}
    .ring-ccw {{
      transform-origin: {cx}px {cy}px;
      animation: spinCCW 16s linear infinite;
    }}
    .radar-spin {{
      transform-origin: 412px 320px;
      animation: spinCW 32s linear infinite;
    }}
    .eye-scan {{
      animation: eyeLook 6s ease-in-out infinite;
    }}
    .cursor-blink {{
      animation: blink 1.1s step-end infinite;
    }}
    .spark-blink {{
      animation: blink 0.8s ease-in-out infinite alternate;
    }}
    .bulb-pulse {{
      animation: glowPulse 2.8s ease-in-out infinite alternate;
    }}

    @keyframes pulseFlow {{
      from {{ stroke-dashoffset: 208; }}
      to {{ stroke-dashoffset: 0; }}
    }}
    @keyframes spinCW {{
      from {{ transform: rotate(0deg); }}
      to {{ transform: rotate(360deg); }}
    }}
    @keyframes spinCCW {{
      from {{ transform: rotate(360deg); }}
      to {{ transform: rotate(0deg); }}
    }}
    @keyframes eyeLook {{
      0%, 100% {{ transform: translate(0px, 0px); }}
      35% {{ transform: translate(-5px, -2px); }}
      70% {{ transform: translate(-2px, 3px); }}
    }}
    @keyframes blink {{
      0%, 100% {{ opacity: 1; }}
      50% {{ opacity: 0.15; }}
    }}
    @keyframes glowPulse {{
      from {{ opacity: 0.55; }}
      to {{ opacity: 1; }}
    }}
  </style>

  <!-- 1. FUNDO E GRADE SCI-FI -->
  <rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="url(#bgGrad)" />
  <rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="url(#hudGrid)" />
  <rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="url(#coreAura)" />
  <rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="url(#tuxAura)" />

  <!-- Moldura Externa HUD Sutil -->
  <rect x="10" y="10" width="{WIDTH - 20}" height="{HEIGHT - 20}" rx="10" fill="none" stroke="#00e5ff" stroke-opacity="0.14" stroke-width="1" />

  <!-- 2. RADAR HOLOGRÁFICO ATRÁS DO TUX -->
  <g>
    <circle cx="412" cy="320" r="108" fill="#071226" fill-opacity="0.65" stroke="#1e3a8a" stroke-width="1.2" />
    <circle cx="412" cy="320" r="92" fill="none" stroke="#00e5ff" stroke-opacity="0.25" stroke-width="1.2" stroke-dasharray="6 8" class="radar-spin" />
    <circle cx="412" cy="320" r="74" fill="none" stroke="#1d4ed8" stroke-opacity="0.30" stroke-width="1" />
    <!-- Sombra de base do Tux -->
    <ellipse cx="412" cy="402" rx="68" ry="14" fill="#020617" opacity="0.85" />
    <ellipse cx="412" cy="402" rx="52" ry="8" fill="none" stroke="#00e5ff" stroke-opacity="0.35" stroke-width="1" filter="url(#cyanGlowSubtle)" />
  </g>

  <!-- 3. TENTÁCULOS DE SEGUNDO PLANO (ATRÁS DO TUX) -->
  {"".join(back_tentacles_svg)}

  <!-- 4. TUX (EMBUTIDO COM CONTRALUZ NEON) -->
  {tux_element}

  <!-- 5. TENTÁCULOS DE PRIMEIRO PLANO -->
  {"".join(front_tentacles_svg)}

  <!-- 6. NÚCLEO DE IA / OLHO BIOMECÂNICO (DIREITA) -->
  <g id="ai-core">
    <!-- Halo externo e base do núcleo -->
    <circle cx="{cx}" cy="{cy}" r="88" fill="#050b16" stroke="#1e293b" stroke-width="6" filter="url(#cyanGlowSubtle)" />
    <circle cx="{cx}" cy="{cy}" r="82" fill="none" stroke="#00e5ff" stroke-width="2" stroke-opacity="0.75" />

    <!-- 4 Nós Cardeais Brilhantes -->
    <circle cx="{cx}" cy="{cy - 82}" r="4.5" fill="#00e5ff" filter="url(#cyanGlow)" />
    <circle cx="{cx}" cy="{cy + 82}" r="4.5" fill="#00e5ff" filter="url(#cyanGlow)" />
    <circle cx="{cx - 82}" cy="{cy}" r="4.5" fill="#00e5ff" filter="url(#cyanGlow)" />
    <circle cx="{cx + 82}" cy="{cy}" r="4.5" fill="#00e5ff" filter="url(#cyanGlow)" />

    <!-- Anéis Concêntricos Animados -->
    <circle cx="{cx}" cy="{cy}" r="68" fill="none" stroke="#0284c7" stroke-width="2.5" stroke-dasharray="36 14 12 14" class="ring-cw" />
    <circle cx="{cx}" cy="{cy}" r="55" fill="none" stroke="#00e5ff" stroke-width="2" stroke-dasharray="50 18" class="ring-ccw" filter="url(#cyanGlowSubtle)" />
    <circle cx="{cx}" cy="{cy}" r="42" fill="#030811" stroke="#38bdf8" stroke-width="1.8" stroke-opacity="0.8" />
    <circle cx="{cx}" cy="{cy}" r="30" fill="#08172e" stroke="#00e5ff" stroke-width="1.5" />

    <!-- Pupila / Lente Óptica Animada -->
    <g class="eye-scan">
      <circle cx="{cx - 3}" cy="{cy}" r="18" fill="#020617" stroke="#00e5ff" stroke-width="2" filter="url(#cyanGlowSubtle)" />
      <!-- Crescente Ciano Luminoso -->
      <path d="M {cx - 5},{cy - 11} A 11,11 0 1,1 {cx - 5},{cy + 11} A 8,9 0 1,0 {cx - 5},{cy - 11} Z" fill="#38bdf8" filter="url(#cyanGlow)" />
      <!-- Reflexo da Lente -->
      <circle cx="{cx - 9}" cy="{cy - 4}" r="3.2" fill="#ffffff" opacity="0.95" />
    </g>
  </g>

  <!-- 7. TIPOGRAFIA E PAINEL HUD (CANTO SUPERIOR ESQUERDO — 100% LIVRE DE COLISÕES) -->
  <g transform="translate(68, 62)">
    <!-- Tag de Telemetria Superior -->
    <text x="0" y="0" fill="#38bdf8" font-size="10.5" font-weight="600" letter-spacing="2.5" class="font-mono" opacity="0.8">
      // SYS.IDENTITY : UFRN.ECT
    </text>

    <!-- Nome Principal com Destaque Neon -->
    <text x="0" y="30" fill="#00e5ff" font-size="16" font-weight="800" letter-spacing="3.6" class="font-ui" filter="url(#cyanGlowSubtle)">
      FERNANDO VICTOR OLIVEIRA DE ARAUJO
    </text>

    <!-- Formação / Instituição -->
    <text x="0" y="64" fill="#f8fafc" font-size="23" font-weight="700" letter-spacing="0.3" class="font-ui">
      Graduando em Ciência e Tecnologia · <tspan fill="#38bdf8">UFRN</tspan>
    </text>

    <!-- Linha Divisória Fina -->
    <line x1="0" y1="82" x2="455" y2="82" stroke="#1e293b" stroke-width="1.2" />

    <!-- Subtítulo + Cursor de Terminal Piscando -->
    <text x="0" y="108" fill="#94a3b8" font-size="14.5" font-weight="400" class="font-mono">
      Explorando tecnologia e descobrindo novos caminhos.<tspan fill="#00e5ff" font-weight="700" class="cursor-blink">_</tspan>
    </text>

    <!-- Barra de Progresso / Energia Ciano Brilhante -->
    <line x1="0" y1="132" x2="455" y2="132" stroke="#0f172a" stroke-width="3" stroke-linecap="round" />
    <line x1="0" y1="132" x2="215" y2="132" stroke="#00e5ff" stroke-width="3.5" stroke-linecap="round" filter="url(#cyanGlow)" />
    <circle cx="215" cy="132" r="3" fill="#ffffff" filter="url(#cyanGlow)" />
  </g>
</svg>
"""

    OUTPUT_SVG.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_SVG.write_text(svg_content, encoding="utf-8")
    print(f"[OK] Banner gerado com sucesso em: {OUTPUT_SVG}")


if __name__ == "__main__":
    generate_banner()
