"""Counter-based Threefry-4x64-20 generator matching the reference stream.

This reproduces, bit-for-bit, the uniform ``[0, 1)`` stream of the external
reference implementation's ``rng(seed, 'threefry')`` global generator, so the
Python port can reproduce the reference convergence data exactly.

Reverse-engineered seeding (validated against the reference RandStream
``State`` for several seeds and against raw ``rand`` draws to machine epsilon):

* Algorithm: Threefry-4x64-20 (Random123), key ``(0, 0, 0, 0)``.
* Counter from the integer seed ``S``::

      counter[j] = ((S + 2*j + 1) << 32) | (S + 2*j)   for j in 0..3

* Each block applies the 20-round Threefry permutation to the counter and
  yields four uint64 outputs; output word ``w`` becomes a double via
  ``(w >> 11) * 2**-53`` (the canonical 53-bit conversion).
* The counter's low 64-bit word advances by one per four-output block, with
  little-endian carry into the higher words.

Matrix draws fill **column-major** (Fortran order) to match the reference
``rand(m, n)`` memory layout; an ``N``-d request fills its trailing two axes
column-major with leading axes indexing successive draws, so a single
``random((k, m, n))`` call equals ``k`` successive column-major ``rand(m, n)``
draws on the reference side.

Exact-parity scope: ``random`` reproduces the reference ``rand`` stream
bit-for-bit. ``integers`` and ``permutation`` reproduce the reference ``randi``
and ``randperm`` too -- validated against reference draws:

* ``randi(imax)`` == ``floor(imax * rand) + 1`` (one double per integer);
* ``randperm(n)`` == the sort method ``[~, p] = sort(rand(1, n))`` (n doubles),
  i.e. ``argsort`` of n fresh draws.
"""

from __future__ import annotations

import copy
from typing import Any

import numpy as np

from gsk_family.common.reference_rng import DoublesStreamGenerator

try:  # numba is a hard dependency; without it the kernel runs as plain Python.
    from numba import njit

    _HAVE_NUMBA = True
except Exception:  # pragma: no cover - exercised only when numba is unavailable.
    _HAVE_NUMBA = False


