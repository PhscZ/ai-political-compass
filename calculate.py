import json
import math
import re
import csv
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless-safe
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
from matplotlib.colors import LinearSegmentedColormap

# ==========================================
# 1. THE SVALUES QUESTIONS DATA
# ==========================================
questions = [
    {"id": 0, "question": "Freedom of business is the best practical way a society can prosper.", "effects": {"right": 1}},
    {"id": 1, "question": "Charity is a better way of helping those in need than social welfare.", "effects": {"right": 1}},
    {"id": 2, "question": "Wages are always fair, as employers know best what a worker's labour is worth.", "effects": {"right": 1}},
    {"id": 3, "question": "It is \"human nature\" to be greedy.", "effects": {"right": 1}},
    {"id": 4, "question": "\"Exploitation\" is an outdated term, as the struggles of 1800s capitalism don't exist anymore.", "effects": {"right": 1}},
    {"id": 5, "question": "Communism is an ideal that can never work in practice.", "effects": {"right": 1}},
    {"id": 6, "question": "Taxation of the wealthy is a bad idea, society would be better off without it.", "effects": {"right": 1}},
    {"id": 7, "question": "The harder you work, the more you progress up the social ladder.", "effects": {"right": 1}},
    {"id": 8, "question": "Organisations and corporations cannot be trusted and need to be regulated by the government.", "effects": {"right": -1}},
    {"id": 9, "question": "A government that provides for everyone is an inherently good idea.", "effects": {"right": -1}},
    {"id": 10, "question": "The current welfare system should be expanded to further combat inequality.", "effects": {"right": -1}},
    {"id": 11, "question": "Land should not be a commodity to be bought and sold.", "effects": {"right": -1}},
    {"id": 12, "question": "All industry and the bank should be nationalised.", "effects": {"right": -1}},
    {"id": 13, "question": "Class is the primary division of society.", "effects": {"right": -1}},
    {"id": 14, "question": "Economic inequality is too high in the world.", "effects": {"right": -1}},
    {"id": 15, "question": "Sometimes it is right that the government may spy on its citizens to combat extremists and terrorists.", "effects": {"auth": 1}},
    {"id": 16, "question": "Authority figures, if morally correct, are a good thing for society.", "effects": {"auth": 1}},
    {"id": 17, "question": "Strength is necessary for any government to succeed.", "effects": {"auth": 1}},
    {"id": 18, "question": "Only the government can fairly and effectively regulate organisations.", "effects": {"auth": 1}},
    {"id": 19, "question": "Society requires structure and bureaucracy in order to function.", "effects": {"auth": 1}},
    {"id": 20, "question": "Mandatory IDs should be used to ensure public safety.", "effects": {"auth": 1}},
    {"id": 21, "question": "In times of crisis, safety becomes more important than civil liberties.", "effects": {"auth": 1}},
    {"id": 22, "question": "If you have nothing to hide, you have nothing to fear.", "effects": {"auth": 1}},
    {"id": 23, "question": "The government should be less involved in the day to day life of its citizens.", "effects": {"auth": -1}},
    {"id": 24, "question": "Without democracy, a society is nothing.", "effects": {"auth": -1}},
    {"id": 25, "question": "Jury nullification should be legal.", "effects": {"auth": -1}},
    {"id": 26, "question": "The smaller the government, the freer the people.", "effects": {"auth": -1}},
    {"id": 27, "question": "The government should, at most, provide emergency services and law enforcement.", "effects": {"auth": -1}},
    {"id": 28, "question": "The police were not created to protect the people, but to uphold the status quo by force.", "effects": {"auth": -1}},
    {"id": 29, "question": "State schools are a bad idea because our state shouldn't be influencing our children.", "effects": {"auth": -1}},
    {"id": 30, "question": "Two consenting individuals should be able to do whatever they want with each other, even if it makes me uncomfortable.", "effects": {"prog": 1}},
    {"id": 31, "question": "An individual's body is their own property, and they should be able to do anything they desire to it.", "effects": {"prog": 1}},
    {"id": 32, "question": "A person should be able to worship whomever or whatever they want.", "effects": {"prog": 1}},
    {"id": 33, "question": "Nudism is perfectly natural.", "effects": {"prog": 1}},
    {"id": 34, "question": "Animals deserve certain universal rights.", "effects": {"prog": 1}},
    {"id": 35, "question": "Gender is a social construct, not a natural state of affairs.", "effects": {"prog": 1}},
    {"id": 36, "question": "Laws based on cultural values, rather than ethical ones, aren't justice.", "effects": {"prog": 1}},
    {"id": 37, "question": "Autonomy of body extends even to minors, the mentally ill, and serious criminals.", "effects": {"prog": 1}},
    {"id": 38, "question": "Homosexuality is against my values.", "effects": {"prog": -1}},
    {"id": 39, "question": "Transgender individuals should not be able to adopt children.", "effects": {"prog": -1}},
    {"id": 40, "question": "Drugs are harmful and should be banned.", "effects": {"prog": -1}},
    {"id": 41, "question": "The death penalty should exist for certain crimes.", "effects": {"prog": -1}},
    {"id": 42, "question": "Victimless crimes should still be punished.", "effects": {"prog": -1}},
    {"id": 43, "question": "One cannot be moral without religion.", "effects": {"prog": -1}},
    {"id": 44, "question": "Parents should hold absolute power over their children, as they are older and more experienced.", "effects": {"prog": -1}},
    {"id": 45, "question": "Multiculturalism is bad.", "effects": {"prog": -1}}
]

