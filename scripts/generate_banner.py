#!/usr/bin/env python3
"""
Gerador do Banner Exuberante Animado para o GitHub Profile (xoykor)
Lê assets/tux.svg e gera:
  - assets/profile-banner.gif (Banner animado com tentáculos em movimento e modo Alerta Vermelho)
  - assets/profile-banner.svg (Versão vetorial do frame base)
  - assets/profile-banner.png (Preview estático em alta resolução)
"""

import base64
import concurrent.futures
import math
import shutil
import subprocess
from pathlib import Path
from PIL import Image

ROOT_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = ROOT_DIR / "assets"
TUX_PATH = ASSETS_DIR / "tux.svg"
OUTPUT_GIF = ASSETS_DIR / "profile-banner.gif"
OUTPUT_SVG = ASSETS_DIR / "profile-banner.svg"
OUTPUT_PNG = ASSETS_DIR / "profile-banner.png"
FRAMES_DIR = ASSETS_DIR / ".banner_frames"

WIDTH = 1200
HEIGHT = 480
FRAME_COUNT = 24
DURATION_MS = 125  # ~8 FPS para animação fluida e leve em GIF


def load_tux_data_uri(svg_path: Path) -> str:
    """Embute o tux.svg em base64 para funcionar perfeitamente em qualquer renderizador."""
    if svg_path.exists():
        raw_bytes = svg_path.read_bytes()
        b64 = base64.b64encode(raw_bytes).decode("utf-8")
        return f"data:image/svg+xml;base64,{b64}"
    return ""


def bezier_point(t: float, p0: tuple, p1: tuple, p2: tuple, p3: tuple) -> tuple:
    """Calcula ponto (x, y) em uma curva de Bézier cúbica."""
    u = 1 - t
    x = (u**3) * p0[0] + 3 * (u**2) * t * p1[0] + 3 * u * (t**2) * p2[0] + (t**3) * p3[0]
    y = (u**3) * p0[1] + 3 * (u**2) * t * p1[1] + 3 * u * (t**2) * p2[1] + (t**3) * p3[1]
    return x, y


