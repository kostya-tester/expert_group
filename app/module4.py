# -*- coding: utf-8 -*-
"""
Модуль 4. Интерактивный справочник выявляемых дефектов.
"""
import tkinter as tk
from tkinter import ttk

from app.styles import (
    BG_MAIN, BG_CARD, BG_PANEL, ACCENT, ACCENT_LIGHT,
    TEXT_MAIN, TEXT_SEC, TEXT_MUTED, BORDER, FONT_FAMILY
)
from app.widgets import (
    ScrollableFrame, DefectCard, DefectDetailPanel,
    SectionHeader, Divider, InfoBox, TagBadge
)
from app.data import ALL_DEFECTS


class Module4(ttk.Frame):
    def __init__(self, parent, base_dir: str, **kwargs):
        super().__init__(parent, style="TFrame", **kwargs)
        self._base_dir = base_dir
        self._filter_group = tk.StringVar(value="Все")
        self._filter_method = tk.StringVar(value="Все")
        self._search_var = tk.StringVar()
        self._cards = []
        self._build()
        self._search_var.trace_add("write", self._apply_filter)
        self._filter_group.trace_add("write", self._apply_filter)
        self._filter_method.trace_add("write", self._apply_filter)

    def _build(self):
        # Заголовок
        hdr = ttk.Frame(self, style="TFrame")
        hdr.pack(fill="x", padx=24, pady=(18, 4))
        ttk.Label(hdr, text="Модуль 4", style="Muted.TLabel").pack(anchor="w")
        ttk.Label(hdr, text="Справочник выявляемых дефектов",
                  style="H1.TLabel").pack(anchor="w")

        InfoBox(
            self,
            "Интерактивный справочник всех дефектов углепластиковых деталей, "
            "изготовленных методом вакуумной инфузии. "
            "Нажмите на карточку для просмотра фотографий, причин возникновения "
            "и характерных признаков при контроле.",
            kind="info"
        ).pack(fill="x", padx=24, pady=(4, 8))

        # Фильтры
        filter_bar = tk.Frame(self, bg=BG_PANEL, bd=0)
        filter_bar.pack(fill="x", padx=12, pady=(0, 8))

        # Поиск
        tk.Label(filter_bar, text="Поиск:", bg=BG_PANEL, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 11)).pack(side="left", padx=(10, 4), pady=6)
        search_entry = tk.Entry(filter_bar, textvariable=self._search_var,
                                bg=BG_CARD, fg=TEXT_MAIN,
                                font=(FONT_FAMILY, 11),
                                bd=1, relief="solid", width=24)
        search_entry.pack(side="left", pady=6)

        # Группа
        tk.Label(filter_bar, text="  Группа:", bg=BG_PANEL, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 11)).pack(side="left", padx=(12, 4))
        groups = ["Все"] + sorted({d["group"] for d in ALL_DEFECTS})
        grp_menu = ttk.Combobox(filter_bar, textvariable=self._filter_group,
                                values=groups, state="readonly", width=22,
                                font=(FONT_FAMILY, 10))
        grp_menu.pack(side="left")

        # Метод
        tk.Label(filter_bar, text="  Метод НК:", bg=BG_PANEL, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 11)).pack(side="left", padx=(12, 4))
        all_methods = set()
        for d in ALL_DEFECTS:
            for m in d["methods_detecting"]:
                # Берём только первое слово (метод без уточнений)
                all_methods.add(m.split(" (")[0].split()[0] if " " in m else m)
        method_list = ["Все"] + sorted(all_methods)
        met_menu = ttk.Combobox(filter_bar, textvariable=self._filter_method,
                                values=method_list, state="readonly", width=16,
                                font=(FONT_FAMILY, 10))
        met_menu.pack(side="left")

        # Кнопка сброса
        tk.Button(filter_bar, text="Сбросить",
                  bg=BG_CARD, fg=TEXT_SEC,
                  font=(FONT_FAMILY, 10),
                  relief="flat", bd=1,
                  cursor="hand2",
                  command=self._reset_filter).pack(side="left", padx=10)

        # Счётчик
        self._count_lbl = tk.Label(filter_bar, text="",
                                   bg=BG_PANEL, fg=TEXT_MUTED,
                                   font=(FONT_FAMILY, 10, "italic"))
        self._count_lbl.pack(side="right", padx=12)

        # Сплит-вью
        paned = tk.PanedWindow(self, orient="horizontal",
                               bg=BG_MAIN, sashwidth=6,
                               sashrelief="flat", bd=0, sashpad=2)
        paned.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        # Левая: сетка карточек
        left_container = tk.Frame(paned, bg=BG_MAIN, bd=0)
        paned.add(left_container, minsize=380)

        self._scroll = ScrollableFrame(left_container, bg=BG_MAIN)
        self._scroll.pack(fill="both", expand=True)
        self._cards_inner = self._scroll.inner

        # Правая: детальная панель
        right = tk.Frame(paned, bg=BG_CARD, bd=1, relief="solid",
                         highlightthickness=1, highlightbackground=BORDER)
        paned.add(right, minsize=360)

        self._detail = DefectDetailPanel(right, self._base_dir)
        self._detail.pack(fill="both", expand=True)

        self._render_cards(ALL_DEFECTS)

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

        # Группируем по группам
        groups = {}
        for d in defects:
            g = d["group"]
            groups.setdefault(g, []).append(d)

        for grp_name, grp_defects in groups.items():
            # Заголовок группы
            g_hdr = tk.Frame(self._cards_inner, bg=BG_PANEL)
            g_hdr.pack(fill="x", pady=(8, 2))
            tk.Label(g_hdr, text=grp_name.upper(),
                     bg=BG_PANEL, fg=TEXT_SEC,
                     font=(FONT_FAMILY, 9, "bold"),
                     padx=10, pady=4).pack(side="left")
            tk.Label(g_hdr, text=f"({len(grp_defects)})",
                     bg=BG_PANEL, fg=TEXT_MUTED,
                     font=(FONT_FAMILY, 9)).pack(side="left")

            # Карточки в 2 колонки
            row_frame = None
            for i, d in enumerate(grp_defects):
                if i % 2 == 0:
                    row_frame = tk.Frame(self._cards_inner, bg=BG_MAIN)
                    row_frame.pack(fill="x", padx=4, pady=3)

                card = DefectCard(
                    row_frame, d, self._base_dir,
                    on_click=self._detail.show,
                    compact=False
                )
                card.pack(side="left", fill="both", expand=True, padx=3)
                self._cards.append(card)

    def _apply_filter(self, *args):
        query = self._search_var.get().strip().lower()
        grp = self._filter_group.get()
        method = self._filter_method.get()

        result = []
        for d in ALL_DEFECTS:
            if grp != "Все" and d["group"] != grp:
                continue
            if method != "Все":
                # Проверяем, есть ли метод в любом из строк methods_detecting
                found = any(method.lower() in m.lower() for m in d["methods_detecting"])
                if not found:
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
