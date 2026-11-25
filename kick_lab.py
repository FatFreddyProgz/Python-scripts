import math
import random
import struct
import tkinter as tk
import wave
from datetime import datetime
from pathlib import Path
from tkinter import messagebox


SAMPLE_RATE = 44100
BG = "#111214"
PANEL = "#1a1c20"
CARD = "#22252a"
ORANGE = "#ff7a18"
TEXT = "#f4f1ed"
MUTED = "#92949a"


def generate_kick(rng):
    params = {
        "start": rng.uniform(105, 210),
        "base": rng.uniform(38, 58),
        "pitch": rng.uniform(0.025, 0.075),
        "decay": rng.uniform(0.28, 0.62),
        "click": rng.uniform(0.15, 0.65),
        "drive": rng.uniform(1.1, 3.8),
        "length": rng.uniform(0.72, 1.15),
    }
    count = int(SAMPLE_RATE * params["length"])
    samples = []
    phase = 0.0
    click_phase = 0.0

    for index in range(count):
        time = index / SAMPLE_RATE
        frequency = params["base"] + (params["start"] - params["base"]) * math.exp(
            -time / params["pitch"]
        )
        phase += 2 * math.pi * frequency / SAMPLE_RATE
        click_phase += 2 * math.pi * 2300 / SAMPLE_RATE

        body_env = math.exp(-time / params["decay"])
        body = math.sin(phase) * body_env
        body += 0.18 * math.sin(2 * phase + 0.3) * math.exp(
            -time / (params["decay"] * 0.72)
        )
        sub = 0.12 * math.sin(phase * 0.5) * math.exp(-time / (params["decay"] * 1.4))

        transient_env = math.exp(-time / 0.006)
        noise = rng.uniform(-1, 1) if time < 0.04 else 0.0
        transient = params["click"] * transient_env * (
            0.38 * math.sin(click_phase) + 0.20 * noise
        )
        driven = math.tanh((body + sub + transient) * params["drive"])
        samples.append(driven)

    peak = max(abs(sample) for sample in samples) or 1.0
    samples = [sample * (0.92 / peak) for sample in samples]
    return params, samples


def write_wav(path, samples):
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(SAMPLE_RATE)
        frames = (struct.pack("<h", int(sample * 32767)) for sample in samples)
        output.writeframes(b"".join(frames))


