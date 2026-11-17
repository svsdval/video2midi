"""Score v2m_auto against the synthetic videos: python tests/score_auto.py synth_dir"""
from __future__ import annotations

import glob
import json
import os
import sys

import mido

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import v2m_auto  # noqa: E402


def read_midi(path: str):
	mid = mido.MidiFile(path)
	out, on, tempo, t = [], {}, 500000, 0.0
	for msg in mido.merge_tracks(mid.tracks):
		t += mido.tick2second(msg.time, mid.ticks_per_beat, tempo)
		if msg.type == 'set_tempo':
			tempo = msg.tempo
		elif msg.type == 'note_on' and msg.velocity > 0:
			on.setdefault((msg.channel, msg.note), []).append(t)
		elif msg.type in ('note_off', 'note_on'):
			k = (msg.channel, msg.note)
			if on.get(k):
				out.append((msg.note, on[k].pop(0), t, msg.channel))
	return out


def score(truth, got, tol=0.12):
	"""Onset matching: same pitch, start within tol seconds. Returns precision, recall, wrong-pitch count, hand accuracy."""
	used = set()
	tp = 0
	hand_pairs = []
	for n in truth:
		best = None
		for j, g in enumerate(got):
			if j in used or g[0] != n['note']:
				continue
			d = abs(g[1] - n['start'])
			if d <= tol and (best is None or d < best[0]):
				best = (d, j)
		if best:
			used.add(best[1])
			tp += 1
			hand_pairs.append((n['hand'], got[best[1]][3]))
	# wrong pitch: an unmatched detected note that starts with an unmatched true note but has another pitch
	wrong = 0
	for j, g in enumerate(got):
		if j in used:
			continue
		if any(abs(g[1] - n['start']) <= tol for n in truth):
			wrong += 1
	# hands: best one-to-one mapping of hands to channels
	hand_ok = 0
	if hand_pairs:
		m1 = sum(1 for a, b in hand_pairs if a == b)
		m2 = sum(1 for a, b in hand_pairs if a != b)
		hand_ok = max(m1, m2) / len(hand_pairs)
	p = tp / max(1, len(got))
	r = tp / max(1, len(truth))
	return p, r, wrong, hand_ok


def main():
	d = sys.argv[1] if len(sys.argv) > 1 else 'synth'
	rows = []
	for v in sorted(glob.glob(os.path.join(d, '*.mp4'))):
		name = os.path.splitext(os.path.basename(v))[0]
		truth = json.load(open(os.path.join(d, name + '.truth.json')))
		out = os.path.join(d, name + '.auto.mid')
		v2m_auto.convert(v, out, quiet=True)
		got = read_midi(out)
		p, r, wrong, hand = score(truth, got)
		rows.append((name, len(truth), len(got), p, r, wrong, hand))
		print(f'{name:28s} truth {len(truth):4d}  got {len(got):4d}  precision {p:.3f}  recall {r:.3f}  '
			f'wrong-pitch {wrong:3d}  hands {hand:.2f}', flush=True)
	return rows


if __name__ == '__main__':
	main()