def _fill_doubles_kernel(
    c0: np.uint64,
    c1: np.uint64,
    c2: np.uint64,
    c3: np.uint64,
    start_block: int,
    n_blocks: int,
    out: np.ndarray,
) -> None:
    """Fill ``out`` (length ``n_blocks * 4``) from consecutive Threefry blocks.

    The counter words ``c0..c3`` must be passed as ``np.uint64``: their full 64-bit
    range is used (the top word can exceed ``2**63 - 1`` for seeds near the unified
    cap ``MAX_SAFE_SEED = 2147483646``), and Numba would otherwise box a plain
    Python ``int`` as ``int64`` and raise ``OverflowError`` at the call boundary.
    """
    parity = np.uint64(0x1BD11BDAA9FC1A22)
    # Rotation constants and the 4-round key-injection schedule are folded
    # into the unrolled round sequence below as literals (see the loop that
    # used to live here in git history). Emitted mechanically by
    # gen_threefry_unroll.py; verified bitwise on 980,000 doubles across 8
    # seeds, 6 counter offsets and the carry/wraparound path.
    u5 = np.uint64(5)
    u6 = np.uint64(6)
    u7 = np.uint64(7)
    u12 = np.uint64(12)
    u14 = np.uint64(14)
    u16 = np.uint64(16)
    u18 = np.uint64(18)
    u22 = np.uint64(22)
    u23 = np.uint64(23)
    u24 = np.uint64(24)
    u25 = np.uint64(25)
    u27 = np.uint64(27)
    u31 = np.uint64(31)
    u32 = np.uint64(32)
    u33 = np.uint64(33)
    u37 = np.uint64(37)
    u39 = np.uint64(39)
    u40 = np.uint64(40)
    u41 = np.uint64(41)
    u42 = np.uint64(42)
    u46 = np.uint64(46)
    u48 = np.uint64(48)
    u50 = np.uint64(50)
    u52 = np.uint64(52)
    u57 = np.uint64(57)
    u58 = np.uint64(58)
    u59 = np.uint64(59)
    u_s1 = np.uint64(1)
    u_s2 = np.uint64(2)
    u_s3 = np.uint64(3)
    u_s4 = np.uint64(4)
    u_s5 = np.uint64(5)
    base0 = np.uint64(c0)
    base1 = np.uint64(c1)
    base2 = np.uint64(c2)
    base3 = np.uint64(c3)
    one = np.uint64(1)
    shift = np.uint64(11)
    scale = 2.0**-53
    for b in range(n_blocks):
        word0 = base0 + np.uint64(start_block + b)
        word1 = base1
        word2 = base2
        word3 = base3
        if word0 < base0:  # little-endian carry (rare for realistic budgets)
            word1 = base1 + one
            if word1 < base1:
                word2 = base2 + one
                if word2 < base2:
                    word3 = base3 + one
        x0 = word0
        x1 = word1
        x2 = word2
        x3 = word3
        # --- round 0 (rot 14/16) ---
        x0 = x0 + x1
        x1 = ((x1 << u14) | (x1 >> u50)) ^ x0
        x2 = x2 + x3
        x3 = ((x3 << u16) | (x3 >> u48)) ^ x2
        tmp = x1
        x1 = x3
        x3 = tmp
        # --- round 1 (rot 52/57) ---
        x0 = x0 + x1
        x1 = ((x1 << u52) | (x1 >> u12)) ^ x0
        x2 = x2 + x3
        x3 = ((x3 << u57) | (x3 >> u7)) ^ x2
        tmp = x1
        x1 = x3
        x3 = tmp
        # --- round 2 (rot 23/40) ---
        x0 = x0 + x1
        x1 = ((x1 << u23) | (x1 >> u41)) ^ x0
        x2 = x2 + x3
        x3 = ((x3 << u40) | (x3 >> u24)) ^ x2
        tmp = x1
        x1 = x3
        x3 = tmp
        # --- round 3 (rot 5/37) ---
        x0 = x0 + x1
        x1 = ((x1 << u5) | (x1 >> u59)) ^ x0
        x2 = x2 + x3
        x3 = ((x3 << u37) | (x3 >> u27)) ^ x2
        tmp = x1
        x1 = x3
        x3 = tmp
        x3 = x3 + parity   # k[4] @ s=1, word 3
        x3 = x3 + u_s1
        # --- round 4 (rot 25/33) ---
        x0 = x0 + x1
        x1 = ((x1 << u25) | (x1 >> u39)) ^ x0
        x2 = x2 + x3
        x3 = ((x3 << u33) | (x3 >> u31)) ^ x2
        tmp = x1
        x1 = x3
        x3 = tmp
        # --- round 5 (rot 46/12) ---
        x0 = x0 + x1
        x1 = ((x1 << u46) | (x1 >> u18)) ^ x0
        x2 = x2 + x3
        x3 = ((x3 << u12) | (x3 >> u52)) ^ x2
        tmp = x1
        x1 = x3
        x3 = tmp
        # --- round 6 (rot 58/22) ---
        x0 = x0 + x1
        x1 = ((x1 << u58) | (x1 >> u6)) ^ x0
        x2 = x2 + x3
        x3 = ((x3 << u22) | (x3 >> u42)) ^ x2
        tmp = x1
        x1 = x3
        x3 = tmp
        # --- round 7 (rot 32/32) ---
        x0 = x0 + x1
        x1 = ((x1 << u32) | (x1 >> u32)) ^ x0
        x2 = x2 + x3
        x3 = ((x3 << u32) | (x3 >> u32)) ^ x2
        tmp = x1
        x1 = x3
        x3 = tmp
        x2 = x2 + parity   # k[4] @ s=2, word 2
        x3 = x3 + u_s2
        # --- round 8 (rot 14/16) ---
        x0 = x0 + x1
        x1 = ((x1 << u14) | (x1 >> u50)) ^ x0
        x2 = x2 + x3
        x3 = ((x3 << u16) | (x3 >> u48)) ^ x2
        tmp = x1
        x1 = x3
        x3 = tmp
        # --- round 9 (rot 52/57) ---
        x0 = x0 + x1
        x1 = ((x1 << u52) | (x1 >> u12)) ^ x0
        x2 = x2 + x3
        x3 = ((x3 << u57) | (x3 >> u7)) ^ x2
        tmp = x1
        x1 = x3
        x3 = tmp
        # --- round 10 (rot 23/40) ---
        x0 = x0 + x1
        x1 = ((x1 << u23) | (x1 >> u41)) ^ x0
        x2 = x2 + x3
        x3 = ((x3 << u40) | (x3 >> u24)) ^ x2
        tmp = x1
        x1 = x3
        x3 = tmp
        # --- round 11 (rot 5/37) ---
        x0 = x0 + x1
        x1 = ((x1 << u5) | (x1 >> u59)) ^ x0
        x2 = x2 + x3
        x3 = ((x3 << u37) | (x3 >> u27)) ^ x2
        tmp = x1
        x1 = x3
        x3 = tmp
        x1 = x1 + parity   # k[4] @ s=3, word 1
        x3 = x3 + u_s3
        # --- round 12 (rot 25/33) ---
        x0 = x0 + x1
        x1 = ((x1 << u25) | (x1 >> u39)) ^ x0
        x2 = x2 + x3
        x3 = ((x3 << u33) | (x3 >> u31)) ^ x2
        tmp = x1
        x1 = x3
        x3 = tmp
        # --- round 13 (rot 46/12) ---
        x0 = x0 + x1
        x1 = ((x1 << u46) | (x1 >> u18)) ^ x0
        x2 = x2 + x3
        x3 = ((x3 << u12) | (x3 >> u52)) ^ x2
        tmp = x1
        x1 = x3
        x3 = tmp
        # --- round 14 (rot 58/22) ---
        x0 = x0 + x1
        x1 = ((x1 << u58) | (x1 >> u6)) ^ x0
        x2 = x2 + x3
        x3 = ((x3 << u22) | (x3 >> u42)) ^ x2
        tmp = x1
        x1 = x3
        x3 = tmp
        # --- round 15 (rot 32/32) ---
        x0 = x0 + x1
        x1 = ((x1 << u32) | (x1 >> u32)) ^ x0
        x2 = x2 + x3
        x3 = ((x3 << u32) | (x3 >> u32)) ^ x2
        tmp = x1
        x1 = x3
        x3 = tmp
        x0 = x0 + parity   # k[4] @ s=4, word 0
        x3 = x3 + u_s4
        # --- round 16 (rot 14/16) ---
        x0 = x0 + x1
        x1 = ((x1 << u14) | (x1 >> u50)) ^ x0
        x2 = x2 + x3
        x3 = ((x3 << u16) | (x3 >> u48)) ^ x2
        tmp = x1
        x1 = x3
        x3 = tmp
        # --- round 17 (rot 52/57) ---
        x0 = x0 + x1
        x1 = ((x1 << u52) | (x1 >> u12)) ^ x0
        x2 = x2 + x3
        x3 = ((x3 << u57) | (x3 >> u7)) ^ x2
        tmp = x1
        x1 = x3
        x3 = tmp
        # --- round 18 (rot 23/40) ---
        x0 = x0 + x1
        x1 = ((x1 << u23) | (x1 >> u41)) ^ x0
        x2 = x2 + x3
        x3 = ((x3 << u40) | (x3 >> u24)) ^ x2
        tmp = x1
        x1 = x3
        x3 = tmp
        # --- round 19 (rot 5/37) ---
        x0 = x0 + x1
        x1 = ((x1 << u5) | (x1 >> u59)) ^ x0
        x2 = x2 + x3
        x3 = ((x3 << u37) | (x3 >> u27)) ^ x2
        tmp = x1
        x1 = x3
        x3 = tmp
        x3 = x3 + u_s5
        base = b * 4
        out[base] = np.float64(x0 >> shift) * scale
        out[base + 1] = np.float64(x1 >> shift) * scale
        out[base + 2] = np.float64(x2 >> shift) * scale
        out[base + 3] = np.float64(x3 >> shift) * scale