questions_object = {q['id']: q for q in questions}

# ==========================================
# 2. COLOR & MD PARSING LOGIC
# ==========================================
CONSOLE_TO_HEX = {
    "orange": "#FF8C00", "bright_black": "#555555", "green": "#228B22",
    "bright_white": "#D3D3D3", "bright_blue": "#1E90FF", "purple": "#8A2BE2",
    "dark_gray": "#696969", "cyan": "#00CED1", "bright_magenta": "#FF00FF",
    "teal": "#008080", "red": "#DC143C", "black": "#000000", "white": "#FFFFFF",
    "blue": "#0000FF", "yellow": "#FFD700", "magenta": "#FF00FF"
}

def parse_models_md(filepath="models.md"):
    model_to_company = {}
    company_colors = {}
    if not os.path.exists(filepath):
        return model_to_company, company_colors

    in_colors_section = False
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"): continue

            if line.lower() == "[colors]":
                in_colors_section = True
                continue

            if in_colors_section:
                if "=" in line:
                    company, color = line.split("=", 1)
                    company_colors[company.strip()] = color.strip()
            else:
                if "|" in line:
                    model, company = line.split("|", 1)
                    model_to_company[model.strip()] = company.strip()
    return model_to_company, company_colors

def get_text_effects(color_hex=None):
    """Returns a thin, inherently black outline for model label text."""
    return [pe.withStroke(linewidth=1.5, foreground="black")]

# ==========================================
# 3. CORE CALCULATION LOGIC
# ==========================================
def calculate_scores(ai_answers):
    max_scores = {"right": 0, "auth": 0, "prog": 0}
    actual_scores = {"right": 0, "auth": 0, "prog": 0}

    for q_id_str, answer in ai_answers.items():
        q_id = int(q_id_str)
        if answer is not None and q_id in questions_object:
            for effect, weight in questions_object[q_id]['effects'].items():
                max_scores[effect] += abs(weight)
                actual_scores[effect] += float(answer) * weight

    results = {}
    for effect in max_scores:
        if max_scores[effect] > 0:
            raw_score = actual_scores[effect] * 10 / max_scores[effect]
            results[effect] = math.floor(raw_score * 100 + 0.5) / 100
        else:
            results[effect] = 0.00
    return results

def generate_results_url(results):
    args = "?"
    keys = list(results.keys())
    for i, effect in enumerate(keys):
        args += f"{effect}={results[effect]}"
        if i < len(keys) - 1: args += "&"
    return f"https://sapplyvalues.github.io/feedback.html{args}"

def extract_json(raw_text):
    match = re.search(r'\{.*\}', raw_text, re.DOTALL)
    return match.group(0) if match else raw_text

# ==========================================
# 4. BATCH PROCESSING FUNCTIONS
# ==========================================
def process_batch(ai_data):
    all_results = []
    for ai_name, raw_response in ai_data.items():
        try:
            answers = json.loads(extract_json(raw_response))
            scores = calculate_scores(answers)
            url = generate_results_url(scores)
            all_results.append({"name": ai_name, "scores": scores, "url": url})
        except json.JSONDecodeError:
            print(f"⚠️ Warning: Could not parse JSON for '{ai_name}'. Skipping.")
    return all_results

def print_comparison_table(results):
    print(f"\n{'AI / Persona':<25} | {'Right':<8} | {'Auth':<8} | {'Prog':<8}")
    print("-" * 60)
    for res in results:
        s = res['scores']
        print(f"{res['name']:<25} | {s.get('right', 0):<8} | {s.get('auth', 0):<8} | {s.get('prog', 0):<8}")

def export_to_csv(results, filename="ai_compass_results.csv"):
    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["AI / Persona", "Right", "Auth", "Prog", "Result URL"])
        for res in results:
            s = res['scores']
            writer.writerow([res['name'], s.get('right', 0), s.get('auth', 0), s.get('prog', 0), res['url']])
    print(f"✅ Results exported to {filename}")