class KickLab:
    def __init__(self, root):
        self.root = root
        self.rng = random.Random()
        self.params = {}
        self.samples = []
        self.kick_number = 0

        root.title("Kick Lab — générateur de kicks")
        root.configure(bg=BG)
        root.geometry("900x690")
        root.minsize(760, 620)

        self.build_ui()
        self.generate()

    def build_ui(self):
        outer = tk.Frame(self.root, bg=BG, padx=34, pady=26)
        outer.pack(fill="both", expand=True)

        header = tk.Frame(outer, bg=BG)
        header.pack(fill="x", pady=(0, 22))
        tk.Label(
            header,
            text="KICK",
            font=("Helvetica", 30, "bold"),
            fg=TEXT,
            bg=BG,
        ).pack(side="left")
        tk.Label(
            header,
            text=" LAB",
            font=("Helvetica", 30, "bold"),
            fg=ORANGE,
            bg=BG,
        ).pack(side="left")
        tk.Label(
            header,
            text="SYNTHÈSE ALÉATOIRE  ·  WAV 16-BIT",
            font=("Helvetica", 10, "bold"),
            fg=MUTED,
            bg=BG,
        ).pack(side="right", pady=(13, 0))

        tk.Label(
            outer,
            text="Un kick. Une nouvelle personnalité à chaque génération.",
            font=("Helvetica", 13),
            fg=TEXT,
            bg=BG,
            anchor="w",
        ).pack(fill="x", pady=(0, 16))

        self.waveform = tk.Canvas(
            outer,
            height=210,
            bg=PANEL,
            highlightthickness=1,
            highlightbackground="#303238",
        )
        self.waveform.pack(fill="x")
        self.waveform.bind("<Configure>", lambda _event: self.draw_waveform())

        self.param_frame = tk.Frame(outer, bg=BG)
        self.param_frame.pack(fill="x", pady=18)
        self.param_values = {}
        for key, title in (
            ("start", "ATTAQUE"),
            ("base", "TONALITÉ"),
            ("decay", "DÉCROISSANCE"),
            ("drive", "SATURATION"),
        ):
            card = tk.Frame(
                self.param_frame,
                bg=CARD,
                padx=15,
                pady=12,
                highlightthickness=1,
                highlightbackground="#303238",
            )
            card.pack(side="left", fill="both", expand=True, padx=(0, 10))
            tk.Label(
                card, text=title, font=("Helvetica", 9, "bold"), fg=MUTED, bg=CARD
            ).pack(anchor="w")
            value = tk.Label(
                card, text="—", font=("Helvetica", 16, "bold"), fg=TEXT, bg=CARD
            )
            value.pack(anchor="w", pady=(7, 0))
            self.param_values[key] = value

        controls = tk.Frame(outer, bg=BG)
        controls.pack(fill="x", pady=(4, 12))
        self.generate_button = tk.Button(
            controls,
            text="↻   GÉNÉRER UN NOUVEAU KICK",
            command=self.generate,
            bg=ORANGE,
            fg="#17120e",
            activebackground="#ff9340",
            activeforeground="#17120e",
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            font=("Helvetica", 11, "bold"),
            padx=20,
            pady=13,
        )
        self.generate_button.pack(side="left")
        self.save_button = tk.Button(
            controls,
            text="↓   ENREGISTRER SUR LE BUREAU",
            command=self.save,
            bg="#292b30",
            fg=TEXT,
            activebackground="#373a40",
            activeforeground=TEXT,
            relief="flat",
            borderwidth=0,
            cursor="hand2",
            font=("Helvetica", 10, "bold"),
            padx=18,
            pady=13,
        )
        self.save_button.pack(side="right")

        self.status = tk.Label(
            outer,
            text="PRÊT À GÉNÉRER",
            font=("Helvetica", 9, "bold"),
            fg=MUTED,
            bg=BG,
            anchor="w",
        )
        self.status.pack(fill="x", pady=(4, 0))

        tk.Label(
            outer,
            text="MONO  ·  44,1 kHz  ·  ENREGISTREMENT WAV SUR LE BUREAU",
            font=("Helvetica", 8, "bold"),
            fg="#676970",
            bg=BG,
            anchor="w",
        ).pack(fill="x", side="bottom", pady=(18, 0))

    def generate(self):
        self.params, self.samples = generate_kick(self.rng)
        self.kick_number += 1
        self.param_values["start"].config(text=f'{self.params["start"]:.0f} Hz')
        self.param_values["base"].config(text=f'{self.params["base"]:.0f} Hz')
        self.param_values["decay"].config(text=f'{self.params["decay"]:.2f} s')
        self.param_values["drive"].config(text=f'{self.params["drive"]:.1f}×')
        self.status.config(text=f"KICK #{self.kick_number:03d}  ·  PRÊT À ÊTRE ENREGISTRÉ", fg=MUTED)
        self.draw_waveform()

    def draw_waveform(self):
        canvas = self.waveform
        canvas.delete("all")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width < 10 or not self.samples:
            return

        middle = height // 2
        canvas.create_line(0, middle, width, middle, fill="#34363b")
        for fraction in (0.25, 0.5, 0.75):
            x = int(width * fraction)
            canvas.create_line(x, 0, x, height, fill="#25272c")

        points = []
        display_count = min(width, len(self.samples))
        for x in range(display_count):
            start = x * len(self.samples) // display_count
            end = max(start + 1, (x + 1) * len(self.samples) // display_count)
            peak = max(abs(value) for value in self.samples[start:end])
            amplitude = peak * (height * 0.43)
            px = x * width / display_count
            points.extend((px, middle - amplitude, px, middle + amplitude))
        canvas.create_line(*points, fill=ORANGE, width=1.5)

        canvas.create_text(
            18, 16, text="FORME D’ONDE", fill=MUTED, anchor="nw",
            font=("Helvetica", 9, "bold"),
        )
        canvas.create_text(
            width - 18, 16, text=f"{self.params.get('length', 0):.2f} s",
            fill=MUTED, anchor="ne", font=("Helvetica", 9, "bold"),
        )

    def save(self):
        desktop = Path.home() / "Desktop"
        try:
            desktop.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            path = desktop / f"kick_{timestamp}.wav"
            suffix = 2
            while path.exists():
                path = desktop / f"kick_{timestamp}_{suffix:02d}.wav"
                suffix += 1
            write_wav(path, self.samples)
        except OSError as error:
            messagebox.showerror(
                "Enregistrement impossible",
                f"Le fichier n’a pas pu être enregistré sur le Bureau.\n\n{error}",
                parent=self.root,
            )
            return

        self.status.config(text=f"ENREGISTRÉ  ·  {path}", fg=ORANGE)


def main():
    root = tk.Tk()
    KickLab(root)
    root.mainloop()


if __name__ == "__main__":
    main()
