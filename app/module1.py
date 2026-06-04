# -*- coding: utf-8 -*-
"""
Модуль 1. Справочник дефектов ВИК.
"""
import tkinter as tk
from tkinter import ttk

from app.styles import (
    BG_MAIN, BG_CARD, BG_PANEL, ACCENT, ACCENT_LIGHT,
    TEXT_MAIN, TEXT_SEC, TEXT_MUTED, BORDER,
    WARN, WARN_LIGHT, FONT_FAMILY
)
from app.widgets import (
    ScrollableFrame, DefectCard, DefectDetailPanel,
    SectionHeader, Divider, InfoBox, TagBadge, WarnBadge
)
from app.data import VIK_DEFECTS


class Module1(ttk.Frame):
    def __init__(self, parent, base_dir: str, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self._base_dir = base_dir
        self._build()

    def _build(self):
        # Заголовок
        hdr = ttk.Frame(self, style="TFrame")
        hdr.pack(fill="x", padx=24, pady=(18, 4))
        ttk.Label(hdr, text="Модуль 1", style="Muted.TLabel").pack(anchor="w")
        ttk.Label(hdr, text="Справочник дефектов визуально-измерительного контроля",
                  style="H1.TLabel").pack(anchor="w")

        info = InfoBox(
            self,
            "ВИК выполняется первым и является обязательным методом контроля. "
            "Ознакомьтесь с перечнем характерных дефектов и особенностей поверхности "
            "углепластиковых деталей, изготовленных методом вакуумной инфузии. "
            "Нажмите на карточку для просмотра подробной информации.",
            kind="info"
        )
        info.pack(fill="x", padx=24, pady=(4, 10))

        # Сплит-вью
        paned = tk.PanedWindow(self, orient="horizontal",
                               bg=BG_MAIN, sashwidth=6,
                               sashrelief="flat", bd=0,
                               sashpad=2)
        paned.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Левая: список карточек
        left = ttk.Frame(paned, style="TFrame")
        paned.add(left, minsize=320)

        # Правая: детальная панель
        right = tk.Frame(paned, bg=BG_CARD, bd=1, relief="solid",
                         highlightthickness=1, highlightbackground=BORDER)
        paned.add(right, minsize=340)

        self._detail = DefectDetailPanel(right, self._base_dir)
        self._detail.pack(fill="both", expand=True)

        # Заголовок левой панели
        ttk.Label(left, text="Дефекты и особенности поверхности",
                  style="H3.TLabel",
                  background=BG_PANEL).pack(fill="x", padx=8, pady=(4, 4))

        scroll = ScrollableFrame(left, bg=BG_MAIN)
        scroll.pack(fill="both", expand=True)
        inner = scroll.inner

        groups = {}
        for d in VIK_DEFECTS:
            g = d.get("group", "Прочие")
            groups.setdefault(g, []).append(d)

        for grp_name, defects in groups.items():
            # Заголовок группы
            g_frame = tk.Frame(inner, bg=BG_PANEL)
            g_frame.pack(fill="x", pady=(6, 2))
            tk.Label(g_frame, text=grp_name.upper(),
                     bg=BG_PANEL, fg=TEXT_SEC,
                     font=(FONT_FAMILY, 9, "bold"),
                     padx=12, pady=4).pack(anchor="w")

            for d in defects:
                card = DefectCard(
                    inner, d, self._base_dir,
                    on_click=self._detail.show,
                    compact=True
                )
                card.pack(fill="x", padx=6, pady=3)
