#!/usr/bin/env python3
"""v2m_auto - automatic video -> MIDI, no manual key/colour setup.

Usage:
	python v2m_auto.py video.mp4 [-o out.mid] [--mode auto|roll|keys] [--debug]

What it does on its own:
	1. finds the piano keyboard in the picture (black key pattern) and maps
	   every key to its MIDI note,
	2. learns the note colours of this particular video (any palette),
	3. reads the falling notes right above the keyboard ("roll" mode) or, when
	   the video has no falling notes, the lit keys themselves ("keys" mode),
	4. writes the MIDI, one channel per note colour (usually one per hand).
"""
from __future__ import annotations

import argparse
import math
import os
import sys
import warnings
from dataclasses import dataclass

import cv2
import numpy as np
from midiutil.MidiFile import MIDIFile

BLACK_PCS = [1, 3, 6, 8, 10]
# gap that follows each black key of BLACK_PCS: S(mall) inside a group, L(arge) between groups
GAP_AFTER = ['S', 'L', 'S', 'S', 'L']
# white key boundary = black key centre + BOUND_CORR * white width
BOUND_CORR = {1: 0.10, 3: -0.10, 6: 0.13, 8: 0.0, 10: -0.13}
NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def note_name(midi: int) -> str:
	return f'{NOTE_NAMES[midi % 12]}{midi // 12 - 1}'


def runs_of(mask) -> list[tuple[int, int]]:
	"""[start, end) of every run of True values."""
	m = np.asarray(mask, dtype=np.int8)
	d = np.diff(np.concatenate(([0], m, [0])))
	return list(zip(np.flatnonzero(d == 1).tolist(), np.flatnonzero(d == -1).tolist()))


# ----------------------------------------------------------------------------
# keyboard detection
# ----------------------------------------------------------------------------

@dataclass
class Keyboard:
	midi: np.ndarray      # note number of every key, ascending
	black: np.ndarray     # bool
	cx: np.ndarray        # centre x
	x0: np.ndarray        # left edge
	x1: np.ndarray        # right edge
	w: float              # white key width
	y0: int               # first row of the black keys (keyboard top)
	y1: int               # last row of the black keys
	x_left: float
	x_right: float


def fit_layout(centers) -> list[int] | None:
	"""Pitch classes of a row of black keys, from their 2-3-2-3 spacing."""
	c = np.asarray(centers, dtype=np.float64)
	n = len(c)
	if n < 5:
		return None
	gaps = np.diff(c)
	sg = np.sort(gaps)
	best_t, best_v = None, -1.0
	for i in range(1, len(sg)):
		a, b = sg[:i], sg[i:]
		v = len(a) * len(b) * (a.mean() - b.mean()) ** 2
		if v > best_v:
			best_v, best_t = v, (sg[i - 1] + sg[i]) / 2
	small, large = gaps[gaps < best_t], gaps[gaps >= best_t]
	if len(small) == 0 or len(large) == 0:
		return None
	gs, gl = float(np.median(small)), float(np.median(large))
	if not 1.3 < gl / gs < 2.5:
		return None
	if gaps.max() > 1.35 * gl or gaps.min() < 0.65 * gs:
		return None
	labels = ['S' if g < best_t else 'L' for g in gaps]
	scores = []
	for o in range(5):
		scores.append(sum(1 for i, lab in enumerate(labels) if GAP_AFTER[(o + i) % 5] != lab))
	o = int(np.argmin(scores))
	if scores[o] > 0.08 * n:
		return None
	if sorted(scores)[1] == scores[o]:
		return None
	return [BLACK_PCS[(o + i) % 5] for i in range(n)]


def row_black_keys(row: np.ndarray):
	"""Black keys seen in one image row, or None if it is no keyboard row.

	Hands may hide a part of the keyboard, so the longest clean stretch of keys is enough.
	"""
	w_img = len(row)
	lo, hi = np.percentile(row, [10, 90])
	if hi - lo < 45:
		return None
	thr = (lo + hi) / 2
	rs = runs_of(row < thr)
	if len(rs) < 7:
		return None
	wd = np.array([b - a for a, b in rs])
	ref = float(np.median(wd))
	keep = wd >= 0.45 * ref
	rs = [r for r, k in zip(rs, keep) if k]
	wd = wd[keep]
	ref = float(np.median(wd))
	good = (wd >= 0.6 * ref) & (wd <= 1.6 * ref)
	good &= np.array([a > 0 and b < w_img for a, b in rs])
	best = None
	for a, b in runs_of(good):
		while b - a >= 7:
			centers = [(rs[i][0] + rs[i][1]) / 2 for i in range(a, b)]
			pcs = fit_layout(centers)
			if pcs is not None:
				cov = wd[a:b].sum() / max(1, rs[b - 1][1] - rs[a][0])
				if 0.18 <= cov <= 0.62 and (best is None or b - a > len(best[0])):
					best = (centers, pcs)
				break
			# a stray blob at one end can spoil the fit: try shorter stretches
			if b - a <= 12:
				break
			c = np.array(centers)
			g = np.diff(c)
			if abs(g[0] - np.median(g)) > abs(g[-1] - np.median(g)):
				a += 1
			else:
				b -= 1
	if best is None:
		return None
	centers, pcs = best
	c = np.array(centers)
	period = float(np.median(c[5:] - c[:-5]))
	i1 = pcs.index(1)
	bright = np.flatnonzero(row >= thr)
	return {
		'centers': centers, 'pcs': pcs, 'thr': thr, 'period': period,
		'anchor': c[i1] % period,
		'all': np.array([(a + b) / 2 for (a, b), ok in zip(rs, good) if ok]),
		'x_left': float(bright[0]), 'x_right': float(bright[-1] + 1),
	}


