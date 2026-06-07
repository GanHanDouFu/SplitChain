"""
Generate architecture diagrams for SplitChain project.
Node Pulse aesthetic: dark backgrounds, electric blue palette, circuit-board precision.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import os

# === Font Setup ===
# Use SimHei for Chinese, DejaVu Sans Mono for code
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Noto Sans SC', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

MONO = 'Consolas'

# === Color Palette ===
BG = '#0a0e17'
BG_CARD = '#111827'
BG_CARD_LIGHT = '#1a2332'
BORDER = '#1e3a5f'
BLUE = '#3b82f6'
BLUE_LIGHT = '#60a5fa'
CYAN = '#06b6d4'
GREEN = '#10b981'
PURPLE = '#8b5cf6'
AMBER = '#f59e0b'
TEXT = '#e2e8f0'
TEXT_DIM = '#64748b'
TEXT_MUTED = '#475569'

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def add_glow(ax, x, y, radius=0.03, color=BLUE, alpha=0.15):
    for r in np.linspace(radius * 3, radius, 6):
        circle = plt.Circle((x, y), r, color=color, alpha=alpha * (r / (radius * 3)), zorder=1)
        ax.add_patch(circle)


def draw_box(ax, x, y, w, h, label, sublabel=None, color=BLUE, icon_text=None, fontsize=11):
    # Shadow
    shadow = FancyBboxPatch((x + 0.006, y - 0.006), w, h,
                             boxstyle="round,pad=0.012",
                             facecolor='#000000', edgecolor='none',
                             alpha=0.3, zorder=2)
    ax.add_patch(shadow)

    # Main box
    box = FancyBboxPatch((x, y), w, h,
                          boxstyle="round,pad=0.012",
                          facecolor=BG_CARD, edgecolor=color,
                          linewidth=1.5, zorder=3)
    ax.add_patch(box)

    # Top accent line
    accent = FancyBboxPatch((x + 0.01, y + h - 0.006), w - 0.02, 0.004,
                             boxstyle="round,pad=0.002",
                             facecolor=color, edgecolor='none',
                             alpha=0.8, zorder=4)
    ax.add_patch(accent)

    # Icon text (replacing emoji)
    if icon_text:
        ax.text(x + w / 2, y + h - 0.03, icon_text,
                fontsize=14, ha='center', va='center',
                color=color, zorder=5, fontweight='bold',
                fontfamily=MONO)

    # Label
    label_y = y + h / 2 - (0.01 if sublabel else 0)
    if icon_text:
        label_y = y + h / 2 - 0.008

    ax.text(x + w / 2, label_y, label,
            fontsize=fontsize, ha='center', va='center',
            color=TEXT, fontweight='bold', zorder=5)

    if sublabel:
        ax.text(x + w / 2, y + 0.022, sublabel,
                fontsize=7.5, ha='center', va='center',
                color=TEXT_DIM, zorder=5, style='italic',
                fontfamily=MONO)

    add_glow(ax, x + w / 2, y + h, radius=0.012, color=color, alpha=0.06)


def draw_arrow(ax, x1, y1, x2, y2, color=BLUE, label=None, style='->', lw=1.5):
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                             arrowstyle=style,
                             color=color, linewidth=lw,
                             connectionstyle="arc3,rad=0",
                             mutation_scale=15, zorder=4)
    ax.add_patch(arrow)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        ax.text(mx + 0.008, my, label,
                fontsize=7, ha='left', va='center',
                color=TEXT_DIM, zorder=5, style='italic',
                fontfamily=MONO)


def draw_layer_label(ax, x, y, label, color=BLUE):
    ax.plot([x - 0.02, x + 0.18], [y, y], color=color, linewidth=0.5, alpha=0.3, zorder=2)
    ax.text(x, y + 0.012, label,
            fontsize=8, ha='left', va='bottom',
            color=color, fontweight='bold', zorder=5,
            fontfamily=MONO, alpha=0.7)


def draw_grid_dots(ax):
    for xi in np.linspace(0.05, 0.95, 18):
        for yi in np.linspace(0.02, 0.98, 12):
            ax.plot(xi, yi, '.', color=TEXT_MUTED, alpha=0.03, markersize=1, zorder=0)


# ============================================================
# DIAGRAM 1: System Architecture
# ============================================================
def create_architecture():
    fig, ax = plt.subplots(1, 1, figsize=(14, 9), dpi=200)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Title
    ax.text(0.5, 0.96, 'SPLITCHAIN', fontsize=28, ha='center', va='center',
            color=BLUE, fontweight='bold', fontfamily=MONO, alpha=0.9)
    ax.text(0.5, 0.925, 'AI Agent On-Chain Payment Splitting System',
            fontsize=10, ha='center', va='center',
            color=TEXT_DIM, fontfamily=MONO)
    ax.plot([0.15, 0.85], [0.91, 0.91], color=BLUE, linewidth=0.5, alpha=0.3)

    # === Layer 1: User Layer ===
    draw_layer_label(ax, 0.06, 0.83, '[ USER LAYER ]', CYAN)

    draw_box(ax, 0.12, 0.73, 0.24, 0.09,
             'Natural Language Input',
             '"split 1 ETH 3:3:4 to A B C"',
             CYAN, icon_text='>', fontsize=10)

    draw_box(ax, 0.64, 0.73, 0.24, 0.09,
             'Web Frontend',
             'MetaMask + Browser',
             CYAN, icon_text='[ ]', fontsize=10)

    # Arrows from user to agent
    draw_arrow(ax, 0.36, 0.775, 0.42, 0.655, CYAN, 'text')
    draw_arrow(ax, 0.64, 0.775, 0.58, 0.655, CYAN, 'Web3.js')

    # === Layer 2: Agent Layer ===
    draw_layer_label(ax, 0.06, 0.66, '[ AGENT LAYER ]', BLUE)

    draw_box(ax, 0.24, 0.52, 0.24, 0.12,
             'AI Agent (Python)',
             'NLP Parse + Web3.py',
             BLUE, icon_text='{}', fontsize=11)

    draw_box(ax, 0.52, 0.52, 0.24, 0.12,
             'Transaction Builder',
             'Sign + Send',
             PURPLE, icon_text='#', fontsize=10)

    draw_arrow(ax, 0.48, 0.58, 0.52, 0.58, BLUE_LIGHT, 'build_tx')

    # === Layer 3: Blockchain Layer ===
    draw_layer_label(ax, 0.06, 0.45, '[ BLOCKCHAIN LAYER ]', GREEN)

    draw_box(ax, 0.06, 0.28, 0.26, 0.14,
             'SplitPayment.sol',
             'createSplit() / executeSplit()',
             GREEN, icon_text='S', fontsize=11)

    draw_box(ax, 0.37, 0.28, 0.26, 0.14,
             'Ethereum Sepolia',
             'Testnet / Consensus',
             AMBER, icon_text='E', fontsize=11)

    draw_box(ax, 0.68, 0.28, 0.26, 0.14,
             'Etherscan',
             'Tx / Address / Events',
             PURPLE, icon_text='?', fontsize=10)

    # Arrows between blockchain components
    draw_arrow(ax, 0.32, 0.35, 0.37, 0.35, GREEN, 'deploy')
    draw_arrow(ax, 0.63, 0.35, 0.68, 0.35, AMBER, 'index')

    # Arrow from agent to blockchain
    draw_arrow(ax, 0.36, 0.52, 0.19, 0.42, BLUE, 'send tx')
    draw_arrow(ax, 0.64, 0.52, 0.50, 0.42, PURPLE, 'RPC')

    # === Bottom: Evidence Layer ===
    draw_layer_label(ax, 0.06, 0.20, '[ EVIDENCE ]', TEXT_MUTED)

    evidence_items = [
        ('Tx Hash', '0xabc...def'),
        ('Contract', '0x123...789'),
        ('Split ID', '#0, #1, #2...'),
        ('Gas Used', '~250,000'),
    ]

    for i, (label, value) in enumerate(evidence_items):
        x = 0.10 + i * 0.22
        box = FancyBboxPatch((x, 0.08), 0.18, 0.08,
                              boxstyle="round,pad=0.008",
                              facecolor=BG_CARD_LIGHT, edgecolor=BORDER,
                              linewidth=0.8, zorder=3)
        ax.add_patch(box)
        ax.text(x + 0.09, 0.135, label,
                fontsize=8, ha='center', va='center',
                color=TEXT_DIM, fontfamily=MONO, zorder=5)
        ax.text(x + 0.09, 0.10, value,
                fontsize=7, ha='center', va='center',
                color=BLUE_LIGHT, fontfamily=MONO, zorder=5)

    draw_grid_dots(ax)

    # Footer
    ax.text(0.5, 0.025,
            'SplitChain  /  Shandong Computer Science Center  /  Blockchain Technology 2026',
            fontsize=7, ha='center', va='center',
            color=TEXT_MUTED, fontfamily=MONO, alpha=0.5)

    plt.tight_layout(pad=0.5)
    fig.savefig(os.path.join(OUTPUT_DIR, 'architecture.png'),
                facecolor=BG, edgecolor='none', bbox_inches='tight', dpi=200)
    plt.close()
    print("Created: architecture.png")


# ============================================================
# DIAGRAM 2: Flowchart
# ============================================================
def create_flowchart():
    fig, ax = plt.subplots(1, 1, figsize=(12, 14), dpi=200)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Title
    ax.text(0.5, 0.97, 'SPLIT EXECUTION FLOW', fontsize=22, ha='center', va='center',
            color=BLUE, fontweight='bold', fontfamily=MONO)
    ax.text(0.5, 0.945, 'On-Chain Payment Splitting Process',
            fontsize=9, ha='center', va='center',
            color=TEXT_DIM, fontfamily=MONO)
    ax.plot([0.2, 0.8], [0.933, 0.933], color=BLUE, linewidth=0.5, alpha=0.3)

    steps = [
        {
            'y': 0.87, 'color': CYAN, 'icon': '>',
            'title': 'User Input',
            'detail': '"split 1 ETH 3:3:4 to addr_A, addr_B, addr_C"',
            'type': 'input'
        },
        {
            'y': 0.77, 'color': BLUE, 'icon': '{}',
            'title': 'Agent Parses Instruction',
            'detail': 'Extract: Amount=1 ETH, Ratio=3:3:4, Addrs=[A,B,C]',
            'type': 'process'
        },
        {
            'y': 0.67, 'color': BLUE, 'icon': '[]',
            'title': 'Build createSplit() Transaction',
            'detail': 'Contract.createSplit([A,B,C], [30,30,40]) + 1 ETH',
            'type': 'process'
        },
        {
            'y': 0.57, 'color': PURPLE, 'icon': '#',
            'title': 'Sign & Send to Sepolia',
            'detail': 'Private Key -> Signed Raw Tx -> RPC Endpoint',
            'type': 'action'
        },
        {
            'y': 0.47, 'color': GREEN, 'icon': 'S',
            'title': 'Contract Records Split Plan',
            'detail': 'splits[0] = {creator, recipients, percentages, 1 ETH}',
            'type': 'state'
        },
        {
            'y': 0.37, 'color': BLUE, 'icon': '!',
            'title': 'Build executeSplit() Transaction',
            'detail': 'Contract.executeSplit(splitId=0)',
            'type': 'process'
        },
        {
            'y': 0.27, 'color': AMBER, 'icon': '$',
            'title': 'Contract Distributes ETH',
            'detail': 'A: 0.3 ETH  |  B: 0.3 ETH  |  C: 0.4 ETH',
            'type': 'action'
        },
        {
            'y': 0.17, 'color': GREEN, 'icon': '*',
            'title': 'Verifiable On-Chain Evidence',
            'detail': 'Etherscan: Tx Hash / Contract Address / Events',
            'type': 'output'
        },
    ]

    box_w = 0.52
    box_h = 0.065
    box_x = 0.24

    for i, step in enumerate(steps):
        y = step['y']

        # Shadow
        shadow = FancyBboxPatch((box_x + 0.005, y - 0.005), box_w, box_h,
                                 boxstyle="round,pad=0.01",
                                 facecolor='#000000', edgecolor='none',
                                 alpha=0.25, zorder=2)
        ax.add_patch(shadow)

        # Main box
        box = FancyBboxPatch((box_x, y), box_w, box_h,
                              boxstyle="round,pad=0.01",
                              facecolor=BG_CARD, edgecolor=step['color'],
                              linewidth=1.2, zorder=3)
        ax.add_patch(box)

        # Left accent
        accent = FancyBboxPatch((box_x, y + 0.005), 0.005, box_h - 0.01,
                                 boxstyle="round,pad=0.001",
                                 facecolor=step['color'], edgecolor='none',
                                 zorder=4)
        ax.add_patch(accent)

        # Step number
        step_num = f"0{i + 1}"
        ax.text(box_x + 0.025, y + box_h / 2, step_num,
                fontsize=8, ha='center', va='center',
                color=step['color'], fontfamily=MONO,
                fontweight='bold', zorder=5, alpha=0.6)

        # Icon (text-based)
        ax.text(box_x + 0.06, y + box_h / 2, step['icon'],
                fontsize=13, ha='center', va='center', zorder=5,
                color=step['color'], fontweight='bold', fontfamily=MONO)

        # Title
        ax.text(box_x + 0.10, y + box_h - 0.018, step['title'],
                fontsize=11, ha='left', va='center',
                color=TEXT, fontweight='bold', zorder=5)

        # Detail
        ax.text(box_x + 0.10, y + 0.018, step['detail'],
                fontsize=7.5, ha='left', va='center',
                color=TEXT_DIM, zorder=5, fontfamily=MONO)

        # Arrow to next step
        if i < len(steps) - 1:
            next_y = steps[i + 1]['y']
            arrow_x = box_x + box_w / 2
            draw_arrow(ax, arrow_x, y, arrow_x, next_y + box_h,
                       step['color'], style='->', lw=1.2)
            mid_y = (y + next_y + box_h) / 2
            ax.plot(arrow_x, mid_y, 'o', color=step['color'],
                    markersize=3, alpha=0.5, zorder=4)

    # Right side annotations
    annotations = [
        (0.87, 'PARSE', CYAN),
        (0.67, 'BUILD', BLUE),
        (0.57, 'SIGN', PURPLE),
        (0.47, 'STORE', GREEN),
        (0.37, 'EXEC', BLUE),
        (0.27, 'SEND', AMBER),
    ]

    for y, label, color in annotations:
        ax.plot([box_x + box_w + 0.02, box_x + box_w + 0.05],
                [y + box_h / 2, y + box_h / 2],
                color=color, linewidth=0.5, alpha=0.3)
        ax.text(box_x + box_w + 0.06, y + box_h / 2, label,
                fontsize=7, ha='left', va='center',
                color=color, fontfamily=MONO, alpha=0.5)

    draw_grid_dots(ax)

    ax.text(0.5, 0.02, 'SplitChain  /  Blockchain Technology Course  /  2026',
            fontsize=7, ha='center', va='center',
            color=TEXT_MUTED, fontfamily=MONO, alpha=0.4)

    plt.tight_layout(pad=0.5)
    fig.savefig(os.path.join(OUTPUT_DIR, 'flowchart.png'),
                facecolor=BG, edgecolor='none', bbox_inches='tight', dpi=200)
    plt.close()
    print("Created: flowchart.png")


if __name__ == '__main__':
    create_architecture()
    create_flowchart()
    print("All diagrams generated successfully.")
