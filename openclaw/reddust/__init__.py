"""Red Dust (SHELTER axis) readable-task runtime: world state, tools, grader.

This is the execution + scoring layer for the §7 readable-by-design tasks in
``tasks/rd_*``.  A task supplies static ``inputs/``, a ``tools.py`` that mutates
a :class:`~openclaw.reddust.world.World`, and a ``verifier/verify.py`` that turns
``success_checks`` into runnable :class:`~openclaw.reddust.checks.Check` objects.
"""
