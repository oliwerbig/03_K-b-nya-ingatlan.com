# -*- coding: utf-8 -*-
"""
report_engine — IFK-TDK 2026 Automatizált Területi Riport Generátor Csomag
"""

from .full_analyzer import FullAreaAnalyzer as AreaAnalyzer
from .full_narrative import FullNarrativeGenerator as NarrativeGenerator
from .full_html_builder import FullHTMLReportBuilder as HTMLReportBuilder

__all__ = ["AreaAnalyzer", "NarrativeGenerator", "HTMLReportBuilder"]
