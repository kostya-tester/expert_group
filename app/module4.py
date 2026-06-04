# -*- coding: utf-8 -*-
"""
Модуль 4. Интерактивный справочник дефектов.
Может показывать только дефекты, выявляемые выбранными методами.
"""
import tkinter as tk
from tkinter import ttk

from app.styles import (
    BG_MAIN, BG_CARD, BG_PANEL, ACCENT, ACCENT_LIGHT, ACCENT_DARK,
    TEXT_MAIN, TEXT_SEC, TEXT_MUTED, BORDER, INFO_LIGHT, FONT_FAMILY
)
from app.widgets import (
    ScrollableFrame, DefectCard, DefectDetailPanel,
    Divider, InfoBox, TagBadge
)
from app.data import ALL_DEFECTS, NK_METHODS


class Module4(ttk.Frame):
    def __init__(self, parent, base_dir: str, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self._base_dir  = base_dir
        self._filter_group  = tk.StringVar(value="Все")
        self._filter_method = tk.StringVar(value="Все")
        self._search_var    = tk.StringVar()
        self._cards = []

        # Список методов, установленных из модуля 3 (пусто = все)
        self._active_methods: list[str] = []

        self._build()
        self._search_var.trace_add("write",    self._apply_filter)
        self._filter_group.trace_add("write",  self._apply_filter)
        self._filter_method.trace_add("write", self._apply_filter)

    # ── Публичный метод: установить фильтр из модуля 3 ───────────────────
    def set_methods_filter(self, methods: list[str]):
        """Показывать только дефекты этих методов. [] = показать все."""
        self._active_methods = methods
        self._apply_filter()
        # Обновить информационную строку
        if methods:
            names = " + ".join(NK_METHODS[m]["full_name"] for m in methods if m in NK_METHODS)
            self._method_info_lbl.config(
                text=f"Показаны дефекты для методов:  {names}",
                fg=ACCENT
            )
        else:
            self._method_info_lbl.config(
                text="Показаны все дефекты  (фильтр по методам не задан)",
                fg=TEXT_MUTED
            )

    # ── Построение интерфейса ─────────────────────────────────────────────
    def _build(self):
        hdr = ttk.Frame(self, style="TFrame")
        hdr.pack(fill="x", padx=24, pady=(18, 4))
        ttk.Label(hdr, text="Модуль 4", style="Muted.TLabel").pack(anchor="w")
        ttk.Label(hdr, text="Справочник выявляемых дефектов",
                  style="H1.TLabel").pack(anchor="w")

        InfoBox(
            self,
            "Интерактивный справочник дефектов углепластиковых деталей. "
            "Нажмите на карточку для просмотра фотографий, причин возникновения "
            "и применяемых методов обнаружения.",
            kind="info"
        ).pack(fill="x", padx=24, pady=(4, 4))

        # Строка активных методов (из модуля 3)
        self._method_info_lbl = tk.Label(
            self,
            text="Показаны все дефекты  (фильтр по методам не задан)",
            bg=BG_MAIN, fg=TEXT_MUTED,
            font=(FONT_FAMILY, 10, "italic"),
            anchor="w"
        )
        self._method_info_lbl.pack(fill="x", padx=24, pady=(0, 6))

        # ── Фильтры ──────────────────────────────────────────────────────
        filter_bar = tk.Frame(self, bg=BG_PANEL)
        filter_bar.pack(fill="x", padx=12, pady=(0, 8))

        tk.Label(filter_bar, text="Поиск:", bg=BG_PANEL, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 11)).pack(side="left", padx=(10, 4), pady=6)
        tk.Entry(filter_bar, textvariable=self._search_var,
                 bg=BG_CARD, fg=TEXT_MAIN, font=(FONT_FAMILY, 11),
                 bd=1, relief="solid", width=22).pack(side="left", pady=6)

        tk.Label(filter_bar, text="  Группа:", bg=BG_PANEL, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 11)).pack(side="left", padx=(12, 4))
        groups = ["Все"] + sorted({d["group"] for d in ALL_DEFECTS})
        ttk.Combobox(filter_bar, textvariable=self._filter_group,
                     values=groups, state="readonly", width=22,
                     font=(FONT_FAMILY, 10)).pack(side="left")

        tk.Label(filter_bar, text="  Метод НК:", bg=BG_PANEL, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 11)).pack(side="left", padx=(12, 4))
        all_methods_set = set()
        for d in ALL_DEFECTS:
            for m in d["methods_detecting"]:
                all_methods_set.add(m.split(" (")[0])
        method_list = ["Все"] + sorted(all_methods_set)
        ttk.Combobox(filter_bar, textvariable=self._filter_method,
                     values=method_list, state="readonly", width=18,
                     font=(FONT_FAMILY, 10)).pack(side="left")

        tk.Button(filter_bar, text="Сбросить",
                  bg=BG_CARD, fg=TEXT_SEC,
                  font=(FONT_FAMILY, 10),
                  relief="flat", bd=1, cursor="hand2",
                  command=self._reset_filter).pack(side="left", padx=10)

        self._count_lbl = tk.Label(filter_bar, text="",
                                   bg=BG_PANEL, fg=TEXT_MUTED,
                                   font=(FONT_FAMILY, 10, "italic"))
        self._count_lbl.pack(side="right", padx=12)

        # ── Сплит-вью ────────────────────────────────────────────────────
        paned = tk.PanedWindow(self, orient="horizontal",
                               bg=BG_MAIN, sashwidth=6,
                               sashrelief="flat", bd=0, sashpad=2)
        paned.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        left = tk.Frame(paned, bg=BG_MAIN)
        paned.add(left, minsize=380)
        self._scroll = ScrollableFrame(left, bg=BG_MAIN)
        self._scroll.pack(fill="both", expand=True)
        self._cards_inner = self._scroll.inner

        right = tk.Frame(paned, bg=BG_CARD, bd=1, relief="solid",
                         highlightthickness=1, highlightbackground=BORDER)
        paned.add(right, minsize=360)
        self._detail = DefectDetailPanel(right, self._base_dir)
        self._detail.pack(fill="both", expand=True)

        self._render_cards(ALL_DEFECTS)

    # ── Рендер карточек ──────────────────────────────────────────────────
    def _render_cards(self, defects):
        for w in self._cards_inner.winfo_children():
            w.destroy()
        self._cards.clear()

        if not defects:
            tk.Label(self._cards_inner,
                     text="Нет дефектов, соответствующих фильтру.",
                     bg=BG_MAIN, fg=TEXT_MUTED,
                     font=(FONT_FAMILY, 12, "italic")).pack(pady=40)
            self._count_lbl.config(text="Найдено: 0")
            return

        self._count_lbl.config(text=f"Найдено: {len(defects)}")

        groups = {}
        for d in defects:
            groups.setdefault(d["group"], []).append(d)

        for grp_name, grp_defects in groups.items():
            g_hdr = tk.Frame(self._cards_inner, bg=BG_PANEL)
            g_hdr.pack(fill="x", pady=(8, 2))
            tk.Label(g_hdr, text=grp_name.upper(),
                     bg=BG_PANEL, fg=TEXT_SEC,
                     font=(FONT_FAMILY, 9, "bold"),
                     padx=10, pady=4).pack(side="left")
            tk.Label(g_hdr, text=f"({len(grp_defects)})",
                     bg=BG_PANEL, fg=TEXT_MUTED,
                     font=(FONT_FAMILY, 9)).pack(side="left")

            row_frame = None
            for i, d in enumerate(grp_defects):
                if i % 2 == 0:
                    row_frame = tk.Frame(self._cards_inner, bg=BG_MAIN)
                    row_frame.pack(fill="x", padx=4, pady=3)
                card = DefectCard(row_frame, d, self._base_dir,
                                  on_click=self._detail.show, compact=False)
                card.pack(side="left", fill="both", expand=True, padx=3)
                self._cards.append(card)

    # ── Фильтрация ───────────────────────────────────────────────────────
    def _apply_filter(self, *args):
        query  = self._search_var.get().strip().lower()
        grp    = self._filter_group.get()
        method = self._filter_method.get()

        result = []
        for d in ALL_DEFECTS:
            # Фильтр по активным методам (из модуля 3)
            if self._active_methods:
                found = False
                for am in self._active_methods:
                    if any(am.lower() in m.lower() for m in d["methods_detecting"]):
                        found = True
                        break
                if not found:
                    continue

            if grp != "Все" and d["group"] != grp:
                continue
            if method != "Все":
                if not any(method.lower() in m.lower() for m in d["methods_detecting"]):
                    continue
            if query:
                haystack = (d["name"] + " " + d.get("short", "") + " " +
                            d.get("description", "")).lower()
                if query not in haystack:
                    continue
            result.append(d)

        self._render_cards(result)

    def _reset_filter(self):
        self._search_var.set("")
        self._filter_group.set("Все")
        self._filter_method.set("Все")
        self._active_methods = []
        self._method_info_lbl.config(
            text="Показаны все дефекты  (фильтр по методам не задан)",
            fg=TEXT_MUTED
        )