def detect_keyboard(gray: np.ndarray, gray_hi: np.ndarray | None = None) -> Keyboard | None:
	"""Find the keyboard in a (median) grayscale frame."""
	h, w_img = gray.shape
	g = cv2.GaussianBlur(gray, (3, 1), 0)
	rows = {}
	for y in range(int(h * 0.15), h):
		r = row_black_keys(g[y].astype(np.float32))
		if r is not None:
			rows[y] = r
	if not rows:
		return None

	def compatible(r1, r2) -> bool:
		p = r1['period']
		if abs(r2['period'] - p) > 0.08 * p:
			return False
		d = (r1['anchor'] - r2['anchor'] + p / 2) % p - p / 2
		return abs(d) < 0.35 * p / 7

	# group into vertical bands of rows that see the same keys
	bands, cur = [], []
	for y in sorted(rows):
		if cur and not (y - cur[-1] <= 3 and compatible(rows[cur[-1]], rows[y])):
			bands.append(cur)
			cur = []
		cur.append(y)
	bands.append(cur)
	min_h = max(4, int(0.012 * h))
	bands = [b for b in bands if len(b) >= min_h]
	if not bands:
		return None
	band = max(bands, key=lambda b: len(b) * np.mean([len(rows[y]['centers']) for y in b]))
	y0, y1 = band[0], band[-1]
	top = band[: max(3, len(band) * 2 // 5)]
	ref_y = max(top, key=lambda y: len(rows[y]['centers']))
	ref = rows[ref_y]
	period = float(np.median([rows[y]['period'] for y in top]))
	w = period / 7
	x_left = min(rows[y]['x_left'] for y in band)
	x_right = max(rows[y]['x_right'] for y in band)
	if gray_hi is not None:
		# hands resting on the keys darken the median picture; the bright picture shows the real extent
		for y in band:
			br = np.flatnonzero(gray_hi[y] >= rows[y]['thr'])
			if len(br):
				x_left, x_right = min(x_left, float(br[0])), max(x_right, float(br[-1] + 1))
	# a keyboard that starts within one key of the picture edge runs out of the picture
	if x_left < 0.8 * w:
		x_left = 0.0
	if w_img - x_right < 0.8 * w:
		x_right = float(w_img)
	# keys hidden in the reference row: continue the pattern octave by octave
	centers, pcs = list(ref['centers']), list(ref['pcs'])
	# a keyboard never ends with a black key: a dark thing at the very edge is the piano case
	while centers and centers[-1] > x_right - 0.8 * w:
		centers.pop()
		pcs.pop()
	while centers and centers[0] < x_left + 0.8 * w:
		centers.pop(0)
		pcs.pop(0)
	while centers[4] - period > x_left + 0.3 * w:
		centers.insert(0, centers[4] - period)
		pcs.insert(0, pcs[4])
	while centers[-5] + period < x_right - 0.3 * w:
		centers.append(centers[-5] + period)
		pcs.append(pcs[-5])
	# ... and snap every key to where the other rows actually see it
	for i, c in enumerate(centers):
		seen = []
		for y in top:
			a = rows[y]['all']
			j = int(np.argmin(np.abs(a - c)))
			if abs(a[j] - c) < 0.3 * w:
				seen.append(a[j])
		if len(seen) >= 3:
			centers[i] = float(np.median(seen))
	return build_keys(centers, pcs, x_left, x_right, y0, y1)


def refine_keyboard(kb: Keyboard, grays: np.ndarray, log) -> Keyboard:
	"""Black key positions measured on many single frames instead of guessed by a regular octave step.

	Hands hide different keys in different frames, and the camera perspective makes octaves unequal,
	so every black key is located where it was actually seen.
	"""
	band = kb.y1 - kb.y0
	ys = range(kb.y0 + max(1, band // 5), kb.y0 + max(2, band * 7 // 10), 2)
	w = kb.w
	xl, xr = int(max(0, kb.x_left)), int(min(grays.shape[2], kb.x_right))
	cen = []
	kmax = np.ones((1, max(3, int(2.5 * w) | 1)), np.uint8)
	for gimg in grays:
		g = cv2.GaussianBlur(gimg, (3, 1), 0)
		# local white level: lighting changes along the keyboard, so compare with the keys nearby
		white = cv2.dilate(g, kmax).astype(np.float32)
		for y in ys:
			row = g[y, xl:xr].astype(np.float32)
			wl = white[y, xl:xr]
			for a, b in runs_of((row < 0.55 * wl) & (wl > 60)):
				if 0.4 * w <= b - a <= 1.0 * w and a > 0 and b < len(row):
					cen.append(xl + (a + b - 1) / 2)
	if len(cen) < 100:
		return kb
	bins = 4
	hist = np.bincount(np.round(np.array(cen) * bins).astype(int), minlength=grays.shape[2] * bins + 2).astype(float)
	hist = np.convolve(hist, np.ones(5) / 5, mode='same')
	pk = [i for i in range(1, len(hist) - 1) if hist[i] >= hist[i - 1] and hist[i] > hist[i + 1]]
	pk.sort(key=lambda i: -hist[i])
	top = hist[pk[0]] if pk else 0
	found = []
	for i in pk:
		if hist[i] < 0.08 * top:
			break
		x = i / bins
		if all(abs(x - f) > 0.6 * w for f in found):
			found.append(x)
	found.sort()
	pcs = fit_layout(found)
	if pcs is None or len(found) < len(np.flatnonzero(kb.black)) * 0.8:
		log('  keyboard: per-frame refinement failed, using the regular grid')
		return kb
	# keep the octave numbering of the first detection: match the key nearest to the middle
	old_b = kb.cx[kb.black]
	old_m = kb.midi[kb.black]
	mid = found[len(found) // 2]
	j = int(np.argmin(np.abs(old_b - mid)))
	nk = build_keys(found, pcs, kb.x_left, kb.x_right, kb.y0, kb.y1, fixed=(len(found) // 2, int(old_m[j])))
	if nk.midi[nk.black][len(found) // 2] % 12 != old_m[j] % 12:
		log('  keyboard: per-frame refinement disagrees with the first detection, using the regular grid')
		return kb
	log(f'  keyboard: {len(found)} black keys located on single frames')
	return nk


def build_keys(centers, pcs, x_left, x_right, y0, y1, fixed=None) -> Keyboard:
	c = np.asarray(centers, dtype=np.float64)
	n = len(c)
	if n >= 6:
		w = float(np.median(c[5:] - c[:-5]) / 7)
	else:
		w = float(np.min(np.diff(c)) / 1.1)
	# white key boundaries, each with the (relative) semitone of the white key right of it
	bx, bsemi, black_semi = [], [], []
	semi = pcs[0] + 1
	for i in range(n):
		cur = c[i] + BOUND_CORR[pcs[i]] * w
		bx.append(cur)
		bsemi.append(semi)
		black_semi.append(semi - 1)
		if pcs[i] in (3, 10):
			if i + 1 < n:
				nxt = c[i + 1] + BOUND_CORR[pcs[i + 1]] * w
				bx.append((cur + nxt) / 2)
			else:
				bx.append(cur + w)
			bsemi.append(semi + 1)
			semi += 3
		else:
			semi += 2

	def next_white(s):
		return s + 1 if s % 12 in (4, 11) else s + 2

	def prev_white(s):
		return s - 1 if s % 12 in (0, 5) else s - 2

	# extend to the keyboard edges with whole white keys
	while bx[0] - w >= x_left - 0.5 * w:
		bx.insert(0, bx[0] - w)
		bsemi.insert(0, prev_white(bsemi[0]))
	if bx[0] - x_left > 0.5 * w:
		bx.insert(0, x_left)
		bsemi.insert(0, prev_white(bsemi[0]))
	while bx[-1] + w <= x_right + 0.5 * w:
		bx.append(bx[-1] + w)
		bsemi.append(next_white(bsemi[-1]))
	if x_right - bx[-1] > 0.5 * w:
		bx.append(x_right)
		bsemi.append(next_white(bsemi[-1]))

	keys = []  # (semi, black, cx, x0, x1)
	for i in range(len(bx) - 1):
		keys.append((bsemi[i], False, (bx[i] + bx[i + 1]) / 2, bx[i], bx[i + 1]))
	for x, s in zip(c, black_semi):
		keys.append((s, True, x, x - 0.3 * w, x + 0.3 * w))
	keys.sort()
	semis = np.array([k[0] for k in keys])
	if fixed is not None:
		# black key number fixed[0] (from the left) is MIDI note fixed[1]
		base = fixed[1] - black_semi[fixed[0]]
	elif len(keys) in (87, 88) and semis[0] % 12 == 9:
		base = 21 - semis[0]
	else:
		mid = float(np.median(semis))
		base = 12 * round((64 - mid) / 12)
	ok = (semis + base >= 21) & (semis + base <= 108)  # piano range
	keys = [k for k, o in zip(keys, ok) if o]
	semis = semis[ok]
	return Keyboard(
		midi=semis + base,
		black=np.array([k[1] for k in keys]),
		cx=np.array([k[2] for k in keys]),
		x0=np.array([k[3] for k in keys]),
		x1=np.array([k[4] for k in keys]),
		w=w, y0=int(y0), y1=int(y1), x_left=x_left, x_right=x_right,
	)


# ----------------------------------------------------------------------------
# colour helpers
# ----------------------------------------------------------------------------

def dist(a: np.ndarray, b: np.ndarray) -> np.ndarray:
	d = a.astype(np.float32) - b.astype(np.float32)
	return np.sqrt((d * d).sum(axis=-1))


def learn_colours(pixels: np.ndarray, merge_dist: float = 40.0, min_share: float = 0.004) -> np.ndarray:
	"""Dominant colours (BGR) of a pixel sample."""
	if len(pixels) < 50:
		return np.zeros((0, 3), np.float32)
	if len(pixels) > 150000:
		idx = np.random.default_rng(0).choice(len(pixels), 150000, replace=False)
		pixels = pixels[idx]
	data = pixels.astype(np.float32)
	k = min(10, len(data) // 10)
	crit = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 1.0)
	cv2.setRNGSeed(1)
	_, lab, cen = cv2.kmeans(data, k, None, crit, 3, cv2.KMEANS_PP_CENTERS)
	cnt = np.bincount(lab.ravel(), minlength=k).astype(np.float64)
	cen = cen.astype(np.float64)
	alive = cnt > 0
	while True:
		ids = np.flatnonzero(alive)
		best = None
		for ii, a in enumerate(ids):
			for b in ids[ii + 1:]:
				d = np.linalg.norm(cen[a] - cen[b])
				if d < merge_dist and (best is None or d < best[0]):
					best = (d, a, b)
		if best is None:
			break
		_, a, b = best
		cen[a] = (cen[a] * cnt[a] + cen[b] * cnt[b]) / (cnt[a] + cnt[b])
		cnt[a] += cnt[b]
		alive[b] = False
	keep = alive & (cnt >= min_share * cnt[alive].sum())
	return cen[keep].astype(np.float32)


def hue_groups(colours: np.ndarray) -> np.ndarray:
	"""Group colours by hue (shades of one colour = one group). Returns group id per colour."""
	n = len(colours)
	if n == 0:
		return np.zeros(0, int)
	hsv = cv2.cvtColor(colours.reshape(1, -1, 3).clip(0, 255).astype(np.uint8), cv2.COLOR_BGR2HSV)[0].astype(float)
	hue, sat, val = hsv[:, 0] * 2, hsv[:, 1] / 255, hsv[:, 2] / 255
	achro = (sat < 0.22) | (val < 0.2)
	parent = list(range(n))

	def find(i):
		while parent[i] != i:
			i = parent[i]
		return i

	for i in range(n):
		for j in range(i + 1, n):
			if achro[i] and achro[j]:
				parent[find(j)] = find(i)
			elif not achro[i] and not achro[j]:
				dh = abs(hue[i] - hue[j])
				if min(dh, 360 - dh) < 28:
					parent[find(j)] = find(i)
	roots = sorted({find(i) for i in range(n)})
	return np.array([roots.index(find(i)) for i in range(n)])


def noise_threshold(d: np.ndarray) -> float:
	return float(np.clip(6 * np.median(d) + 20, 35, 70))


def spatial_background(blk: np.ndarray, win: int) -> np.ndarray:
	"""Background of every frame row taken sideways: median colour over a wide horizontal window.

	Catches what a time-based model cannot: fades, flashes and a moving picture behind the notes.
	"""
	step = max(1, win // 40)
	sub = blk[:, ::step]
	k = max(3, (win // step) | 1)
	pad = k // 2
	padded = np.pad(sub, ((0, 0), (pad, pad), (0, 0)), mode='reflect')
	view = np.lib.stride_tricks.sliding_window_view(padded, k, axis=1)  # (t, x, 3, k)
	med = np.median(view, axis=-1)
	return np.repeat(med, step, axis=1)[:, : blk.shape[1]]


class Background:
	"""Per-column background colour of one image row over time (static or slowly changing)."""

	def __init__(self, rows: np.ndarray, fps: float) -> None:
		n = len(rows)
		self.rows = rows
		self.sub = max(1, n // 400)
		self.glob = np.median(rows[:: self.sub], axis=0).astype(np.float32)
		self.step = max(1, int(fps * 2))
		self.half = max(2, int(fps * 6))
		self.centers = list(range(0, n, self.step))
		self.chunks = np.stack([self._win(c).astype(np.float32) for c in self.centers])
		drift = np.abs(self.chunks - self.glob).mean()
		self.static = bool(drift < 8)

	def _slice(self, c):
		return self.rows[max(0, c - self.half): c + self.half: 4]

	def _win(self, c):
		return np.median(self._slice(c), axis=0)

	def refine(self, colours: np.ndarray, radius: float) -> None:
		"""Recompute ignoring note-coloured pixels, so long notes do not become background."""
		if len(colours) == 0:
			return

		def masked(block, fallback):
			b = block.astype(np.float32)
			nl = np.zeros(b.shape[:2], bool)
			for col in colours:
				nl |= dist(b, col) < radius
			b[nl] = np.nan
			with warnings.catch_warnings():
				warnings.simplefilter('ignore')
				med = np.nanmedian(b, axis=0)
			bad = (~nl).sum(axis=0) < 6
			med[bad] = fallback[bad]
			return med

		self.glob = masked(self.rows[:: self.sub], self.glob)
		if not self.static:
			self.chunks = np.stack([masked(self._slice(c), self.glob) for c in self.centers])

	def at(self, t0: int, t1: int) -> np.ndarray:
		"""Background for frames [t0, t1): shape (t1-t0, W, 3)."""
		if self.static:
			return np.broadcast_to(self.glob, (t1 - t0, *self.glob.shape))
		idx = np.clip(np.round(np.arange(t0, t1) / self.step).astype(int), 0, len(self.centers) - 1)
		return self.chunks[idx]


# ----------------------------------------------------------------------------
# video pass
# ----------------------------------------------------------------------------

def median_frame(cap, n_frames: int, f0: int, f1: int, count: int = 40):
	"""(median frame, per-pixel bright gray frame) of frames spread over the video."""
	frames = []
	for f in np.linspace(f0 + (f1 - f0) * 0.05, f0 + (f1 - f0) * 0.95, count).astype(int):
		cap.set(cv2.CAP_PROP_POS_FRAMES, int(f))
		ok, fr = cap.read()
		if ok:
			frames.append(fr)
	if not frames:
		sys.exit('cannot read frames from the video')
	st = np.stack(frames)
	gr = np.stack([cv2.cvtColor(f, cv2.COLOR_BGR2GRAY) for f in frames])
	return np.median(st, axis=0).astype(np.uint8), np.percentile(gr, 85, axis=0).astype(np.uint8), gr


def assign_piece(kb: Keyboard, a: int, b: int, white_idx: np.ndarray, out: list) -> None:
	"""Which keys does a horizontal piece [a, b) of one colour belong to."""
	w = kb.w
	width = b - a
	cen = (a + b) / 2
	if width < 1.3 * w:
		# one bar = one note: the key whose centre is closest (black keys sit between two white ones)
		k = int(np.argmin(np.abs(kb.cx - cen)))
		if abs(kb.cx[k] - cen) < 0.6 * w:
			out.append(k)
		return
	ov = np.minimum(kb.x1[white_idx], b) - np.maximum(kb.x0[white_idx], a)
	sel = white_idx[ov >= 0.5 * (kb.x1[white_idx] - kb.x0[white_idx])]
	if len(sel) == 0:
		k = int(np.argmin(np.abs(kb.cx - cen)))
		if abs(kb.cx[k] - cen) < 0.6 * w:
			out.append(k)
		return
	out.extend(sel.tolist())
	# a bar sticking out past the white keys it covers = the neighbouring black key (same colour)
	res = max(0.22 * w, 2.5)
	lo, hi = int(sel[0]), int(sel[-1])
	if kb.x0[lo] - a > res and lo > 0 and kb.black[lo - 1]:
		out.append(lo - 1)
	if b - kb.x1[hi] > res and hi + 1 < len(kb.midi) and kb.black[hi + 1]:
		out.append(hi + 1)


def align_lanes(kb: Keyboard, labels: np.ndarray, log) -> Keyboard:
	"""Falling bars are often drawn on their own grid, a little shifted or scaled against the filmed keys.

	Collect where single bars really fall over the whole video and move the key grid onto them.
	"""
	w = kb.w
	n, w_img = labels.shape
	cen = []
	for t in range(0, n, max(1, n // 4000)):
		for a, b in runs_of(labels[t] >= 0):
			if 0.4 * w <= b - a <= 1.25 * w:
				cen.append((a + b - 1) / 2)
	if len(cen) < 50:
		return kb
	bins = 4  # 0.25 px
	hist = np.bincount(np.round(np.array(cen) * bins).astype(int), minlength=w_img * bins + 1).astype(float)
	hist = np.convolve(hist, np.ones(3) / 3, mode='same')
	pk = [i for i in range(1, len(hist) - 1) if hist[i] >= hist[i - 1] and hist[i] > hist[i + 1] and hist[i] >= 5]
	if len(pk) < 6:
		return kb
	# keep the strongest peak in every half-key window
	pk.sort(key=lambda i: -hist[i])
	lanes, wts = [], []
	for i in pk:
		x = i / bins
		if all(abs(x - l) > 0.4 * w for l in lanes):
			lanes.append(x)
			wts.append(hist[i])
	lanes, wts = np.array(lanes), np.sqrt(np.array(wts))
	xc = float(np.average(lanes, weights=wts))  # pivot in the middle of the played lanes

	def cost_of(sc: float, d: float) -> float:
		pos = (kb.cx - xc) * sc + xc + d
		j = np.searchsorted(pos, lanes).clip(1, len(pos) - 1)
		dd = np.minimum(np.abs(lanes - pos[j - 1]), np.abs(lanes - pos[j]))
		return float((np.minimum(dd, 0.3 * w) * wts).sum())

	# coarse search over a wide range, then refine; ties go to the smaller change
	best = (cost_of(1.0, 0.0), 1.0, 0.0)
	for sc in np.arange(0.90, 1.1001, 0.004):
		for d in np.arange(-0.6 * w, 0.6 * w + 1e-9, 0.04 * w):
			c = cost_of(sc, d)
			if c < best[0] - 1e-6 * best[0] - 1e-9:
				best = (c, sc, d)
	_, s0, d0 = best
	for sc in np.arange(s0 - 0.004, s0 + 0.0041, 0.0005):
		for d in np.arange(d0 - 0.04 * w, d0 + 0.04 * w + 1e-9, 0.005 * w):
			c = cost_of(sc, d)
			if c < best[0] - 1e-9:
				best = (c, sc, d)
	_, sc, d = best
	if abs(d) < 0.05 and abs(sc - 1) < 1e-3:
		return kb

	def tr(x):
		return (x - xc) * sc + xc + d

	log(f'  roll: bars drawn {d:+.1f} px / x{sc:.3f} against the keys, grid adjusted')
	return Keyboard(midi=kb.midi, black=kb.black, cx=tr(kb.cx), x0=tr(kb.x0), x1=tr(kb.x1), w=kb.w * sc,
					y0=kb.y0, y1=kb.y1, x_left=kb.x_left, x_right=kb.x_right)


def analyse_roll(kb: Keyboard, row_a: np.ndarray, row_b: np.ndarray, strip: np.ndarray, fps: float, d_rows: int, margin: int, log):
	"""Falling-notes reading. Returns (on[n, keys] colour index or -1, colours, splits, speed, frame shift)."""
	n, w_img, _ = row_a.shape
	nk = len(kb.midi)
	bg = Background(row_a, fps)
	# pass 1: everything that is not background
	smp = slice(None, None, max(1, n // 600))
	win = int(14 * kb.w)
	d0 = dist(row_a[smp], bg.at(0, n)[smp])
	thr = noise_threshold(d0)
	colours = learn_colours(row_a[smp][(d0 > thr) & (dist(row_a[smp], spatial_background(row_a[smp], win)) > thr)])
	if len(colours) == 0:
		return None
	radius = 90.0
	min_piece = max(2, int(round(0.25 * kb.w)))

	def label_all(rows=None, bgm=None) -> np.ndarray:
		"""Label every pixel of the scan row with its note colour (or -1)."""
		rows = row_a if rows is None else rows
		bgm = bg if bgm is None else bgm
		lab = np.full((n, w_img), -1, np.int8)
		for t0 in range(0, n, 512):
			t1 = min(n, t0 + 512)
			blk = rows[t0:t1]
			dc = np.stack([dist(blk, c) for c in colours], axis=-1)
			ok = (dc.min(axis=-1) < radius) & (dist(blk, bgm.at(t0, t1)) > thr)
			ok &= dist(blk, spatial_background(blk, win)) > thr
			lab[t0:t1] = np.where(ok, dc.argmin(axis=-1), -1)
		return lab

	# keep only the colours that really form bars (key-wide and lasting several frames);
	# background texture, glow and noise colours do not
	labels = label_all()
	kern_x, kern_t = np.ones((1, min_piece), np.uint8), np.ones((3, 1), np.uint8)
	keep = []
	for ci in range(len(colours)):
		mc = (labels == ci).astype(np.uint8)
		tot = int(mc.sum())
		if tot == 0:
			continue
		op = cv2.morphologyEx(cv2.morphologyEx(mc, cv2.MORPH_OPEN, kern_x), cv2.MORPH_OPEN, kern_t)
		if op.sum() >= 0.35 * tot:
			keep.append(ci)
	if not keep:
		return None
	colours = colours[keep]
	labels = label_all()

	# notes fall: whatever appears on the scan row appeared on a higher row some frames earlier.
	# The delay is measured on the moments things appear, so a still background picture does not count.
	bg_b = Background(row_b, fps)
	labels_b = label_all(row_b, bg_b)
	max_lag = max(4, min(n // 3, int(d_rows / 0.7)))
	kern3 = np.ones((3, 3), np.uint8)

	def onsets(m: np.ndarray, wide: bool = False) -> np.ndarray:
		e = np.zeros(m.shape, np.uint8)
		e[1:] = m[1:] & ~m[:-1]
		return cv2.dilate(e, kern3).astype(bool) if wide else e.astype(bool)

	ea, eb = onsets(labels >= 0), onsets(labels_b >= 0, True)
	sc = np.array([0.0] + [float((eb[: n - lag] & ea[lag:]).sum()) for lag in range(1, max_lag)])
	pk = int(sc.argmax())
	speed, lag_i = None, 0
	if os.environ.get('V2M_DEBUG'):
		log('  lag curve', np.round(sc[:40]).astype(int).tolist(), 'peak', pk, 'median', float(np.median(sc[1:])), 'onsets', int(ea.sum()))
	if pk >= 1 and sc[pk] > 2.5 * np.median(sc[1:]) + 1e-9 and sc[pk] >= 0.15 * ea.sum():
		lag = float(pk)
		if pk < len(sc) - 1:
			den = sc[pk - 1] - 2 * sc[pk] + sc[pk + 1]
			if den < 0:
				lag += 0.5 * (sc[pk - 1] - sc[pk + 1]) / den
		speed, lag_i = d_rows / lag, pk
		# a colour whose appearances are not repeated on the higher row is not a falling note
		keep = []
		for ci in range(len(colours)):
			ca = onsets(labels == ci)
			cb = onsets(labels_b == ci, True)
			if ca.sum() and (cb[: n - pk] & ca[pk:]).sum() >= 0.08 * ca[pk:].sum():
				keep.append(ci)
		if not keep:
			return None
		colours = colours[keep]
	bg.refine(colours, radius)
	bg_b.refine(colours, radius)
	labels = label_all()
	labels_b = label_all(row_b, bg_b)
	log(f'  roll: background is {"static" if bg.static else "changing"}, threshold {thr:.0f}, {len(colours)} note colour shade(s)')

	kb = align_lanes(kb, labels, log)
	# typical bar width: when bars are drawn narrower than the keys (with gaps between them),
	# a light patch many keys wide is a background picture, not a chord
	wd = [b - a for t in range(0, n, max(1, n // 3000)) for a, b in runs_of(labels[t] >= 0)]
	wd = np.array([x for x in wd if 0.3 * kb.w <= x <= 1.6 * kb.w])
	bar_w = float(np.median(wd)) if len(wd) > 50 else kb.w
	max_piece = 2.0 * kb.w if bar_w < 0.9 * kb.w else 1e9
	white_idx = np.flatnonzero(~kb.black)
	hole = max(1, int(0.1 * kb.w))
	min_run = max(2, min_piece // 2)
	xl, xr = max(0, int(kb.x_left)), min(w_img, int(math.ceil(kb.x_right)))
	def keys_on(labels: np.ndarray) -> np.ndarray:
		"""Which key shows which note colour in every frame."""
		on = np.full((n, nk), -1, np.int8)
		for t in range(n):
			lab = labels[t]
			m = lab >= 0
			if not m.any():
				continue
			if m[xl:xr].mean() > 0.5:
				# a line across the whole keyboard (bar line, flash) is not a chord: keep the previous state
				if t > 0:
					on[t] = on[t - 1]
				continue
			rs = [r for r in runs_of(m) if r[1] - r[0] >= min_run]
			if not rs:
				continue
			# close small holes
			merged = [list(rs[0])]
			for a, b in rs[1:]:
				if a - merged[-1][1] <= hole:
					merged[-1][1] = b
				else:
					merged.append([a, b])
			for a, b in merged:
				if b - a < min_piece or b - a > max_piece:
					continue
				seg = lab[a:b].copy()
				# holes take the label on their left
				for i in np.flatnonzero(seg < 0):
					seg[i] = seg[i - 1] if i > 0 else seg[seg >= 0][0]
				cuts = [0, *(np.flatnonzero(np.diff(seg)) + 1).tolist(), len(seg)]
				pieces = [[cuts[i], cuts[i + 1], int(seg[cuts[i]])] for i in range(len(cuts) - 1)]
				# merge slivers (borders, antialiasing) into the bigger neighbour
				while len(pieces) > 1:
					i = min(range(len(pieces)), key=lambda q: pieces[q][1] - pieces[q][0])
					if pieces[i][1] - pieces[i][0] >= min_piece:
						break
					if i == 0:
						j = 1
					elif i == len(pieces) - 1:
						j = i - 1
					else:
						j = i - 1 if (pieces[i - 1][1] - pieces[i - 1][0]) >= (pieces[i + 1][1] - pieces[i + 1][0]) else i + 1
					pieces[j][0] = min(pieces[j][0], pieces[i][0])
					pieces[j][1] = max(pieces[j][1], pieces[i][1])
					del pieces[i]
				# neighbours with the same label after merging
				k = 0
				while k + 1 < len(pieces):
					if pieces[k][2] == pieces[k + 1][2]:
						pieces[k][1] = pieces[k + 1][1]
						del pieces[k + 1]
					else:
						k += 1
				for pa, pb, pl in pieces:
					ks: list[int] = []
					assign_piece(kb, a + pa, a + pb, white_idx, ks)
					for key in ks:
						on[t, key] = pl
		return on

	on = keys_on(labels)
	on_b = keys_on(labels_b)

	# frames where the whole picture suddenly changes (flash, inverted colours, cut) cannot be read
	bg_med = np.median(bg.at(0, n), axis=1) if not bg.static else np.broadcast_to(np.median(bg.glob, axis=0), (n, 3))
	odd = dist(np.median(row_a, axis=1), bg_med) > thr
	if odd.mean() > 0.4:
		odd[:] = False
	# a flash is short; a long stretch with another look is a new scene and is read normally
	for a, b in runs_of(odd):
		if b - a > fps:
			odd[a:b] = False
	if speed:
		lag = lag_i
		# every note must have been seen falling: the same key lit on the higher row `lag` frames earlier
		for k in range(nk):
			for a, b in runs_of(on[:, k] >= 0):
				if a - lag < 0:
					continue
				seen = on_b[a - lag: b - lag, k][~odd[a - lag: b - lag] & ~odd[a:b]]
				if len(seen) and (seen >= 0).mean() < 0.4:
					on[a:b, k] = -1
		# unreadable frames: take what the higher row showed `lag` frames earlier
		for t in np.flatnonzero(odd):
			if t - lag >= 0 and not odd[t - lag]:
				on[t] = on_b[t - lag]
			elif t > 0:
				on[t] = on[t - 1]
	else:
		for t in np.flatnonzero(odd):
			if t > 0:
				on[t] = on[t - 1]
	if odd.any():
		log(f'  roll: {int(odd.sum())} unreadable frame(s) (flashes) bridged')
	if speed:
		log(f'  roll: notes fall at {speed:.2f} px/frame')
	else:
		log('  roll: fall speed not measurable')

	# sub-frame gaps between repeated notes: look at the rows that pass the scan line before the next frame
	splits = {}
	if speed and speed >= 1.5:
		jmax = min(strip.shape[1] - 1, int(round(speed)))
		kcx = np.clip(np.round(kb.cx).astype(int), 0, w_img - 1)
		for t in range(n - 1):
			held = np.flatnonzero((on[t] >= 0) & (on[t + 1] >= 0))
			if len(held) == 0:
				continue
			bgk = bg.at(t, t + 1)[0][kcx[held]]
			ref = strip[t, 0, held].astype(np.float32)
			sj = strip[t, 1: jmax + 1, held].astype(np.float32)  # (held, j, 3)
			if sj.ndim == 2:
				sj = sj[None]
			d_ref = np.sqrt(((sj - ref[:, None]) ** 2).sum(-1))
			d_bg = np.sqrt(((sj - bgk[:, None]) ** 2).sum(-1))
			gap = (d_bg < d_ref) & (d_ref > thr * 0.6)
			for hi in np.flatnonzero(gap.any(axis=1)):
				js = np.flatnonzero(gap[hi]) + 1
				splits[(t, int(held[hi]))] = (js[0] / speed, min(1.0, (js[-1] + 1) / speed))
	shift = margin / speed if speed else 0.0
	return on, colours, splits, speed, shift


def analyse_keys(kb: Keyboard, samples: np.ndarray, fps: float, log):
	"""Lit-keys reading. Returns (on, colours)."""
	n, nk, _ = samples.shape
	rest = np.median(samples[:: max(1, n // 600)], axis=0).astype(np.float32)
	d = dist(samples, rest[None])
	thr = max(45.0, noise_threshold(d[:: max(1, n // 600)]))
	m = d > thr
	colours = learn_colours(samples[m])
	if len(colours) == 0:
		return None
	dc = np.stack([dist(samples, c) for c in colours], axis=-1)
	on = np.where(m & (dc.min(-1) < 90), dc.argmin(-1), -1).astype(np.int8)
	log(f'  keys: threshold {thr:.0f}, {len(colours)} lit colour shade(s)')
	return on, colours


def build_notes(on: np.ndarray, groups: np.ndarray, splits: dict, min_frames: float):
	"""(key index, channel group, start frame, end frame) list."""
	n, nk = on.shape
	notes = []
	g = np.where(on >= 0, groups[np.clip(on, 0, None)], -1)
	for k in range(nk):
		col = g[:, k]
		if not (col >= 0).any():
			continue
		chg = np.flatnonzero(np.diff(col)) + 1
		bounds = [0, *chg.tolist(), n]
		for i in range(len(bounds) - 1):
			a, b = bounds[i], bounds[i + 1]
			if col[a] < 0:
				continue
			start = float(a)
			for t in range(a, b - 1):
				sp = splits.get((t, k))
				if sp:
					end = t + sp[0]
					if end - start >= min_frames:
						notes.append((k, int(col[a]), start, end))
					start = t + sp[1]
			if b - start >= min_frames:
				notes.append((k, int(col[a]), start, float(b)))
	return notes


def write_midi(path: str, kb: Keyboard, notes, fps: float, shift: float, tempo: int = 120) -> None:
	mf = MIDIFile(1, removeDuplicates=True, deinterleave=False, adjust_origin=False)
	mf.addTrackName(0, 0, 'Piano')
	mf.addTempo(0, 0, tempo)
	bps = tempo / 60.0
	for ch in sorted({c for _, c, _, _ in notes}):
		mf.addProgramChange(0, ch, 0, 0)
	for k, ch, a, b in sorted(notes, key=lambda q: q[2]):
		t0 = max(0.0, (a + shift) / fps)
		mf.addNote(0, ch, int(kb.midi[k]), t0 * bps, max(0.02, (b - a) / fps) * bps, 100)
	with open(path, 'wb') as f:
		mf.writeFile(f)


def draw_debug(path: str, frame: np.ndarray, kb: Keyboard, y_scan: int, y_white: int) -> None:
	img = frame.copy()
	h = img.shape[0]
	for i in range(len(kb.midi)):
		if kb.black[i]:
			cv2.line(img, (int(kb.cx[i]), kb.y0), (int(kb.cx[i]), kb.y1), (0, 0, 255), 1)
		else:
			cv2.line(img, (int(kb.x0[i]), kb.y0), (int(kb.x0[i]), min(h - 1, y_white + 6)), (255, 160, 0), 1)
			if kb.midi[i] % 12 == 0:
				cv2.putText(img, note_name(int(kb.midi[i])), (int(kb.x0[i]) + 1, max(10, y_scan - 4)),
							cv2.FONT_HERSHEY_SIMPLEX, 0.35, (0, 255, 255), 1)
	cv2.line(img, (0, y_scan), (img.shape[1], y_scan), (0, 255, 0), 1)
	cv2.imwrite(path, img)


def convert(video: str, out: str | None = None, mode: str = 'auto', start: float = 0.0, end: float | None = None,
			debug: bool = False, octave: int = 0, quiet: bool = False) -> dict:
	def log(*a):
		if not quiet:
			print(*a, flush=True)

	cap = cv2.VideoCapture(video)
	if not cap.isOpened():
		sys.exit(f'cannot open video: {video}')
	fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
	total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
	h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
	w_img = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
	f0 = max(0, int(start * fps))
	f1 = total if end is None else min(total, int(end * fps))
	log(f'{os.path.basename(video)}: {w_img}x{h}, {fps:.2f} fps, {(f1 - f0) / fps:.1f} s')

	med, gray_hi, grays = median_frame(cap, total, f0, f1)
	kb = detect_keyboard(cv2.cvtColor(med, cv2.COLOR_BGR2GRAY), gray_hi)
	if kb is None:
		sys.exit('keyboard not found in the video (no row with a black-key pattern)')
	kb = refine_keyboard(kb, grays, log)
	kb.midi = kb.midi + 12 * octave
	nk = len(kb.midi)
	log(f'keyboard: {nk} keys {note_name(int(kb.midi[0]))}..{note_name(int(kb.midi[-1]))}, '
		f'rows {kb.y0}-{kb.y1}, white key {kb.w:.1f} px')

	margin = max(6, int(round(0.07 * h)))
	y_a = max(1, kb.y0 - margin)
	d_rows = max(8, int(round(0.12 * h)))
	y_b = max(0, y_a - d_rows)
	d_rows = y_a - y_b
	k_rows = min(y_a, max(4, math.ceil(0.05 * h)))
	# sample columns per key for the strip and for the lit-key patches
	off = np.where(kb.black, 0.12, 0.15) * kb.w
	cols = np.clip(np.round(np.stack([kb.cx - off, kb.cx, kb.cx + off], axis=1)).astype(int), 0, w_img - 1)
	gray = cv2.cvtColor(med, cv2.COLOR_BGR2GRAY).astype(np.float32)
	band = kb.y1 - kb.y0
	wcx = np.clip(np.round(kb.cx[~kb.black]).astype(int), 0, w_img - 1)
	cand = range(min(h - 1, kb.y1 + 3), min(h, kb.y1 + max(4, band)))
	y_white = max(cand, key=lambda y: float(np.median(gray[y, wcx]))) if len(cand) else min(h - 1, kb.y1 + 2)
	y_black = kb.y0 + band // 2
	key_y = np.where(kb.black, y_black, y_white)

	n = f1 - f0
	row_a = np.zeros((n, w_img, 3), np.uint8)
	row_b = np.zeros((n, w_img, 3), np.uint8)
	strip = np.zeros((n, k_rows + 1, nk, 3), np.uint8)
	samples = np.zeros((n, nk, 3), np.uint8)
	cap.set(cv2.CAP_PROP_POS_FRAMES, f0)
	t = 0
	dbg_frame = None
	while t < n:
		ok, fr = cap.read()
		if not ok:
			break
		row_a[t] = fr[y_a]
		row_b[t] = fr[y_b]
		st = fr[y_a - k_rows: y_a + 1][::-1]  # row 0 = scan row, then upwards
		strip[t] = np.median(st[:, cols], axis=2)
		samples[t] = np.median(fr[key_y[:, None], cols], axis=1)
		if t == n // 2:
			dbg_frame = fr.copy()
		t += 1
		if t % max(1, n // 10) == 0:
			log(f'  reading video {100 * t // n}%')
	cap.release()
	n = t
	row_a, row_b, strip, samples = row_a[:n], row_b[:n], strip[:n], samples[:n]
	if n < 5:
		sys.exit('video too short')
	if debug and dbg_frame is not None:
		dpath = os.path.splitext(out or video)[0] + '_auto_debug.jpg'
		draw_debug(dpath, dbg_frame, kb, y_a, y_white)
		log(f'debug picture: {dpath}')

	results = {}
	if mode in ('auto', 'roll'):
		r = analyse_roll(kb, row_a, row_b, strip, fps, d_rows, kb.y0 - y_a, log)
		if r is not None:
			on, colours, splits, speed, shift = r
			groups = hue_groups(colours)
			results['roll'] = (build_notes(on, groups, splits, 2.0), colours, groups, shift)
	if mode in ('auto', 'keys'):
		r = analyse_keys(kb, samples, fps, log)
		if r is not None:
			on, colours = r
			groups = hue_groups(colours)
			results['keys'] = (build_notes(on, groups, {}, 2.0), colours, groups, 0.0)
	if not results:
		sys.exit('no notes found')
	n_roll = len(results['roll'][0]) if 'roll' in results else 0
	n_keys = len(results['keys'][0]) if 'keys' in results else 0
	if mode == 'auto':
		log(f'  candidates: roll {n_roll} notes, lit keys {n_keys} notes')
	used = 'roll' if ('roll' in results and (n_roll >= max(10, 0.3 * n_keys) or 'keys' not in results)) else 'keys'
	if used not in results:
		used = next(iter(results))
	notes, colours, groups, shift = results[used]
	if not notes:
		sys.exit('no notes found')

	# channels: highest-pitched colour first (usually the right hand)
	gids = sorted({g for _, g, _, _ in notes})
	mean_pitch = {g: np.mean([kb.midi[k] for k, gg, _, _ in notes if gg == g]) for g in gids}
	order = sorted(gids, key=lambda g: -mean_pitch[g])[:16]
	chan = {g: i for i, g in enumerate(order)}
	notes = [(k, chan[g], a, b) for k, g, a, b in notes if g in chan]

	out = out or (video + '_auto.mid')
	write_midi(out, kb, notes, fps, shift)
	log(f'mode: {used}; {len(notes)} notes, {len(order)} channel(s)')
	for g in order:
		c = colours[groups == g].mean(axis=0)
		cnt = sum(1 for q in notes if q[1] == chan[g])
		log(f'  channel {chan[g] + 1}: {cnt} notes, colour RGB({c[2]:.0f},{c[1]:.0f},{c[0]:.0f})')
	log(f'saved: {out}')
	return {'mode': used, 'notes': len(notes), 'channels': len(order), 'out': out, 'keys': nk,
			'low': int(kb.midi[0]), 'high': int(kb.midi[-1])}


def main() -> None:
	ap = argparse.ArgumentParser(description='Automatic piano video -> MIDI (no manual setup).')
	ap.add_argument('video', nargs='+', help='video file(s)')
	ap.add_argument('-o', '--out', help='output .mid (single video only)')
	ap.add_argument('--mode', choices=['auto', 'roll', 'keys'], default='auto',
					help='roll = read falling notes, keys = read lit keys (default: decide automatically)')
	ap.add_argument('--start', type=float, default=0.0, help='start time, seconds')
	ap.add_argument('--end', type=float, default=None, help='end time, seconds')
	ap.add_argument('--octave', type=int, default=0, help='shift the result by N octaves')
	ap.add_argument('--debug', action='store_true', help='save a picture with the detected keys')
	a = ap.parse_args()
	for v in a.video:
		convert(v, a.out if len(a.video) == 1 else None, a.mode, a.start, a.end, a.debug, a.octave)


if __name__ == '__main__':
	main()