def bezier_tangent_angle(t: float, p0: tuple, p1: tuple, p2: tuple, p3: tuple) -> float:
    """Calcula o ângulo tangente em graus no ponto t da curva de Bézier cúbica."""
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
    pulse_offset: float = 0.0,
    energy_color: str = "#00e5ff",
    energy_glow: str = "url(#cyanGlow)",
) -> str:
    """Gera o corpo do tentáculo mecânico segmentado com sombra, relevo e pulso neon."""
    path_d = f"M {p0[0]:.1f},{p0[1]:.1f} C {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f} {p3[0]:.1f},{p3[1]:.1f}"

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
        <!-- Feixe de energia neon pulsante -->
        <path d="{path_d}" fill="none" stroke="{energy_color}" stroke-width="2.2" stroke-linecap="round" stroke-dasharray="14 90" stroke-dashoffset="-{pulse_offset:.1f}" filter="{energy_glow}" />
        <!-- Pontos de reflexo metálico calculados dinamicamente na curva -->
        {highlights_svg}
      </g>
    """


def build_claw(
    x: float,
    y: float,
    angle: float,
    scale: float = 1.0,
    tool: str = "none",
    tool_anim: float = 0.0,
    accent_color: str = "#00e5ff",
    accent_glow: str = "url(#cyanGlowSubtle)",
) -> str:
    """Desenha a garra robótica articulada e a ferramenta acoplada na ponta."""
    tool_svg = ""
    if tool == "screwdriver":
        # Chave de fenda amarela com faíscas animadas
        spark_r = 2.4 + 1.4 * math.sin(tool_anim * 2)
        spark_op = 0.5 + 0.5 * math.sin(tool_anim * 2) ** 2
        tool_svg = f"""
        <g transform="rotate(15) translate(16, 0)">
          <!-- Haste metálica -->
          <rect x="28" y="-2.2" width="38" height="4.4" rx="1.5" fill="#cbd5e1" stroke="#0f172a" stroke-width="1.5" />
          <polygon points="66,-2.2 75,-0.8 75,0.8 66,2.2" fill="{accent_color}" filter="{accent_glow}" />
          <!-- Cabo isolado amarelo/âmbar -->
          <rect x="0" y="-8" width="30" height="16" rx="5" fill="url(#screwdriverGrad)" stroke="#0f172a" stroke-width="2" />
          <line x1="8" y1="-5" x2="22" y2="-5" stroke="#fef08a" stroke-width="1.8" stroke-linecap="round" opacity="0.8" />
          <line x1="8" y1="0" x2="22" y2="0" stroke="#78350f" stroke-width="1.8" stroke-linecap="round" opacity="0.5" />
          <!-- Faíscas de energia na ponta -->
          <circle cx="77" cy="0" r="{spark_r:.1f}" fill="{accent_color}" opacity="{spark_op:.2f}" filter="{accent_glow}" />
        </g>
        """
    elif tool == "paper":
        # Folha de código / documento com leve flutuação
        paper_rot = 20 + 4 * math.sin(tool_anim)
        tool_svg = f"""
        <g transform="rotate({paper_rot:.1f}) translate(12, -18)">
          <path d="M 0,0 L 36,-6 L 44,36 L 8,42 Z" fill="#f8fafc" stroke="#0f172a" stroke-width="2" filter="url(#cyanGlowSubtle)" />
          <path d="M 6,6 L 30,2 L 36,32 L 12,36 Z" fill="#e2e8f0" opacity="0.4" />
          <!-- Linhas de código estilizadas -->
          <line x1="8" y1="9" x2="22" y2="7" stroke="#0284c7" stroke-width="2.5" stroke-linecap="round" />
          <line x1="10" y1="16" x2="31" y2="13" stroke="#334155" stroke-width="2" stroke-linecap="round" />
          <line x1="11" y1="22" x2="27" y2="19" stroke="{accent_color}" stroke-width="2" stroke-linecap="round" />
          <line x1="13" y1="29" x2="33" y2="26" stroke="#334155" stroke-width="2" stroke-linecap="round" />
        </g>
        """
    elif tool == "bulb":
        # Lâmpada de ideia com pulso de brilho dourado
        halo_r = 26 + 6 * math.sin(tool_anim)
        halo_op = 0.40 + 0.25 * math.sin(tool_anim)
        tool_svg = f"""
        <g transform="rotate(-15) translate(14, 0)">
          <!-- Halo de luz dourada pulsante -->
          <circle cx="34" cy="0" r="{halo_r:.1f}" fill="url(#bulbHalo)" opacity="{halo_op:.2f}" />
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
        <!-- Articulação / Punho com anel neon reativo -->
        <circle cx="0" cy="0" r="12" fill="#091324" stroke="{accent_color}" stroke-width="2" filter="{accent_glow}" />
        <circle cx="0" cy="0" r="6" fill="#334155" stroke="{accent_color}" stroke-width="1.2" />
        <circle cx="0" cy="0" r="2.2" fill="{accent_color}" />
      </g>
    """


def make_frame_svg(frame: int, tux_uri: str) -> str:
    """Gera o código SVG para um frame específico com cinemática dos tentáculos e modo Alerta Vermelho."""
    # Coordenadas do Núcleo Robótico (Direita)
    cx, cy = 875, 255
    phase_base = 2 * math.pi * frame / FRAME_COUNT

    # --- Modo de Alerta Vermelho (Frames 8 a 13: alcance máximo da chave de fenda) ---
    is_alert = 8 <= frame <= 13

    if is_alert:
        # Paleta Neon Vermelha / Carmesim de Alerta
        accent_color = "#ff2a55"
        accent_glow = "url(#redGlow)"
        accent_glow_subtle = "url(#redGlowSubtle)"
        ring_color = "#ff3366"
        crescent_color = "#ff2a55"
        pupil_halo_color = "#ff0044"
        pupil_halo_op = "0.45"
        radar_alert_stroke = "#ef4444"
        hud_alert_tag = '<tspan fill="#ff2a55" font-weight="700"> [SCAN.ALERT]</tspan>'
    else:
        # Paleta Neon Ciano / Azul padrão
        accent_color = "#00e5ff"
        accent_glow = "url(#cyanGlow)"
        accent_glow_subtle = "url(#cyanGlowSubtle)"
        ring_color = "#00e5ff"
        crescent_color = "#38bdf8"
        pupil_halo_color = "#00e5ff"
        pupil_halo_op = "0.15"
        radar_alert_stroke = "#00e5ff"
        hud_alert_tag = ""

    # --- Ângulos de Rotação e Cinemática ---
    rot_cw = (frame / FRAME_COUNT) * 360.0
    rot_ccw = -(frame / FRAME_COUNT) * 360.0
    radar_rot = (frame / FRAME_COUNT) * 360.0

    # Movimento de varredura da pupila / olho óptico
    eye_dx = -3 + 5.0 * math.sin(phase_base)
    eye_dy = 2.8 * math.cos(phase_base)

    # Piscar do cursor do terminal no HUD
    cursor_op = "1" if (frame % 12) < 7 else "0.1"

    # --- Cinemática dos 6 Tentáculos ---
    # 1. Tentáculo de fundo (passa por trás do Tux, ondulando)
    cyc1 = phase_base + 0.8
    t1_p0 = (cx - 45, cy + 10)
    t1_p3 = (435 + 24 * math.cos(cyc1), 345 + 18 * math.sin(cyc1))
    t1_p1 = (690 + 20 * math.sin(cyc1), 275 + 15 * math.cos(cyc1))
    t1_p2 = (550 - 15 * math.cos(cyc1), 315 + 22 * math.sin(cyc1))

    # 2. Tentáculo superior direito (segurando o código/papel, flutuando suavemente)
    cyc2 = phase_base + 2.0
    t2_p0 = (cx + 40, cy - 40)
    t2_p3 = (1070 + 16 * math.cos(cyc2), 95 + 18 * math.sin(cyc2))
    t2_p1 = (960 + 12 * math.sin(cyc2), 175 - 10 * math.cos(cyc2))
    t2_p2 = (1025 + 14 * math.cos(cyc2), 130 + 12 * math.sin(cyc2))

    # 3. Tentáculo inferior direito (segurando a lâmpada com brilho pulsante)
    cyc3 = phase_base + 3.8
    t3_p0 = (cx + 45, cy + 35)
    t3_p3 = (1055 + 18 * math.cos(cyc3), 405 + 14 * math.sin(cyc3))
    t3_p1 = (965 + 14 * math.sin(cyc3), 310 + 12 * math.cos(cyc3))
    t3_p2 = (1015 - 12 * math.cos(cyc3), 360 + 16 * math.sin(cyc3))

    # 4. Tentáculo superior esquerdo (curvado abaixo do texto, ondulando em direção à cabeça do Tux)
    cyc4 = phase_base + 1.2
    t4_p0 = (cx - 35, cy - 42)
    t4_p3 = (415 + 22 * math.cos(cyc4), 210 + 16 * math.sin(cyc4))
    t4_p1 = (710 + 20 * math.cos(cyc4), 160 + 14 * math.sin(cyc4))
    t4_p2 = (535 - 18 * math.sin(cyc4), 190 + 15 * math.cos(cyc4))

    # 5. Tentáculo médio esquerdo (segurando a chave de fenda e alcançando o Tux)
    cyc5 = phase_base + 0.5
    reach = 0.5 - 0.5 * math.cos(phase_base)  # Movimento de vai-e-vem fluido (ápice nos frames 11-13)
    t5_p0 = (cx - 50, cy - 18)
    t5_p3 = (565 - 38 * reach, 265 + 18 * math.sin(cyc5))
    t5_p1 = (725 - 15 * reach + 18 * math.sin(cyc5), 200 + 12 * math.cos(cyc5))
    t5_p2 = (635 - 28 * reach, 230 + 20 * math.sin(cyc5))

    # 6. Tentáculo inferior esquerdo (passando abaixo dos pés do Tux)
    cyc6 = phase_base + 4.2
    t6_p0 = (cx - 40, cy + 35)
    t6_p3 = (345 + 28 * math.cos(cyc6), 425 + 12 * math.sin(cyc6))
    t6_p1 = (675 + 22 * math.sin(cyc6), 340 + 15 * math.cos(cyc6))
    t6_p2 = (505 - 18 * math.cos(cyc6), 395 + 16 * math.sin(cyc6))

    tentacles_specs = [
        ("t-back-mid", t1_p0, t1_p1, t1_p2, t1_p3, 17, 0.60, (frame * 5.5 + 20) % 104, "none", cyc1, "#00e5ff", "url(#cyanGlow)"),
        ("t-top-right", t2_p0, t2_p1, t2_p2, t2_p3, 18, 0.90, (frame * 6.0 + 40) % 104, "paper", cyc2, "#00e5ff", "url(#cyanGlow)"),
        ("t-bot-right", t3_p0, t3_p1, t3_p2, t3_p3, 18, 0.90, (frame * 6.0 + 70) % 104, "bulb", cyc3, "#00e5ff", "url(#cyanGlow)"),
        ("t-top-left", t4_p0, t4_p1, t4_p2, t4_p3, 20, 0.95, (frame * 6.5 + 0) % 104, "none", cyc4, "#00e5ff", "url(#cyanGlow)"),
        ("t-mid-left", t5_p0, t5_p1, t5_p2, t5_p3, 19, 1.00, (frame * 7.0 + 50) % 104, "screwdriver", cyc5, accent_color, accent_glow),
        ("t-bot-left", t6_p0, t6_p1, t6_p2, t6_p3, 20, 1.00, (frame * 6.2 + 85) % 104, "none", cyc6, "#00e5ff", "url(#cyanGlow)"),
    ]

    back_tentacles_svg = []
    front_tentacles_svg = []

    for tid, p0, p1, p2, p3, thick, opac, pulse_off, tool, anim_val, en_col, en_glow in tentacles_specs:
        t_svg = build_tentacle(tid, p0, p1, p2, p3, thick, opac, pulse_off, energy_color=en_col, energy_glow=en_glow)
        end_angle = bezier_tangent_angle(1.0, p0, p1, p2, p3)
        c_svg = build_claw(
            p3[0],
            p3[1],
            end_angle,
            scale=0.95,
            tool=tool,
            tool_anim=anim_val,
            accent_color=accent_color if (is_alert and tool == "screwdriver") else "#00e5ff",
            accent_glow=accent_glow_subtle if (is_alert and tool == "screwdriver") else "url(#cyanGlowSubtle)",
        )
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

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" width="{WIDTH}" height="{HEIGHT}">
  <defs>
    <!-- Gradiente de Fundo Sci-Fi Profundo -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#04070d" />
      <stop offset="50%" stop-color="#07101e" />
      <stop offset="100%" stop-color="#03060c" />
    </linearGradient>

    <!-- Halo Radial do Núcleo de IA -->
    <radialGradient id="coreAura" cx="73%" cy="53%" r="42%">
      <stop offset="0%" stop-color="{accent_color}" stop-opacity="0.25" />
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

    <!-- Filtros de Brilho Ciano Neon -->
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

    <!-- Filtros de Brilho Vermelho Neon (Modo Alerta) -->
    <filter id="redGlow" x="-30%" y="-30%" width="160%" height="160%">
      <feGaussianBlur stdDeviation="4" result="blur" />
      <feMerge>
        <feMergeNode in="blur" />
        <feMergeNode in="SourceGraphic" />
      </feMerge>
    </filter>

    <filter id="redGlowSubtle" x="-20%" y="-20%" width="140%" height="140%">
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
  </style>

  <!-- 1. FUNDO E GRADE SCI-FI -->
  <rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="url(#bgGrad)" />
  <rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="url(#hudGrid)" />
  <rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="url(#coreAura)" />
  <rect width="{WIDTH}" height="{HEIGHT}" rx="14" fill="url(#tuxAura)" />

  <!-- Moldura Externa HUD Sutil -->
  <rect x="10" y="10" width="{WIDTH - 20}" height="{HEIGHT - 20}" rx="10" fill="none" stroke="{accent_color}" stroke-opacity="0.14" stroke-width="1" />

  <!-- 2. RADAR HOLOGRÁFICO ATRÁS DO TUX (COM ROTAÇÃO SINCRONIZADA) -->
  <g>
    <circle cx="412" cy="320" r="108" fill="#071226" fill-opacity="0.65" stroke="#1e3a8a" stroke-width="1.2" />
    <circle cx="412" cy="320" r="92" fill="none" stroke="{radar_alert_stroke}" stroke-opacity="0.25" stroke-width="1.2" stroke-dasharray="6 8" transform="rotate({radar_rot:.1f} 412 320)" />
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
    <circle cx="{cx}" cy="{cy}" r="88" fill="#050b16" stroke="#1e293b" stroke-width="6" filter="{accent_glow_subtle}" />
    <circle cx="{cx}" cy="{cy}" r="82" fill="none" stroke="{ring_color}" stroke-width="2" stroke-opacity="0.85" />

    <!-- 4 Nós Cardeais Brilhantes (Reativos ao Alerta) -->
    <circle cx="{cx}" cy="{cy - 82}" r="4.5" fill="{accent_color}" filter="{accent_glow}" />
    <circle cx="{cx}" cy="{cy + 82}" r="4.5" fill="{accent_color}" filter="{accent_glow}" />
    <circle cx="{cx - 82}" cy="{cy}" r="4.5" fill="{accent_color}" filter="{accent_glow}" />
    <circle cx="{cx + 82}" cy="{cy}" r="4.5" fill="{accent_color}" filter="{accent_glow}" />

    <!-- Anéis Concêntricos Mecânicos com Rotação Oposta -->
    <circle cx="{cx}" cy="{cy}" r="68" fill="none" stroke="#0284c7" stroke-width="2.5" stroke-dasharray="36 14 12 14" transform="rotate({rot_cw:.1f} {cx} {cy})" />
    <circle cx="{cx}" cy="{cy}" r="55" fill="none" stroke="{ring_color}" stroke-width="2" stroke-dasharray="50 18" transform="rotate({rot_ccw:.1f} {cx} {cy})" filter="{accent_glow_subtle}" />
    <circle cx="{cx}" cy="{cy}" r="42" fill="#030811" stroke="#38bdf8" stroke-width="1.8" stroke-opacity="0.8" />
    <circle cx="{cx}" cy="{cy}" r="30" fill="#08172e" stroke="{ring_color}" stroke-width="1.5" />

    <!-- Pupila / Lente Óptica com Varredura Ativa e Mudança de Cor (Ciano <-> Vermelho) -->
    <g transform="translate({eye_dx:.1f}, {eye_dy:.1f})">
      <!-- Halo interno da pupila -->
      <circle cx="{cx}" cy="{cy}" r="16" fill="{pupil_halo_color}" opacity="{pupil_halo_op}" filter="{accent_glow}" />
      <circle cx="{cx}" cy="{cy}" r="18" fill="#020617" stroke="{ring_color}" stroke-width="2" filter="{accent_glow_subtle}" />
      <!-- Crescente Luminoso (Vermelho no modo alerta / Ciano no padrão) -->
      <path d="M {cx - 2},{cy - 11} A 11,11 0 1,1 {cx - 2},{cy + 11} A 8,9 0 1,0 {cx - 2},{cy - 11} Z" fill="{crescent_color}" filter="{accent_glow}" />
      <!-- Reflexo de Lente Especular Branco -->
      <circle cx="{cx - 6}" cy="{cy - 4}" r="3.2" fill="#ffffff" opacity="0.95" />
    </g>
  </g>

  <!-- 7. TIPOGRAFIA E PAINEL HUD (CANTO SUPERIOR ESQUERDO) -->
  <g transform="translate(68, 62)">
    <!-- Tag de Telemetria Superior (Indica Alerta Dinâmico) -->
    <circle cx="-10" cy="-3.5" r="3" fill="{accent_color}" filter="{accent_glow}" />
    <text x="0" y="0" fill="#38bdf8" font-size="10.5" font-weight="600" letter-spacing="2.5" class="font-mono" opacity="0.8">
      // SYS.IDENTITY : UFRN.ECT{hud_alert_tag}
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
      Explorando tecnologia e descobrindo novos caminhos.<tspan fill="#00e5ff" font-weight="700" opacity="{cursor_op}">_</tspan>
    </text>

    <!-- Barra de Progresso / Energia Ciano Brilhante -->
    <line x1="0" y1="132" x2="455" y2="132" stroke="#0f172a" stroke-width="3" stroke-linecap="round" />
    <line x1="0" y1="132" x2="215" y2="132" stroke="#00e5ff" stroke-width="3.5" stroke-linecap="round" filter="url(#cyanGlow)" />
    <circle cx="215" cy="132" r="3" fill="#ffffff" filter="url(#cyanGlow)" />
  </g>
</svg>
"""