if _HAVE_NUMBA:
    _fill_doubles_kernel = njit(cache=True, fastmath=False)(_fill_doubles_kernel)


_EMPTY_F64: np.ndarray = np.empty(0, dtype=np.float64)  # shared immutable-by-convention empty reservoir

class ThreefryGenerator(DoublesStreamGenerator):
    """Deterministic Threefry-4x64-20 stream reproducing the reference RNG.

    ``random``/``integers``/``permutation``/``choice`` come from the shared
    :class:`DoublesStreamGenerator` base; only the counter-based ``_draw`` and the
    state snapshot are Threefry-specific.
    """

    def __init__(self, seed: int) -> None:
        """Seed the counter from an integer seed (low 32 bits, per reference)."""
        s = int(seed) & 0xFFFFFFFF
        self._c0 = (((s + 1) << 32) | s) & 0xFFFFFFFFFFFFFFFF
        self._c1 = (((s + 3) << 32) | (s + 2)) & 0xFFFFFFFFFFFFFFFF
        self._c2 = (((s + 5) << 32) | (s + 4)) & 0xFFFFFFFFFFFFFFFF
        self._c3 = (((s + 7) << 32) | (s + 6)) & 0xFFFFFFFFFFFFFFFF
        self._next_block = 0
        # Index-based reservoir (P3-RNG, 2026-07-25). Previously a shrinking
        # ndarray that was re-sliced on EVERY draw -- `self._buffer =
        # self._buffer[take:]` allocates a fresh view object per call, which
        # profiling attributed 47% of atmals-gsk runtime to (scalar draws
        # dominate its local search). Now a fixed array plus an integer cursor:
        # no per-call allocation, and refills amortise the JIT call over
        # _REFILL_BLOCKS blocks instead of one.
        #
        # BIT-IDENTICAL by construction: `_fill_doubles_kernel` maps block index
        # k -> a fixed quadruple of doubles, independent of how many blocks are
        # requested per call. Generating _REFILL_BLOCKS blocks at once therefore
        # yields exactly the sequence that generating them one at a time yields;
        # only the buffering schedule changes, never a value or its position.
        self._buf: np.ndarray = np.empty(0, dtype=np.float64)
        self._pos = 0

    #: Blocks (4 doubles each) generated per refill. Amortises the njit call and
    #: the Python-level call overhead across many scalar draws. Kept modest so
    #: ``copy_state`` snapshots stay small (it serialises the unconsumed tail).
    _REFILL_BLOCKS = 256

    def _generate(self, n_blocks: int) -> np.ndarray:
        """Return ``4*n_blocks`` fresh doubles and advance the block counter."""
        block: np.ndarray = np.empty(n_blocks * 4, dtype=np.float64)
        # Pass the counter words as uint64 so Numba boxes them as uint64 (not
        # int64); c1..c3 can exceed int64 max for seeds near MAX_SAFE_SEED.
        _fill_doubles_kernel(
            np.uint64(self._c0),
            np.uint64(self._c1),
            np.uint64(self._c2),
            np.uint64(self._c3),
            self._next_block,
            n_blocks,
            block,
        )
        self._next_block += n_blocks
        return block

    def random_scalar(self) -> float:
        """Return the next double. Fast path for scalar ``random()``.

        Avoids the ``np.empty(1)`` allocation and the array round trip that
        ``float(self._draw(1)[0])`` pays. Consumes exactly one double from the
        same stream position, so it is interchangeable with ``_draw(1)``.
        """
        if self._pos >= self._buf.size:
            self._buf = self._generate(self._REFILL_BLOCKS)
            self._pos = 0
        value = self._buf[self._pos]
        self._pos += 1
        return float(value)

    def peek_doubles(self, count: int) -> np.ndarray:
        """Return the next ``count`` doubles WITHOUT consuming them.

        Pairs with :meth:`skip_doubles` so a caller can vectorize a draw whose
        consumption is data-dependent (a bounded-rejection loop): peek a chunk,
        use as many as the loop actually needs, then skip exactly that many. The
        values are the doubles successive ``random_scalar`` calls would return,
        in the same order, so any result computed from them is bit-identical to
        the scalar path.

        Materializing future blocks into the reservoir is stream-neutral: only
        the boundary between "buffered" and "not yet computed" moves, never the
        sequence itself, and ``copy_state`` snapshots the unconsumed tail.
        Added for the vendored external baselines; no family optimizer calls it.
        """
        if count <= 0:
            return np.empty(0, dtype=np.float64)
        avail = self._buf.size - self._pos
        if avail < count:
            tail = self._buf[self._pos:].copy()
            need = count - tail.size
            n_blocks = max((need + 3) // 4, self._REFILL_BLOCKS)
            self._buf = np.concatenate([tail, self._generate(n_blocks)])
            self._pos = 0
        return self._buf[self._pos:self._pos + count]

    def skip_doubles(self, count: int) -> None:
        """Consume ``count`` doubles previously exposed by :meth:`peek_doubles`."""
        if count <= 0:
            return
        if self._buf.size - self._pos < count:
            raise ValueError(
                f"skip_doubles({count}) exceeds the {self._buf.size - self._pos} "
                f"doubles currently buffered; call peek_doubles first."
            )
        self._pos += count

    def _draw(self, count: int) -> np.ndarray:
        """Return ``count`` consecutive doubles, buffering partial blocks."""
        if count <= 0:
            return np.empty(0, dtype=np.float64)
        avail = self._buf.size - self._pos
        # Fully served from the reservoir: one slice, no generation.
        if count <= avail:
            out = self._buf[self._pos:self._pos + count].copy()
            self._pos += count
            return out
        out = np.empty(count, dtype=np.float64)
        filled = 0
        if avail:
            out[:avail] = self._buf[self._pos:]
            self._pos = self._buf.size
            filled = avail
        need = count - filled
        # W1.1 direct fill (2026-07-25): full blocks are generated straight into
        # `out`, eliminating the intermediate `block` allocation plus the
        # full-size memcpy `out[filled:] = block[:need]` that every large draw
        # paid (microbenched: 56% of draw cost at >=300k doubles). Only the
        # final PARTIAL block (need % 4 doubles) goes through a 4-double temp,
        # whose unconsumed tail becomes the new reservoir.
        #
        # Bit-identical BY CONSTRUCTION: _fill_doubles_kernel maps block index
        # k to a fixed quadruple of doubles independent of the destination
        # buffer, so the same values land at the same logical stream positions;
        # _next_block advances by full_blocks + (1 if rem else 0)
        # == (need + 3) // 4, exactly as before; and the unconsumed reservoir
        # tail after the call holds the identical doubles the old
        # `block[need:]` held (the last block's last 4-rem values), so
        # copy_state() snapshots are unchanged byte-for-byte.
        full_blocks = need // 4
        rem = need - full_blocks * 4
        if full_blocks:
            _fill_doubles_kernel(
                np.uint64(self._c0),
                np.uint64(self._c1),
                np.uint64(self._c2),
                np.uint64(self._c3),
                self._next_block,
                full_blocks,
                out[filled:filled + full_blocks * 4],
            )
            self._next_block += full_blocks
            filled += full_blocks * 4
        if rem:
            tail = self._generate(1)
            out[filled:] = tail[:rem]
            self._buf = tail
            self._pos = rem
        else:
            self._buf = _EMPTY_F64
            self._pos = 0
        return out

    def copy_state(self) -> dict[str, Any]:
        """Return a deep-copyable snapshot of the generator state."""
        return {
            "kind": "threefry4x64_20",
            "counter": [int(self._c0), int(self._c1), int(self._c2), int(self._c3)],
            "next_block": int(self._next_block),
            # Serialise only the UNCONSUMED tail, preserving the original
            # snapshot schema: the reservoir is an internal buffering detail, so
            # a snapshot must describe the stream position, not the cursor.
            "buffer": self._buf[self._pos:].tolist(),
        }

    def restore_state(self, state: dict[str, Any]) -> None:
        """Restore a previously captured generator state."""
        snapshot = copy.deepcopy(state)
        counter = snapshot["counter"]
        self._c0, self._c1, self._c2, self._c3 = (int(v) for v in counter)
        self._next_block = int(snapshot["next_block"])
        self._buf = np.asarray(snapshot["buffer"], dtype=np.float64)
        self._pos = 0
