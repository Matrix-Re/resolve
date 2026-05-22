import ipaddress
import json
import re
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from core.constants import JSON_EXTENSION
from core.constants import DEFAULT_ZONES_DIR

DEFAULT_ZONES_PATH = Path(DEFAULT_ZONES_DIR)
DOMAIN_REGEX = re.compile(r"^[a-z0-9-]+(\.[a-z0-9-]+)+$")


class ZoneEditor(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("ReSolve - DNS Zone Editor")
        self.geometry("1050x620")
        self.minsize(950, 560)

        self.zones_path = DEFAULT_ZONES_PATH
        self.current_zone_path: Path | None = None
        self.current_zone: dict | None = None
        self.selected_record: tuple[str, str] | None = None

        self.configure_style()
        self.create_widgets()
        self.load_zone_list()

    def configure_style(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")

        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Subtitle.TLabel", font=("Segoe UI", 10))
        style.configure("Section.TLabelframe.Label", font=("Segoe UI", 10, "bold"))
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"))

    def create_widgets(self) -> None:
        main_frame = ttk.Frame(self, padding=14)
        main_frame.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(main_frame)
        header.pack(fill=tk.X, pady=(0, 12))

        ttk.Label(
            header,
            text="ReSolve - DNS Zone Editor",
            style="Title.TLabel",
        ).pack(anchor="w")

        ttk.Label(
            header,
            text="Créer, modifier et supprimer les zones DNS JSON du projet.",
            style="Subtitle.TLabel",
        ).pack(anchor="w")

        content = ttk.Frame(main_frame)
        content.pack(fill=tk.BOTH, expand=True)

        self.create_zone_panel(content)
        self.create_record_panel(content)

    def create_zone_panel(self, parent: ttk.Frame) -> None:
        panel = ttk.LabelFrame(
            parent,
            text="Zones DNS",
            padding=12,
            style="Section.TLabelframe",
        )
        panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 12))

        ttk.Label(panel, text="Nouvelle zone").pack(anchor="w")

        self.new_zone_entry = ttk.Entry(panel, width=32)
        self.new_zone_entry.pack(fill=tk.X, pady=(4, 6))
        self.new_zone_entry.insert(0, "google.com")

        ttk.Button(
            panel,
            text="Créer la zone",
            command=self.create_zone,
            style="Primary.TButton",
        ).pack(fill=tk.X, pady=(0, 10))

        ttk.Separator(panel).pack(fill=tk.X, pady=8)

        ttk.Label(panel, text="Zones disponibles").pack(anchor="w")

        self.zone_listbox = tk.Listbox(
            panel,
            width=34,
            height=20,
            activestyle="dotbox",
        )
        self.zone_listbox.pack(fill=tk.BOTH, expand=True, pady=(4, 8))
        self.zone_listbox.bind("<<ListboxSelect>>", self.on_zone_selected)

        ttk.Button(
            panel,
            text="Recharger",
            command=self.load_zone_list,
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            panel,
            text="Supprimer la zone sélectionnée",
            command=self.delete_zone,
        ).pack(fill=tk.X, pady=2)

    def create_record_panel(self, parent: ttk.Frame) -> None:
        panel = ttk.Frame(parent)
        panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.zone_title_label = ttk.Label(
            panel,
            text="Aucune zone sélectionnée",
            style="Title.TLabel",
        )
        self.zone_title_label.pack(anchor="w")

        self.zone_path_label = ttk.Label(panel, text="")
        self.zone_path_label.pack(anchor="w", pady=(0, 10))

        columns = ("domain", "record_type", "value", "ttl")
        self.records_tree = ttk.Treeview(
            panel,
            columns=columns,
            show="headings",
            height=14,
        )

        self.records_tree.heading("domain", text="Domaine")
        self.records_tree.heading("record_type", text="Type")
        self.records_tree.heading("value", text="Valeur")
        self.records_tree.heading("ttl", text="TTL")

        self.records_tree.column("domain", width=260)
        self.records_tree.column("record_type", width=90, anchor="center")
        self.records_tree.column("value", width=260)
        self.records_tree.column("ttl", width=90, anchor="center")

        self.records_tree.pack(fill=tk.BOTH, expand=True)
        self.records_tree.bind("<<TreeviewSelect>>", self.on_record_selected)

        form = ttk.LabelFrame(
            panel,
            text="Édition d’un enregistrement",
            padding=12,
            style="Section.TLabelframe",
        )
        form.pack(fill=tk.X, pady=(12, 0))

        ttk.Label(form, text="Sous-domaine").grid(row=0, column=0, sticky="w")
        ttk.Label(form, text="Type").grid(row=0, column=1, sticky="w")
        ttk.Label(form, text="Valeur IP").grid(row=0, column=2, sticky="w")
        ttk.Label(form, text="TTL").grid(row=0, column=3, sticky="w")

        self.subdomain_entry = ttk.Entry(form, width=28)
        self.subdomain_entry.grid(row=1, column=0, padx=(0, 8), sticky="ew")

        self.record_type_combo = ttk.Combobox(
            form,
            values=["A", "AAAA"],
            width=8,
            state="readonly",
        )
        self.record_type_combo.grid(row=1, column=1, padx=(0, 8))
        self.record_type_combo.set("A")

        self.value_entry = ttk.Entry(form, width=32)
        self.value_entry.grid(row=1, column=2, padx=(0, 8), sticky="ew")

        self.ttl_entry = ttk.Entry(form, width=10)
        self.ttl_entry.grid(row=1, column=3, sticky="ew")
        self.ttl_entry.insert(0, "300")

        form.columnconfigure(0, weight=1)
        form.columnconfigure(2, weight=1)

        help_text = (
            "Sous-domaine vide = domaine racine de la zone. "
            "Exemple : vide + google.com → google.com ; maps + google.com → maps.google.com"
        )
        ttk.Label(form, text=help_text).grid(
            row=2,
            column=0,
            columnspan=4,
            sticky="w",
            pady=(8, 0),
        )

        buttons = ttk.Frame(panel)
        buttons.pack(fill=tk.X, pady=10)

        ttk.Button(
            buttons,
            text="Ajouter",
            command=self.add_record,
            style="Primary.TButton",
        ).pack(side=tk.LEFT, padx=(0, 6))

        ttk.Button(
            buttons,
            text="Modifier sélection",
            command=self.update_record,
        ).pack(side=tk.LEFT, padx=6)

        ttk.Button(
            buttons,
            text="Supprimer record",
            command=self.delete_record,
        ).pack(side=tk.LEFT, padx=6)

        ttk.Button(
            buttons,
            text="Vider formulaire",
            command=self.clear_form,
        ).pack(side=tk.LEFT, padx=6)

        ttk.Button(
            buttons,
            text="Sauvegarder",
            command=self.save_zone,
            style="Primary.TButton",
        ).pack(side=tk.RIGHT)

    def load_zone_list(self) -> None:
        self.zones_path.mkdir(parents=True, exist_ok=True)

        self.zone_listbox.delete(0, tk.END)

        for zone_file in sorted(self.zones_path.glob(f"*{JSON_EXTENSION}")):
            self.zone_listbox.insert(tk.END, zone_file.name)

    def create_zone(self) -> None:
        zone_name = self.normalize_zone_name(self.new_zone_entry.get())

        if not self.is_valid_domain(zone_name):
            messagebox.showerror(
                "Erreur",
                "Format invalide. Exemple attendu : google.com",
            )
            return

        zone_path = self.zones_path / f"{zone_name}{JSON_EXTENSION}"

        if zone_path.exists():
            messagebox.showerror(
                "Erreur",
                f"La zone {zone_name} existe déjà.",
            )
            return

        zone_content = {"records": {}}

        zone_path.write_text(
            json.dumps(zone_content, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        self.load_zone_list()
        messagebox.showinfo("Succès", f"Zone créée : {zone_name}")

    def delete_zone(self) -> None:
        selection = self.zone_listbox.curselection()

        if not selection:
            return

        zone_name = self.zone_listbox.get(selection[0])
        zone_path = self.zones_path / zone_name

        if zone_path.exists():
            zone_path.unlink()

        self.current_zone_path = None
        self.current_zone = None
        self.selected_record = None
        self.zone_title_label.config(text="Aucune zone sélectionnée")
        self.zone_path_label.config(text="")
        self.clear_records_table()
        self.clear_form()
        self.load_zone_list()

    def on_zone_selected(self, event) -> None:
        selection = self.zone_listbox.curselection()

        if not selection:
            return

        zone_name = self.zone_listbox.get(selection[0])
        self.load_zone(self.zones_path / zone_name)

    def load_zone(self, zone_path: Path) -> None:
        try:
            zone = json.loads(zone_path.read_text(encoding="utf-8"))

            if not isinstance(zone, dict):
                raise ValueError("La zone doit être un objet JSON.")

            if "records" not in zone:
                raise ValueError("Champ obligatoire manquant : records.")

            if not isinstance(zone["records"], dict):
                raise ValueError("Le champ records doit être un objet.")

            self.current_zone_path = zone_path
            self.current_zone = zone
            self.selected_record = None

            zone_domain = self.get_zone_domain()
            self.zone_title_label.config(text=f"Zone : {zone_domain}")
            self.zone_path_label.config(text=str(zone_path))

            self.refresh_records()
            self.clear_form()

        except Exception as error:
            messagebox.showerror("Erreur", str(error))

    def refresh_records(self) -> None:
        self.clear_records_table()

        if self.current_zone is None:
            return

        records = self.current_zone.get("records", {})

        for domain, record_types in sorted(records.items()):
            for record_type, record_data in sorted(record_types.items()):
                self.records_tree.insert(
                    "",
                    tk.END,
                    values=(
                        domain,
                        record_type,
                        record_data.get("value", ""),
                        record_data.get("ttl", ""),
                    ),
                )

    def clear_records_table(self) -> None:
        for item in self.records_tree.get_children():
            self.records_tree.delete(item)

    def on_record_selected(self, event) -> None:
        selection = self.records_tree.selection()

        if not selection:
            return

        domain, record_type, value, ttl = self.records_tree.item(
            selection[0],
            "values",
        )

        self.selected_record = (domain, record_type)

        zone_domain = self.get_zone_domain()
        subdomain = self.extract_subdomain(domain, zone_domain)

        self.subdomain_entry.delete(0, tk.END)
        self.subdomain_entry.insert(0, subdomain)

        self.record_type_combo.set(record_type)

        self.value_entry.delete(0, tk.END)
        self.value_entry.insert(0, value)

        self.ttl_entry.delete(0, tk.END)
        self.ttl_entry.insert(0, str(ttl))

    def add_record(self) -> None:
        if self.current_zone is None:
            messagebox.showwarning("Attention", "Aucune zone sélectionnée.")
            return

        full_domain, record_type, value, ttl = self.read_form()

        if full_domain is None:
            return

        records = self.current_zone.setdefault("records", {})
        domain_records = records.setdefault(full_domain, {})

        if record_type in domain_records:
            messagebox.showerror(
                "Erreur",
                f"L’enregistrement {record_type} existe déjà pour {full_domain}.",
            )
            return

        domain_records[record_type] = {
            "value": value,
            "ttl": ttl,
        }

        self.refresh_records()
        self.clear_form()

    def update_record(self) -> None:
        if self.current_zone is None:
            messagebox.showwarning("Attention", "Aucune zone sélectionnée.")
            return

        if self.selected_record is None:
            messagebox.showwarning("Attention", "Aucun record sélectionné.")
            return

        old_domain, old_record_type = self.selected_record
        full_domain, record_type, value, ttl = self.read_form()

        if full_domain is None:
            return

        records = self.current_zone.setdefault("records", {})

        if (
            (full_domain, record_type) != self.selected_record
            and full_domain in records
            and record_type in records[full_domain]
        ):
            messagebox.showerror(
                "Erreur",
                f"L’enregistrement {record_type} existe déjà pour {full_domain}.",
            )
            return

        if old_domain in records and old_record_type in records[old_domain]:
            del records[old_domain][old_record_type]

            if not records[old_domain]:
                del records[old_domain]

        records.setdefault(full_domain, {})[record_type] = {
            "value": value,
            "ttl": ttl,
        }

        self.selected_record = None
        self.refresh_records()
        self.clear_form()

    def delete_record(self) -> None:
        if self.current_zone is None or self.selected_record is None:
            return

        domain, record_type = self.selected_record
        records = self.current_zone.get("records", {})

        if domain in records and record_type in records[domain]:
            del records[domain][record_type]

            if not records[domain]:
                del records[domain]

        self.selected_record = None
        self.refresh_records()
        self.clear_form()

    def save_zone(self) -> None:
        if self.current_zone_path is None or self.current_zone is None:
            messagebox.showwarning("Attention", "Aucune zone sélectionnée.")
            return

        self.current_zone_path.write_text(
            json.dumps(self.current_zone, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        messagebox.showinfo("Succès", "Zone sauvegardée.")

    def read_form(self) -> tuple[str | None, str, str, int]:
        zone_domain = self.get_zone_domain()

        subdomain = self.subdomain_entry.get().strip().lower().removesuffix(".")
        record_type = self.record_type_combo.get().strip().upper()
        value = self.value_entry.get().strip()
        ttl_text = self.ttl_entry.get().strip()

        if not value:
            messagebox.showerror("Erreur", "La valeur IP est obligatoire.")
            return None, record_type, value, 0

        if record_type not in {"A", "AAAA"}:
            messagebox.showerror("Erreur", "Le type doit être A ou AAAA.")
            return None, record_type, value, 0

        try:
            ttl = int(ttl_text)
        except ValueError:
            messagebox.showerror("Erreur", "Le TTL doit être un entier.")
            return None, record_type, value, 0

        if ttl <= 0:
            messagebox.showerror("Erreur", "Le TTL doit être supérieur à 0.")
            return None, record_type, value, 0

        full_domain = self.build_full_domain(subdomain, zone_domain)

        if not self.is_valid_domain(full_domain):
            messagebox.showerror(
                "Erreur",
                f"Domaine invalide : {full_domain}",
            )
            return None, record_type, value, ttl

        if not self.is_valid_ip_for_record_type(value, record_type):
            messagebox.showerror(
                "Erreur",
                f"La valeur ne correspond pas au type {record_type}.",
            )
            return None, record_type, value, ttl

        return full_domain, record_type, value, ttl

    def build_full_domain(self, subdomain: str, zone_domain: str) -> str:
        if not subdomain:
            return zone_domain

        return f"{subdomain}.{zone_domain}"

    def extract_subdomain(self, full_domain: str, zone_domain: str) -> str:
        if full_domain == zone_domain:
            return ""

        suffix = f".{zone_domain}"

        if full_domain.endswith(suffix):
            return full_domain.removesuffix(suffix)

        return full_domain

    def get_zone_domain(self) -> str:
        if self.current_zone_path is None:
            return ""

        return self.current_zone_path.name.removesuffix(JSON_EXTENSION)

    def clear_form(self) -> None:
        self.selected_record = None

        self.subdomain_entry.delete(0, tk.END)
        self.value_entry.delete(0, tk.END)

        self.ttl_entry.delete(0, tk.END)
        self.ttl_entry.insert(0, "300")

        self.record_type_combo.set("A")

    def normalize_zone_name(self, value: str) -> str:
        value = value.strip().lower().removesuffix(".")

        if value.endswith(JSON_EXTENSION):
            value = value.removesuffix(JSON_EXTENSION)

        return value

    def is_valid_domain(self, value: str) -> bool:
        return bool(DOMAIN_REGEX.match(value))

    def is_valid_ip_for_record_type(self, value: str, record_type: str) -> bool:
        try:
            ip = ipaddress.ip_address(value)
        except ValueError:
            return False

        if record_type == "A":
            return ip.version == 4

        if record_type == "AAAA":
            return ip.version == 6

        return False


def main() -> None:
    app = ZoneEditor()
    app.mainloop()


if __name__ == "__main__":
    main()
