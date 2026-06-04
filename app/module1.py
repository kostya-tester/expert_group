# -*- coding: utf-8 -*-
"""
Модуль 1. Справочник дефектов ВИК.
Кнопка «Критические поверхностные дефекты отсутствуют» → переход на Модуль 2.
"""
import tkinter as tk
from tkinter import ttk

from app.styles import (
    BG_MAIN, BG_CARD, BG_PANEL, ACCENT, ACCENT_LIGHT, ACCENT_DARK,
    TEXT_MAIN, TEXT_SEC, TEXT_MUTED, BORDER,
    WARN, WARN_LIGHT, OK, OK_LIGHT, FONT_FAMILY
)
from app.widgets import (
    ScrollableFrame, DefectCard, DefectDetailPanel,
    SectionHeader, Divider, InfoBox, TagBadge, WarnBadge
)
from app.data import VIK_DEFECTS


class Module1(ttk.Frame):
    def __init__(self, parent, base_dir: str, on_go_module2=None, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self._base_dir = base_dir
        self._on_go_module2 = on_go_module2
        self._build()

    def _build(self):
        # ── Заголовок ───────────────────────────────────────────────────────
        hdr = ttk.Frame(self, style="TFrame")
        hdr.pack(fill="x", padx=24, pady=(18, 4))
        ttk.Label(hdr, text="Модуль 1", style="Muted.TLabel").pack(anchor="w")
        ttk.Label(hdr, text="Справочник дефектов визуально-измерительного контроля",
                  style="H1.TLabel").pack(anchor="w")

        InfoBox(
            self,
            "ВИК выполняется первым и является обязательным методом контроля. "
            "Ознакомьтесь с перечнем характерных дефектов и особенностей поверхности "
            "углепластиковых деталей, изготовленных методом вакуумной инфузии. "
            "Нажмите на карточку для просмотра подробной информации.",
            kind="info"
        ).pack(fill="x", padx=24, pady=(4, 8))

        # ── Кнопка перехода ─────────────────────────────────────────────────
        btn_bar = tk.Frame(self, bg=OK_LIGHT,
                           highlightthickness=1, highlightbackground=OK)
        btn_bar.pack(fill="x", padx=24, pady=(0, 10))

        tk.Label(btn_bar,
                 text="После завершения визуального осмотра:",
                 bg=OK_LIGHT, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 11),
                 padx=14, pady=8).pack(side="left")

        go_btn = tk.Button(
            btn_bar,
            text="✔  Критические поверхностные дефекты отсутствуют  →  перейти к выбору метода НК",
            bg=ACCENT, fg="#FFFFFF",
            font=(FONT_FAMILY, 11, "bold"),
            relief="flat", bd=0,
            padx=16, pady=8,
            cursor="hand2",
            activebackground=ACCENT_DARK,
            activeforeground="#FFFFFF",
            command=self._go_module2
        )
        go_btn.pack(side="left", padx=(0, 14), pady=8)

        # ── Сплит-вью ───────────────────────────────────────────────────────
        paned = tk.PanedWindow(self, orient="horizontal",
                               bg=BG_MAIN, sashwidth=6,
                               sashrelief="flat", bd=0, sashpad=2)
        paned.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        left = ttk.Frame(paned, style="TFrame")
        paned.add(left, minsize=320)

        right = tk.Frame(paned, bg=BG_CARD, bd=1, relief="solid",
                         highlightthickness=1, highlightbackground=BORDER)
        paned.add(right, minsize=340)

        self._detail = DefectDetailPanel(right, self._base_dir)
        self._detail.pack(fill="both", expand=True)

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

    def _go_module2(self):
        if self._on_go_module2:
            self._on_go_module2()
