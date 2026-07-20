import os

import pygame

_FONT_ASSET = os.path.join(os.path.dirname(__file__), 'assets', 'DejaVuSans.ttf')

_GL_CONST_NAMES = [
	'GL_ALPHA_TEST', 'GL_BGR', 'GL_BLEND', 'GL_COLOR_BUFFER_BIT', 'GL_COMPILE',
	'GL_CULL_FACE', 'GL_DECAL', 'GL_DEPTH_BUFFER_BIT', 'GL_DEPTH_TEST', 'GL_ENABLE_BIT',
	'GL_GEQUAL', 'GL_LINEAR', 'GL_LINE_LOOP', 'GL_MODELVIEW', 'GL_NEAREST', 'GL_ONE',
	'GL_ONE_MINUS_SRC_ALPHA', 'GL_PROJECTION', 'GL_QUADS', 'GL_REPEAT', 'GL_RGB',
	'GL_RGBA', 'GL_SRC_ALPHA', 'GL_TEXTURE_2D', 'GL_TEXTURE_ENV', 'GL_TEXTURE_ENV_MODE',
	'GL_TEXTURE_MAG_FILTER', 'GL_TEXTURE_MIN_FILTER', 'GL_TEXTURE_WRAP_S',
	'GL_TEXTURE_WRAP_T', 'GL_TRIANGLES', 'GL_UNPACK_ALIGNMENT', 'GL_UNSIGNED_BYTE',
]

try:
	import OpenGL.GL as _GL
	from OpenGL.GL import *  # noqa: F403 - real GL functions/constants pass through unchanged
	_HAS_OPENGL = True
	_OPENGL_IMPORT_ERROR = None
except Exception as _e:
	_GL = None
	_HAS_OPENGL = False
	_OPENGL_IMPORT_ERROR = _e
	# Placeholder values so call sites like `glDisable(GL_TEXTURE_2D)` don't NameError
	# in software mode - glEnable/glDisable/glBlendFunc below are no-ops in that mode,
	# so the actual numeric identity of these placeholders is never used.
	for _i, _name in enumerate(_GL_CONST_NAMES):
		globals()[_name] = _i

USE_OPENGL = True


def gl_available() -> bool:
	return _HAS_OPENGL


def gl_import_error():
	return _OPENGL_IMPORT_ERROR


_offset_stack = [(0.0, 0.0)]
_current_color = (255, 255, 255, 255)
_target_surface = None
_font_cache = {}
_scratch_cache = {}


def set_target_surface(surface) -> None:
	global _target_surface
	_target_surface = surface


def target_surface():
	return _target_surface


def current_offset() -> tuple[float, float]:
	return _offset_stack[-1]


def current_color() -> tuple[int, int, int, int]:
	return _current_color


def get_font(size: int) -> pygame.font.Font:
	f = _font_cache.get(size)
	if f is None:
		f = pygame.font.Font(_FONT_ASSET, size)
		_font_cache[size] = f
	return f


def get_scratch_surface(kind: str, w: int, h: int) -> pygame.Surface:
	w = max(1, int(w))
	h = max(1, int(h))
	key = (kind, w, h)
	s = _scratch_cache.get(key)
	if s is None:
		s = pygame.Surface((w, h), pygame.SRCALPHA)
		_scratch_cache[key] = s
	else:
		s.fill((0, 0, 0, 0))
	return s


def glPushMatrix() -> None:
	if USE_OPENGL:
		_GL.glPushMatrix()
	else:
		_offset_stack.append(_offset_stack[-1])


def glPopMatrix() -> None:
	if USE_OPENGL:
		_GL.glPopMatrix()
	else:
		_offset_stack.pop()


def glTranslatef(x, y, z=0) -> None:
	if USE_OPENGL:
		_GL.glTranslatef(x, y, z)
	else:
		ox, oy = _offset_stack[-1]
		_offset_stack[-1] = (ox + x, oy + y)


def glColor4f(r, g, b, a=1.0) -> None:
	if USE_OPENGL:
		_GL.glColor4f(r, g, b, a)
	else:
		global _current_color
		_current_color = (int(r * 255), int(g * 255), int(b * 255), int(a * 255))


def glColor4ub(r, g, b, a=255) -> None:
	if USE_OPENGL:
		_GL.glColor4ub(r, g, b, a)
	else:
		global _current_color
		_current_color = (int(r), int(g), int(b), int(a))


def glEnable(cap) -> None:
	if USE_OPENGL:
		_GL.glEnable(cap)


def glDisable(cap) -> None:
	if USE_OPENGL:
		_GL.glDisable(cap)


def glBlendFunc(a, b) -> None:
	if USE_OPENGL:
		_GL.glBlendFunc(a, b)


def glLineWidth(w) -> None:
	if USE_OPENGL:
		_GL.glLineWidth(w)
