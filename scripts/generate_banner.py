from math import cos, pi, sin, atan2, degrees
from pathlib import Path
import subprocess
import shutil
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
TUX_SOURCE = (ASSETS / 'tux.svg').read_text(encoding='utf-8')
TUX_START = TUX_SOURCE.index('>', TUX_SOURCE.index('<svg')) + 1
TUX_END = TUX_SOURCE.rfind('</svg>')
TUX_CONTENT = TUX_SOURCE[TUX_START:TUX_END]
FRAMES_DIR = ASSETS / '.frames'
WIDTH, HEIGHT = 1200, 440
FRAME_COUNT = 24
DURATION_MS = 145

ARMS = [
    ((-0.85, -0.52), (670, 82),  0.75, 'wrap_top'),
    ((-1.00, -0.03), (625, 220), 2.15, 'wrap_side'),
    ((-0.82,  0.55), (682, 380), 3.50, 'wrap_bottom'),
    (( 0.80, -0.55), (1078, 76), 4.10, 'book'),
    (( 0.95, -0.18), (1125, 222), 5.20, 'screw_tux'),
    (( 0.80,  0.56), (1062, 384), 0.10, 'bulb'),
]
CENTER = (878, 230)


def arm_svg(frame, spec, alert):
    (dx, dy), (ex, ey), phase, behavior = spec
    cx, cy = CENTER
    sx, sy = cx + dx * 69, cy + dy * 69
    nx, ny = -dy, dx
    cycle = 2 * pi * frame / FRAME_COUNT + phase
    wave = sin(cycle)
    wave2 = cos(2 * pi * frame / FRAME_COUNT + phase)
    if behavior == 'wrap_top':
        theta = -pi / 2 + .46 * sin(cycle)
        ex, ey = 320 + 86 * cos(theta), 280 + 130 * sin(theta)
    elif behavior == 'wrap_side':
        ex, ey = 420 + 8 * sin(cycle), 280 + 76 * sin(cycle)
    elif behavior == 'wrap_bottom':
        theta = pi / 2 + .46 * sin(cycle)
        ex, ey = 320 + 86 * cos(theta), 280 + 130 * sin(theta)
    elif behavior == 'book':
        ex, ey = 1078 + 5 * sin(cycle), 76 + 9 * cos(cycle)
    elif behavior == 'screw_tux':
        reach = .5 - .5 * cos(2 * pi * frame / FRAME_COUNT)
        ex, ey = 548 - 28 * reach, 246 + 20 * sin(cycle)
    elif behavior == 'bulb':
        ex, ey = 1062 + 7 * sin(cycle), 384 + 8 * cos(cycle)
    bend = (38 if behavior.startswith('wrap_') else 28) * wave
    if behavior == 'screw_tux':
        c1x, c1y = sx + 73, sy - 92 + 16 * wave
        c2x, c2y = ex + 224, 94 + 22 * wave2
    else:
        c1x, c1y = sx + (ex - sx) * .34 + nx * bend, sy + (ey - sy) * .34 + ny * bend
        c2x, c2y = sx + (ex - sx) * .72 - nx * 20 * wave2, sy + (ey - sy) * .72 - ny * 20 * wave2
    d = f'M {sx:.1f} {sy:.1f} C {c1x:.1f} {c1y:.1f}, {c2x:.1f} {c2y:.1f}, {ex:.1f} {ey:.1f}'
    angle = degrees(atan2(ey - c2y, ex - c2x))
    dash = (frame * 1.7 + phase * 8) % 22
    accent = '#ff4d63' if alert else '#49dce1'
    claw = '#ff99a6' if alert else '#9beee8'
    if behavior == 'book':
        prop = '''
          <g transform="translate(25 -20) rotate(-12)">
            <path d="M8 2Q0 -2 -10 1V30Q0 27 8 32Z" fill="#e9c98b" stroke="#f6e4bd" stroke-width="2"/>
            <path d="M8 2Q18 -2 29 1V30Q18 27 8 32Z" fill="#fff1d1" stroke="#f6e4bd" stroke-width="2"/>
            <path d="M8 2V32" stroke="#8e6540" stroke-width="2"/>
            <path d="M-5 8L4 10M-5 14L4 16M13 9L23 7M13 15L23 13" stroke="#9b8a70" stroke-width="1.4" stroke-linecap="round"/>
          </g>'''
    elif behavior == 'screw_tux':
        prop = '''
          <g transform="translate(21 0)">
            <rect x="0" y="-7" width="27" height="14" rx="6" fill="#e96856" stroke="#ffb49d" stroke-width="2"/>
            <path d="M27 0H69" stroke="#dbe5eb" stroke-width="5" stroke-linecap="round"/>
            <path d="M68 -5V5" stroke="#8fa5b2" stroke-width="3" stroke-linecap="round"/>
            <path d="M8 -4V4" stroke="#9a3b38" stroke-width="1.5"/>
          </g>'''
    elif behavior == 'bulb':
        prop = '''
          <g transform="translate(27 -8)">
            <path d="M0 9A13 13 0 1 1 24 9C21 13 19 16 19 20H5C5 16 3 13 0 9Z" fill="#ffdf79" stroke="#fff0bb" stroke-width="2"/>
            <path d="M7 22H17M8 26H16M10 30H14" stroke="#aabac2" stroke-width="3" stroke-linecap="round"/>
            <path d="M8 5Q11 1 15 4" fill="none" stroke="#fff9e4" stroke-width="2" stroke-linecap="round"/>
          </g>'''
    else:
        prop = ''
    return f'''
      <path d="{d}" fill="none" stroke="#07121e" stroke-width="28" stroke-linecap="round"/>
      <path d="{d}" fill="none" stroke="#284458" stroke-width="20" stroke-linecap="round"/>
      <path d="{d}" fill="none" stroke="url(#metal)" stroke-width="13" stroke-linecap="round" stroke-dasharray="10 8" stroke-dashoffset="-{dash:.1f}"/>
      <path d="{d}" fill="none" stroke="#d3e1e9" stroke-opacity=".62" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="3 15" stroke-dashoffset="-{dash:.1f}"/>
      <g transform="translate({ex:.1f} {ey:.1f}) rotate({angle:.1f})">
        {prop}
        <circle r="13" fill="#172b3a" stroke="#a9bfcd" stroke-width="3"/>
        <circle r="5" fill="{accent}"/>
        <path d="M 7 -4 L 22 -15 M 8 0 L 26 0 M 7 4 L 22 15" fill="none" stroke="{claw}" stroke-width="3.5" stroke-linecap="round"/>
        <path d="M 11 -5 L 23 -13 M 12 0 L 27 0 M 11 5 L 23 13" fill="none" stroke="#344d60" stroke-width="1.3"/>
        <circle cx="22" cy="-15" r="3" fill="#d3e1e9"/><circle cx="26" cy="0" r="3" fill="#d3e1e9"/><circle cx="22" cy="15" r="3" fill="#d3e1e9"/>
      </g>
    '''