def load_responses_from_folder(folder_path="models"):
    ai_data = {}
    if not os.path.exists(folder_path): return ai_data
    for filename in os.listdir(folder_path):
        if filename.endswith((".json", ".txt", ".md")):
            ai_name = os.path.splitext(filename)[0]
            with open(os.path.join(folder_path, filename), 'r', encoding='utf-8') as f:
                ai_data[ai_name] = f.read()
    return ai_data

# ==========================================
# 5. GROUP COMPASS IMAGE BUILDER
# ==========================================
def plot_all_models(results, filename="all_models_compass.png"):
    if not results:
        print("⚠️ No results to plot.")
        return

    model_to_company, company_colors_raw = parse_models_md("models.md")
    company_colors_hex = {c: CONSOLE_TO_HEX.get(v.lower(), "#888888") for c, v in company_colors_raw.items()}

    company_shape_index = {}
    shapes = ['o', 's', '^', 'p']  # circle, square, triangle, pentagon

    sorted_results = sorted(results, key=lambda r: r['scores'].get('prog', 0), reverse=True)

    # ---------- Bigger canvas + high DPI = crisp, readable output ----------
    fig = plt.figure(figsize=(20, 14), facecolor="#ececec")
    ax = fig.add_axes([0.07, 0.26, 0.52, 0.66])
    ax.set_facecolor("#ececec")

    # Quadrants
    ax.add_patch(Rectangle((-10, 0), 10, 10, facecolor="#f4b6b6", edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((0, 0), 10, 10, facecolor="#8fd3f4", edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((-10, -10), 10, 10, facecolor="#b7d9b0", edgecolor="none", zorder=0))
    ax.add_patch(Rectangle((0, -10), 10, 10, facecolor="#f0f0a8", edgecolor="none", zorder=0))

    # Grid + frame
    ax.set_xlim(-10, 10); ax.set_ylim(-10, 10)
    ax.set_xticks(range(-10, 11)); ax.set_yticks(range(-10, 11))
    ax.grid(True, color="#9a9a9a", linewidth=0.5, zorder=1)
    ax.set_xticklabels([]); ax.set_yticklabels([]); ax.tick_params(length=0)
    for spine in ax.spines.values(): spine.set_visible(False)

    lw = 3
    ax.plot([-10, 10], [0, 0], color="black", lw=lw, zorder=2)
    ax.plot([0, 0], [-10, 10], color="black", lw=lw, zorder=2)
    arrowprops = dict(arrowstyle="-|>", color="black", lw=lw, mutation_scale=25)
    for xy, xytext in [((11.0, 0), (9.8, 0)), ((-11.0, 0), (-9.8, 0)),
                       ((0, 11.0), (0, 9.8)), ((0, -11.0), (0, -9.8))]:
        ax.annotate("", xy=xy, xytext=xytext, arrowprops=arrowprops, zorder=3, clip_on=False)

    lbl = dict(fontsize=16, fontweight="bold", ha="center", va="center", clip_on=False)
    ax.text(0, 11.7, "Authority", **lbl)
    ax.text(0, -11.7, "Liberty", **lbl)
    ax.text(-11.3, 0, "Left", **lbl)
    ax.text(11.3, 0, "Right", **lbl)

    # ---------- Prog/Con gradient bar ----------
    bar = fig.add_axes([0.74, 0.26, 0.035, 0.66])
    cmap = LinearSegmentedColormap.from_list(
        "progcon", ["#050530", "#00008b", "#2255dd", "#55aaff", "#7fd4b0", "#2ecc40", "#009900"])
    grad = np.linspace(0, 1, 256).reshape(-1, 1)
    bar.imshow(grad, aspect="auto", cmap=cmap, extent=[0, 1, -10, 10], origin="lower")
    bar.set_xlim(0, 1); bar.set_ylim(-10, 10)
    bar.set_xticks([]); bar.set_yticks([])
    for spine in bar.spines.values(): spine.set_visible(False)
    fig.text(0.7575, 0.94, "Progressive", fontsize=16, fontweight="bold", ha="center")
    fig.text(0.7575, 0.225, "Conservative", fontsize=16, fontweight="bold", ha="center")

    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    placed_boxes = []

    def smart_label(name, x, y, color_hex, effects):
        """Places a compass label at the first offset that doesn't collide with already-placed labels."""
        candidates = [(9, 7, 'left'), (9, -8, 'left'), (-9, 7, 'right'), (-9, -8, 'right'),
                      (0, 10, 'center'), (0, -11, 'center'), (13, 1, 'left'), (-13, 1, 'right'),
                      (11, 13, 'left'), (-11, 13, 'right'), (11, -14, 'left'), (-11, -14, 'right'),
                      (20, 4, 'left'), (-20, 4, 'right'), (0, 18, 'center'), (0, -19, 'center')]
        fallback = None
        for dx, dy, ha in candidates:
            ann = ax.annotate(name, (x, y), textcoords="offset points", xytext=(dx, dy),
                              ha=ha, va='center', fontsize=8, fontweight='bold',
                              color=color_hex, path_effects=effects, zorder=6, clip_on=False)
            # padded(2) gives a little breathing room between labels
            box = ann.get_window_extent(renderer).padded(2)

            if not any(box.overlaps(b) for b in placed_boxes):
                # Success! Delete the temporary fallback label if we were holding one
                if fallback is not None:
                    fallback[0].remove()
                placed_boxes.append(box)
                return ann

            if fallback is None:
                fallback = (ann, box)   # keep this one only as a last resort
            else:
                ann.remove()            # discard this failed attempt immediately

        # No collision-free spot found: keep the single fallback label
        ann, box = fallback
        placed_boxes.append(box)
        return ann

    # ---------- Plot every model ----------
    handles = []
    for res in sorted_results:
        company = model_to_company.get(res['name'], 'unknown')
        color_hex = company_colors_hex.get(company, "#888888")
        idx = company_shape_index.get(company, 0)
        marker = shapes[idx % len(shapes)]
        company_shape_index[company] = idx + 1

        s = res['scores']
        x, y, z = s.get('right', 0), s.get('auth', 0), s.get('prog', 0)
        effects = get_text_effects(color_hex)

        # Small marker on the 2D compass
        ax.scatter([x], [y], s=90, marker=marker, color=color_hex,
                   edgecolors="black", linewidths=1.0, zorder=5)
        smart_label(res['name'], x, y, color_hex, effects)

        # Tick line on the bar
        bar.axhline(z, color='black', lw=3.0, zorder=4)
        bar.axhline(z, color=color_hex, lw=2.0, zorder=5)

        handles.append(Line2D([0], [0], marker=marker, color="w", markerfacecolor=color_hex,
                              markeredgecolor="black", markersize=7,
                              label=f"{res['name']}  (R:{x} | A:{y} | P:{z})"))

    # ---------- Bar callout labels: evenly spaced, alternating sides, leader lines ----------
    zs = [r['scores'].get('prog', 0) for r in sorted_results]
    lo, hi = max(min(zs) - 1.5, -9.8), min(max(zs) + 1.5, 9.8)
    left_items  = [r for i, r in enumerate(sorted_results) if i % 2 == 0]
    right_items = [r for i, r in enumerate(sorted_results) if i % 2 == 1]

    def spread(items, side):
        n = len(items)
        for j, res in enumerate(items):
            y_lab = hi - (hi - lo) * (j / (n - 1)) if n > 1 else (hi + lo) / 2
            z = res['scores'].get('prog', 0)
            company = model_to_company.get(res['name'], 'unknown')
            color_hex = company_colors_hex.get(company, "#888888")
            effects = get_text_effects(color_hex)
            if side == 'left':
                bar.plot([0.0, -0.18], [z, y_lab], color=color_hex, lw=0.8, alpha=0.9,
                         zorder=6, clip_on=False)
                bar.text(-0.24, y_lab, res['name'], ha='right', va='center', fontsize=8,
                         fontweight='bold', color=color_hex, path_effects=effects,
                         clip_on=False, zorder=7)
            else:
                bar.plot([1.0, 1.18], [z, y_lab], color=color_hex, lw=0.8, alpha=0.9,
                         zorder=6, clip_on=False)
                bar.text(1.24, y_lab, res['name'], ha='left', va='center', fontsize=8,
                         fontweight='bold', color=color_hex, path_effects=effects,
                         clip_on=False, zorder=7)

    spread(left_items, 'left')
    spread(right_items, 'right')

    # ---------- Legend + watermark ----------
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.36, 0.015),
               ncol=3, fontsize=8, frameon=True, facecolor="white", edgecolor="#999999")
    fig.text(0.995, 0.015, "SapplyValues.github.io", ha="right", va="bottom",
             fontsize=12, color="#444444")

    fig.savefig(filename, dpi=220, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(f"🖼️ Group compass image saved as {filename} (4400x3080 px)")

# ==========================================
# 6. RUN THE SCRIPT
# ==========================================
if __name__ == "__main__":
    ai_responses = load_responses_from_folder("models")

    if not ai_responses:
        print("No files found in the 'models' folder.")
    else:
        print(f"Found {len(ai_responses)} model responses. Calculating scores...\n")
        results = process_batch(ai_responses)
        print_comparison_table(results)
        export_to_csv(results)
        plot_all_models(results, "all_models_compass.png")
