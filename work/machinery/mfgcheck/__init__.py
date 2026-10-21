# SPDX-License-Identifier: MIT
# Copyright (c) 3000 galion-studio
"""mfgcheck: a small, cited manufacturability checker for simple car parts.

Every rule carries a source id (see ``mfgcheck.data.SOURCES``) that resolves to a
URL. The checker flags rule breaches and suggests the nearest manufacturable
value. It does not predict fracture; it applies published design rules.
"""
from .checks import Finding, check_part, flc0_keeler, flc_major_limit

__all__ = ["Finding", "check_part", "flc0_keeler", "flc_major_limit"]
__version__ = "0.1.0"
