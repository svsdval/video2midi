"""Synthetic falling-notes piano videos with a known answer, for testing v2m_auto.

	python tests/synth_video.py out_dir        -> writes several videos + <name>.truth.json
"""
from __future__ import annotations

import json
import os
import sys

import cv2
import numpy as np

BLACK = {1, 3, 6, 8, 10}


def is_black(m: int) -> bool:
	return m % 12 in BLACK


def key_layout(lo: int, hi: int, x0: float, x1: float):
	"""x centre and width of every key lo..hi on a keyboard drawn from x0 to x1."""
	whites = [m for m in range(lo, hi + 1) if not is_black(m)]
	ww = (x1 - x0) / len(whites)
	pos = {}
	i = 0
	for m in range(lo, hi + 1):
		if is_black(m):
			pos[m] = (x0 + i * ww, 0.6 * ww)  # between the previous and the next white key
		else:
			pos[m] = (x0 + (i + 0.5) * ww, ww)
			i += 1
	return pos, ww


def make_song(seed: int, lo: int, hi: int, length: float):
	rng = np.random.default_rng(seed)
	notes = []
	t = 0.5
	while t < length - 1.5:
		# left hand: low notes, long
		m = int(rng.integers(max(lo, 33), 55))
		notes.append((m, t, t + float(rng.choice([0.5, 0.75, 1.0])), 1))
		# right hand: chords and melody, sometimes repeated notes, sometimes black keys next to white
		k = int(rng.integers(1, 4))
		base = int(rng.integers(58, min(hi, 90)))
		for j in range(k):
			mm = min(hi, base + j * int(rng.integers(2, 5)))
			d = float(rng.choice([0.2, 0.25, 0.4, 0.5]))
			notes.append((mm, t, t + d, 0))
			if rng.random() < 0.3:  # same key again right after a short gap
				notes.append((mm, t + d + 0.07, t + d + 0.07 + 0.2, 0))
		t += float(rng.choice([0.5, 0.75, 1.0]))
	# remove overlaps on the same key
	notes.sort(key=lambda n: (n[0], n[1]))
	clean = []
	for n in notes:
		if clean and clean[-1][0] == n[0] and n[1] < clean[-1][2] + 0.05:
			continue
		clean.append(n)
	return sorted(clean, key=lambda n: n[1])


def render(path: str, style: dict, seed: int = 1, length: float = 20.0) -> list:
	w, h = style.get('size', (1280, 720))
	fps = style.get('fps', 30)
	lo, hi = style.get('range', (21, 108))
	kx0, kx1 = style.get('kx', (0, w))
	ky = int(h * style.get('ky', 0.78))  # keyboard top
	kh = h - ky if style.get('kh') is None else style['kh']
	speed = style.get('speed', 250.0)  # px per second
	pos, ww = key_layout(lo, hi, kx0, kx1)
	notes = make_song(seed, lo, hi, length)
	colours = style['colours']  # (right hand, left hand), BGR
	bar_scale = style.get('bar_scale', 0.85)
	bg = style.get('bg', (0, 0, 0))
	fourcc = cv2.VideoWriter_fourcc(*'mp4v')
	vw = cv2.VideoWriter(path, fourcc, fps, (w, h))
	yy, xx = np.mgrid[0:ky, 0:w]
	for f in range(int(length * fps)):
		t = f / fps
		img = np.zeros((h, w, 3), np.uint8)
		if bg == 'gradient':
			img[:ky] = np.stack([40 + 60 * yy / ky, 20 + 30 * xx / w, 60 + 40 * np.sin(xx / 90.0 + t)], -1).clip(0, 255).astype(np.uint8)
		elif bg == 'image':
			img[:ky] = np.stack([90 + 60 * np.sin(xx / 70.0 + t * 0.7) * np.cos(yy / 50.0),
								80 + 50 * np.cos(xx / 110.0 - t * 0.3),
								100 + 40 * np.sin(yy / 40.0 + t)], -1).clip(0, 255).astype(np.uint8)
		else:
			img[:ky] = bg
		# falling bars
		lit = {}
		for m, a, b, hand in notes:
			y_bot = ky - (a - t) * speed
			y_top = ky - (b - t) * speed
			if y_bot < 0 or y_top > ky:
				continue
			cx, kw = pos[m]
			bw = kw * (bar_scale if not is_black(m) else 1.0)
			c = colours[hand]
			p0 = (int(round(cx - bw / 2)), int(max(0, y_top)))
			p1 = (int(round(cx + bw / 2)) - 1, int(min(ky - 1, y_bot)))
			cv2.rectangle(img, p0, p1, c, -1)
			if style.get('outline'):
				cv2.rectangle(img, p0, p1, tuple(int(v * 0.6) for v in c), 1)
			if a <= t < b:
				lit[m] = c
		# keyboard
		img[ky:] = (60, 60, 60)
		for m in range(lo, hi + 1):
			if is_black(m):
				continue
			cx, kw = pos[m]
			col = lit.get(m, (235, 235, 235))
			cv2.rectangle(img, (int(cx - kw / 2) + 1, ky), (int(cx + kw / 2) - 1, h - 1), col, -1)
		for m in range(lo, hi + 1):
			if not is_black(m):
				continue
			cx, kw = pos[m]
			col = tuple(int(v * 0.7) for v in lit[m]) if m in lit else (20, 20, 20)
			cv2.rectangle(img, (int(cx - kw / 2), ky), (int(cx + kw / 2), ky + int(kh * 0.62)), col, -1)
		if style.get('line'):
			cv2.line(img, (0, ky - 2), (w, ky - 2), style['line'], 3)
		vw.write(img)
	vw.release()
	return notes


STYLES = {
	'classic_green_blue': {'colours': [(80, 220, 120), (230, 160, 60)], 'bg': (25, 25, 25)},
	'pink_yellow_gradient': {'colours': [(180, 100, 255), (60, 220, 255)], 'bg': 'gradient', 'line': (60, 60, 230)},
	'one_colour_white_on_black': {'colours': [(240, 240, 240), (240, 240, 240)], 'bg': (0, 0, 0), 'bar_scale': 1.0},
	'dark_bars_light_bg': {'colours': [(70, 40, 40), (40, 40, 90)], 'bg': (225, 225, 225), 'outline': True},
	'moving_picture_bg': {'colours': [(255, 255, 0), (0, 128, 255)], 'bg': 'image'},
	'small_keyboard_61': {'colours': [(60, 200, 250), (250, 120, 160)], 'bg': (40, 10, 30), 'range': (36, 96),
						'kx': (90, 1190), 'size': (1280, 720)},
	'low_res_480p': {'colours': [(90, 255, 90), (255, 90, 90)], 'bg': (10, 10, 10), 'size': (854, 480), 'speed': 160},
}


if __name__ == '__main__':
	out = sys.argv[1] if len(sys.argv) > 1 else 'synth'
	os.makedirs(out, exist_ok=True)
	for i, (name, st) in enumerate(STYLES.items()):
		p = os.path.join(out, name + '.mp4')
		notes = render(p, st, seed=i + 1)
		with open(os.path.join(out, name + '.truth.json'), 'w') as f:
			json.dump([{'note': n[0], 'start': n[1], 'end': n[2], 'hand': n[3]} for n in notes], f)
		print(p, len(notes), 'notes')