def convert_svg_to_png(svg_path: Path, png_path: Path) -> None:
    """Renderiza um arquivo SVG em PNG via rsvg-convert mantendo máxima fidelidade vetorial."""
    subprocess.run(
        ["rsvg-convert", "-w", str(WIDTH), "-h", str(HEIGHT), str(svg_path), "-o", str(png_path)],
        check=True,
    )


def generate_all() -> None:
    print("[*] Carregando Tux SVG...")
    tux_uri = load_tux_data_uri(TUX_PATH)

    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    svg_files = []
    png_files = []

    print(f"[*] Gerando {FRAME_COUNT} frames vetoriais (incluindo Alerta Vermelho nos frames 8-13)...")
    for i in range(FRAME_COUNT):
        frame_svg_code = make_frame_svg(i, tux_uri)
        svg_file = FRAMES_DIR / f"frame_{i:02d}.svg"
        png_file = FRAMES_DIR / f"frame_{i:02d}.png"
        svg_file.write_text(frame_svg_code, encoding="utf-8")
        svg_files.append(svg_file)
        png_files.append(png_file)

        # Salva o frame 0 como a versão SVG estática principal
        if i == 0:
            OUTPUT_SVG.write_text(frame_svg_code, encoding="utf-8")

    print("[*] Renderizando frames PNG em paralelo...")
    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = [
            executor.submit(convert_svg_to_png, svg_p, png_p)
            for svg_p, png_p in zip(svg_files, png_files)
        ]
        for f in concurrent.futures.as_completed(futures):
            f.result()

    print("[*] Montando GIF animado com paleta unificada (Ciano + Alerta Vermelho)...")
    rgb_frames = [Image.open(p).convert("RGB") for p in png_files]

    # Amostra o frame normal (0) e o frame de alerta máximo (10) para compor a paleta perfeita
    palette_sample = Image.new("RGB", (1200, 960))
    palette_sample.paste(rgb_frames[0], (0, 0))
    palette_sample.paste(rgb_frames[10], (0, 480))
    unified_palette = palette_sample.quantize(colors=256, method=Image.Quantize.MEDIANCUT)

    quantized_frames = [
        f.quantize(palette=unified_palette, dither=Image.Dither.NONE)
        for f in rgb_frames
    ]

    quantized_frames[0].save(
        OUTPUT_GIF,
        save_all=True,
        append_images=quantized_frames[1:],
        duration=DURATION_MS,
        loop=0,
        disposal=2,
    )

    # Salva preview estático em PNG de alta resolução
    rgb_frames[0].save(OUTPUT_PNG)

    # Limpeza dos frames temporários
    shutil.rmtree(FRAMES_DIR)

    print(f"[OK] GIF gerado com sucesso em: {OUTPUT_GIF}")
    print(f"[OK] SVG gerado com sucesso em: {OUTPUT_SVG}")
    print(f"[OK] PNG gerado com sucesso em: {OUTPUT_PNG}")


if __name__ == "__main__":
    generate_all()