def make_svg(frame=0):
    alert = 8 <= frame <= 12
    accent = '#ff4058' if alert else '#2cd0dc'
    iris = '#ff4d63' if alert else '#32d7de'
    pupil = '#ffe4e8' if alert else '#c5fff4'
    eye_x = 878 - 10 + 5 * sin(2 * pi * frame / FRAME_COUNT)
    eye_y = 230 + 2.2 * cos(2 * pi * frame / FRAME_COUNT)
    arms = ''.join(arm_svg(frame, spec, alert) for spec in ARMS)
    pulse = .15 + .08 * (1 + sin(2 * pi * frame / FRAME_COUNT))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">
      <defs>
        <linearGradient id="bg" x2="1" y2="1"><stop stop-color="#081522"/><stop offset=".6" stop-color="#0b1725"/><stop offset="1" stop-color="#11152a"/></linearGradient>
        <linearGradient id="metal" x2="0" y2="1"><stop stop-color="#d6e2e9"/><stop offset=".44" stop-color="#819aaa"/><stop offset="1" stop-color="#405b6e"/></linearGradient>
        <radialGradient id="halo"><stop stop-color="#13b9d2" stop-opacity=".34"/><stop offset="1" stop-color="#13b9d2" stop-opacity="0"/></radialGradient>
        <pattern id="grid" width="34" height="34" patternUnits="userSpaceOnUse"><path d="M34 0H0V34" fill="none" stroke="#89a8bb" stroke-opacity=".07"/></pattern>
        <filter id="blur"><feGaussianBlur stdDeviation="24"/></filter>
        <filter id="soft"><feGaussianBlur stdDeviation="4"/></filter>
        <clipPath id="eyeClip"><circle cx="878" cy="230" r="22"/></clipPath>
      </defs>
      <rect width="1200" height="440" rx="18" fill="url(#bg)"/>
      <rect width="1200" height="440" rx="18" fill="url(#grid)"/>
      <ellipse cx="881" cy="228" rx="335" ry="240" fill="url(#halo)"/>
      <g fill="#75dfe2" opacity=".6"><circle cx="544" cy="93" r="2"/><circle cx="605" cy="359" r="2"/><circle cx="1145" cy="111" r="2"/><circle cx="1163" cy="334" r="2"/><circle cx="460" cy="166" r="1.7"/></g>
      <path d="M40 105H500" stroke="#234253" stroke-width="1"/>
      <text x="52" y="59" fill="#8af1e8" font-family="Arial, sans-serif" font-size="13" font-weight="700" letter-spacing="3">FERNANDO VICTOR OLIVEIRA DE ARAUJO</text>
      <text x="50" y="91" fill="#eaf2f7" font-family="Arial, sans-serif" font-size="17" font-weight="600">Graduando em Ciência e Tecnologia · UFRN</text>
      <text x="50" y="132" fill="#9eb1bf" font-family="Arial, sans-serif" font-size="14">Explorando tecnologia e descobrindo novos caminhos.</text>
      <path d="M50 177H331" stroke="#28c4d7" stroke-width="2"/>
      <g opacity=".8"><circle cx="320" cy="288" r="128" fill="#122435"/><circle cx="320" cy="288" r="111" fill="none" stroke="#234458" stroke-width="1.5"/><circle cx="320" cy="288" r="102" fill="none" stroke="#2e5768" stroke-width="1" stroke-dasharray="2 9"/></g>
      <svg x="230" y="170" width="180" height="213" viewBox="0 0 216 256" preserveAspectRatio="xMidYMid meet">{TUX_CONTENT}</svg>
      <!-- braços móveis do agente -->
      {arms}
      <!-- corpo do agente e olho central -->
      <g>
        <circle cx="878" cy="230" r="82" fill="#0a1420" stroke="#29495b" stroke-width="8"/>
        <circle cx="878" cy="230" r="68" fill="#102332" stroke="#a5bbc7" stroke-width="2.5"/>
        <circle cx="878" cy="230" r="54" fill="#0a1825" stroke="#2cd0dc" stroke-width="3"/>
        <circle cx="878" cy="230" r="37" fill="#102d3b" stroke="#6997a9" stroke-width="2"/>
        <circle cx="878" cy="230" r="26" fill="#06202d" stroke="{accent}" stroke-width="2"/>
        <g clip-path="url(#eyeClip)">
          <circle cx="{eye_x:.2f}" cy="{eye_y:.2f}" r="19" fill="{iris}" opacity="{pulse:.3f}" filter="url(#soft)"/>
          <ellipse cx="{eye_x:.2f}" cy="{eye_y:.2f}" rx="14" ry="15" fill="{iris}" stroke="{pupil}" stroke-width="2"/>
          <ellipse cx="{eye_x:.2f}" cy="{eye_y:.2f}" rx="8" ry="10" fill="#071923"/>
          <circle cx="{eye_x - 3:.2f}" cy="{eye_y - 4:.2f}" r="3.5" fill="{pupil}"/>
        </g>
        <circle cx="878" cy="148" r="5" fill="{accent}"/><circle cx="960" cy="230" r="5" fill="{accent}"/>
        <circle cx="878" cy="312" r="5" fill="{accent}"/><circle cx="796" cy="230" r="5" fill="{accent}"/>
      </g>
    </svg>'''


def main():
    FRAMES_DIR.mkdir(parents=True, exist_ok=True)
    clean_svg = lambda frame: '\n'.join(line.rstrip() for line in make_svg(frame).splitlines()) + '\n'
    (ASSETS / 'profile-banner.svg').write_text(clean_svg(0), encoding='utf-8')
    for i in range(FRAME_COUNT):
        svg = FRAMES_DIR / f'frame-{i:02d}.svg'
        png = FRAMES_DIR / f'frame-{i:02d}.png'
        svg.write_text(clean_svg(i), encoding='utf-8')
        subprocess.run(['rsvg-convert', '-w', str(WIDTH), '-h', str(HEIGHT), str(svg), '-o', str(png)], check=True)
    frames = [Image.open(FRAMES_DIR / f'frame-{i:02d}.png').convert('RGB').convert('P', palette=Image.Palette.ADAPTIVE, colors=128) for i in range(FRAME_COUNT)]
    frames[0].save(ASSETS / 'profile-banner.gif', save_all=True, append_images=frames[1:], duration=DURATION_MS, loop=0, optimize=True, disposal=2)
    # Save a clean still preview at the same resolution as the animated banner.
    Image.open(FRAMES_DIR / 'frame-00.png').save(ASSETS / 'profile-banner.png')
    shutil.rmtree(FRAMES_DIR)
    print(f'Wrote SVG, GIF ({FRAME_COUNT} frames), and PNG to {ASSETS}')


if __name__ == '__main__':
    main()
