# -*- coding: utf-8 -*-
"""
Вспомогательные виджеты многократного использования.
"""
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from app.styles import (
    BG_CARD, BG_MAIN, BG_PANEL, ACCENT, ACCENT_LIGHT,
    TEXT_MAIN, TEXT_SEC, TEXT_MUTED, BORDER, SEP_COLOR,
    WARN, WARN_LIGHT, OK, OK_LIGHT, INFO, INFO_LIGHT,
    FONT_FAMILY
)


def get_image_path(img_name: str, base_dir: str) -> str | None:
    if not img_name:
        return None
    path = os.path.join(base_dir, "assets", "images", img_name)
    return path if os.path.exists(path) else None


def load_tk_image(path: str, max_w: int = 300, max_h: int = 220) -> ImageTk.PhotoImage | None:
    if not path or not os.path.exists(path):
        return None
    try:
        img = Image.open(path)
        img.thumbnail((max_w, max_h), Image.LANCZOS)
        return ImageTk.PhotoImage(img)
    except Exception:
        return None


class ScrollableFrame(ttk.Frame):
    """Прокручиваемый фрейм."""

    def __init__(self, parent, bg=BG_MAIN, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(style="TFrame")

        canvas = tk.Canvas(self, bg=bg, highlightthickness=0, borderwidth=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.inner = ttk.Frame(canvas, style="TFrame")

        self.inner.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        self._canvas_window = canvas.create_window((0, 0), window=self.inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        canvas.bind("<Configure>", self._on_canvas_resize)
        self.inner.bind("<Enter>", lambda e: self._bind_scroll(canvas))
        self.inner.bind("<Leave>", lambda e: self._unbind_scroll(canvas))
        self._canvas = canvas

    def _on_canvas_resize(self, event):
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    def _bind_scroll(self, canvas):
        canvas.bind_all("<MouseWheel>",   lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))
        canvas.bind_all("<Button-4>",     lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind_all("<Button-5>",     lambda e: canvas.yview_scroll(1, "units"))

    def _unbind_scroll(self, canvas):
        canvas.unbind_all("<MouseWheel>")
        canvas.unbind_all("<Button-4>")
        canvas.unbind_all("<Button-5>")


class SectionHeader(ttk.Label):
    def __init__(self, parent, text, **kwargs):
        super().__init__(parent, text=text, style="H2.TLabel", **kwargs)


class Divider(ttk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, height=1, style="TFrame", **kwargs)
        self.configure(style="TFrame")
        inner = tk.Frame(self, bg=SEP_COLOR, height=1)
        inner.pack(fill="x", padx=0, pady=0)


class TagBadge(tk.Label):
    """Небольшой цветной ярлык-бейдж."""
    def __init__(self, parent, text, color=ACCENT, bg_color=ACCENT_LIGHT, **kwargs):
        super().__init__(
            parent, text=text,
            fg=color, bg=bg_color,
            font=(FONT_FAMILY, 9, "bold"),
            padx=6, pady=2,
            relief="flat",
            **kwargs
        )


class WarnBadge(TagBadge):
    def __init__(self, parent, text="Критический дефект", **kwargs):
        super().__init__(parent, text=text, color=WARN, bg_color=WARN_LIGHT, **kwargs)


class InfoBox(tk.Frame):
    """Блок с цветным фоном для информационного сообщения."""
    def __init__(self, parent, text, kind="info", **kwargs):
        colors = {
            "info":  (INFO_LIGHT,  INFO),
            "warn":  (WARN_LIGHT,  WARN),
            "ok":    (OK_LIGHT,    OK),
            "plain": (BG_PANEL,    TEXT_MAIN),
        }
        bg, fg = colors.get(kind, colors["plain"])
        super().__init__(parent, bg=bg, bd=0, relief="flat", padx=10, pady=8, **kwargs)
        tk.Label(
            self, text=text,
            bg=bg, fg=fg,
            font=(FONT_FAMILY, 11),
            wraplength=600, justify="left",
            anchor="w"
        ).pack(fill="x")


class DefectCard(tk.Frame):
    """
    Карточка дефекта: фото + название + краткое описание.
    Нажатие вызывает callback(defect_data).
    """
    def __init__(self, parent, defect: dict, base_dir: str,
                 on_click=None, compact=False, **kwargs):
        super().__init__(
            parent, bg=BG_CARD,
            bd=1, relief="solid",
            highlightthickness=1,
            highlightbackground=BORDER,
            **kwargs
        )
        self._defect = defect
        self._on_click = on_click
        self._hover_bg = ACCENT_LIGHT
        self._normal_bg = BG_CARD

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._click)

        img_key = defect.get("images", [defect.get("image")])
        if isinstance(img_key, str):
            img_key = [img_key]
        img_path = None
        for k in img_key:
            p = get_image_path(k, base_dir)
            if p:
                img_path = p
                break

        if compact:
            self._build_compact(defect, img_path, base_dir)
        else:
            self._build_full(defect, img_path, base_dir)

    def _build_full(self, defect, img_path, base_dir):
        # Изображение
        photo = load_tk_image(img_path, 200, 150)
        if photo:
            lbl_img = tk.Label(self, image=photo, bg=BG_CARD, cursor="hand2")
            lbl_img.image = photo
            lbl_img.pack(padx=10, pady=(10, 4))
            lbl_img.bind("<Button-1>", self._click)
            self._propagate_bind(lbl_img)
        else:
            placeholder = tk.Label(
                self, text="[нет фото]",
                bg="#EEEBE4", fg=TEXT_MUTED,
                font=(FONT_FAMILY, 10, "italic"),
                width=20, height=6
            )
            placeholder.pack(padx=10, pady=(10, 4))
            self._propagate_bind(placeholder)

        # Бейджи группы / критичности
        row_badges = tk.Frame(self, bg=BG_CARD)
        row_badges.pack(fill="x", padx=10)
        TagBadge(row_badges, defect.get("group", ""), bg_color="#EBE8E1", color=TEXT_SEC).pack(side="left")
        if defect.get("is_critical"):
            WarnBadge(row_badges).pack(side="left", padx=(4, 0))
        self._propagate_bind(row_badges)

        # Название
        lbl_name = tk.Label(
            self, text=defect["name"],
            bg=BG_CARD, fg=TEXT_MAIN,
            font=(FONT_FAMILY, 11, "bold"),
            wraplength=180, justify="left",
            cursor="hand2", anchor="w"
        )
        lbl_name.pack(fill="x", padx=10, pady=(4, 2))
        lbl_name.bind("<Button-1>", self._click)
        self._propagate_bind(lbl_name)

        # Короткое описание
        lbl_short = tk.Label(
            self, text=defect.get("short", ""),
            bg=BG_CARD, fg=TEXT_SEC,
            font=(FONT_FAMILY, 10),
            wraplength=180, justify="left",
            anchor="w"
        )
        lbl_short.pack(fill="x", padx=10, pady=(0, 10))
        lbl_short.bind("<Button-1>", self._click)
        self._propagate_bind(lbl_short)

    def _build_compact(self, defect, img_path, base_dir):
        """Горизонтальная компактная карточка."""
        photo = load_tk_image(img_path, 80, 60)
        left = tk.Frame(self, bg=BG_CARD, width=90)
        left.pack(side="left", fill="y", padx=(8, 0), pady=8)
        left.pack_propagate(False)
        if photo:
            lbl_img = tk.Label(left, image=photo, bg=BG_CARD, cursor="hand2")
            lbl_img.image = photo
            lbl_img.pack(expand=True)
            lbl_img.bind("<Button-1>", self._click)
            self._propagate_bind(lbl_img)
        else:
            tk.Label(left, text="[нет фото]", bg="#EEEBE4", fg=TEXT_MUTED,
                     font=(FONT_FAMILY, 8, "italic")).pack(expand=True)

        right = tk.Frame(self, bg=BG_CARD)
        right.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        tk.Label(right, text=defect["name"],
                 bg=BG_CARD, fg=TEXT_MAIN,
                 font=(FONT_FAMILY, 11, "bold"),
                 anchor="w", justify="left").pack(fill="x")
        tk.Label(right, text=defect.get("short", ""),
                 bg=BG_CARD, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 10),
                 wraplength=300, anchor="w", justify="left").pack(fill="x")
        self._propagate_bind(right)

    def _propagate_bind(self, widget):
        widget.bind("<Enter>", self._on_enter)
        widget.bind("<Leave>", self._on_leave)
        if self._on_click:
            widget.bind("<Button-1>", self._click)

    def _on_enter(self, e=None):
        self._set_bg(ACCENT_LIGHT)
        self.configure(highlightbackground=ACCENT, cursor="hand2")

    def _on_leave(self, e=None):
        self._set_bg(BG_CARD)
        self.configure(highlightbackground=BORDER, cursor="")

    def _set_bg(self, color):
        for w in self.winfo_children():
            try:
                w.configure(bg=color)
            except Exception:
                pass
            for child in w.winfo_children():
                try:
                    child.configure(bg=color)
                except Exception:
                    pass
        try:
            self.configure(bg=color)
        except Exception:
            pass

    def _click(self, e=None):
        if self._on_click:
            self._on_click(self._defect)


class DefectDetailPanel(tk.Frame):
    """Панель подробного просмотра дефекта (правая часть сплит-вью)."""

    def __init__(self, parent, base_dir: str, **kwargs):
        super().__init__(parent, bg=BG_CARD, bd=0, **kwargs)
        self._base_dir = base_dir
        self._photo_refs = []
        self._placeholder()

    def _placeholder(self):
        for w in self.winfo_children():
            w.destroy()
        self._photo_refs.clear()
        tk.Label(
            self,
            text="Выберите дефект из списка\nдля просмотра подробной информации",
            bg=BG_CARD, fg=TEXT_MUTED,
            font=(FONT_FAMILY, 12, "italic"),
            justify="center"
        ).place(relx=0.5, rely=0.5, anchor="center")

    def show(self, defect: dict):
        for w in self.winfo_children():
            w.destroy()
        self._photo_refs.clear()

        scroll = ScrollableFrame(self, bg=BG_CARD)
        scroll.pack(fill="both", expand=True)
        inner = scroll.inner

        # Заголовок + бейджи
        hdr = tk.Frame(inner, bg=BG_CARD)
        hdr.pack(fill="x", padx=16, pady=(14, 4))

        grp = defect.get("group") or defect.get("groups", [""])[0]
        TagBadge(hdr, grp, bg_color="#EBE8E1", color=TEXT_SEC).pack(side="left")
        if defect.get("is_critical"):
            WarnBadge(hdr).pack(side="left", padx=(6, 0))

        tk.Label(inner, text=defect["name"],
                 bg=BG_CARD, fg=TEXT_MAIN,
                 font=(FONT_FAMILY, 16, "bold"),
                 anchor="w", justify="left",
                 wraplength=440).pack(fill="x", padx=16, pady=(0, 8))

        Divider(inner).pack(fill="x", padx=16, pady=4)

        # Фотографии
        imgs = defect.get("images") or ([defect.get("image")] if defect.get("image") else [])
        photos_frame = tk.Frame(inner, bg=BG_CARD)
        photos_frame.pack(fill="x", padx=16, pady=(4, 8))
        for img_name in imgs:
            if not img_name:
                continue
            p = get_image_path(img_name, self._base_dir)
            photo = load_tk_image(p, 380, 260)
            if photo:
                self._photo_refs.append(photo)
                tk.Label(photos_frame, image=photo, bg=BG_CARD).pack(pady=4)

        # Описание
        self._section(inner, "Описание", defect.get("description", ""))

        # Причины
        causes = defect.get("causes", [])
        if causes:
            tk.Label(inner, text="Причины возникновения",
                     bg=BG_CARD, fg=TEXT_MAIN,
                     font=(FONT_FAMILY, 12, "bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(8, 2))
            for c in causes:
                row = tk.Frame(inner, bg=BG_CARD)
                row.pack(fill="x", padx=16, pady=1)
                tk.Label(row, text="•", bg=BG_CARD, fg=ACCENT,
                         font=(FONT_FAMILY, 12, "bold")).pack(side="left", anchor="n")
                tk.Label(row, text=c, bg=BG_CARD, fg=TEXT_SEC,
                         font=(FONT_FAMILY, 11),
                         wraplength=400, justify="left", anchor="w").pack(side="left", padx=(4, 0))

        # Выявляемые методы
        methods = defect.get("methods_detecting", [])
        if methods:
            tk.Label(inner, text="Методы обнаружения",
                     bg=BG_CARD, fg=TEXT_MAIN,
                     font=(FONT_FAMILY, 12, "bold"),
                     anchor="w").pack(fill="x", padx=16, pady=(10, 4))
            row_m = tk.Frame(inner, bg=BG_CARD)
            row_m.pack(fill="x", padx=16, pady=(0, 12))
            for m in methods:
                TagBadge(row_m, m, color=ACCENT, bg_color=ACCENT_LIGHT).pack(side="left", padx=(0, 4), pady=2)

    def _section(self, parent, title: str, text: str):
        if not text:
            return
        tk.Label(parent, text=title,
                 bg=BG_CARD, fg=TEXT_MAIN,
                 font=(FONT_FAMILY, 12, "bold"),
                 anchor="w").pack(fill="x", padx=16, pady=(8, 2))
        tk.Label(parent, text=text,
                 bg=BG_CARD, fg=TEXT_SEC,
                 font=(FONT_FAMILY, 11),
                 wraplength=440, justify="left", anchor="w").pack(fill="x", padx=16, pady=(0, 4))
