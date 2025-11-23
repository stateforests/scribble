import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Dict, Any, Callable, Optional

from src.api import API
from src.utils import parse_time, get_category, center_window, validate_run

GAME_ID = "nd27np51" # color book
PLATFORM_ID = "8gej2n93" # pc

CATEGORIES = {
    "Solo": None, 
    "Duo": None, 
    "Trio": None,
    "Quartet": None,
    "Squad": None
}
VARIABLES = {
    'variable_id': 'onv520ml', # gears?
    'options': {
        'Gearless': 'q757r8p1',
        'Gear': '1gnx2m6l'
    }
}

TEXT_WIDGET_STYLE = {
    'font': ('Segoe UI', 9),
    'insertwidth': 1,
    'relief': 'sunken',
    'borderwidth': 1,
    'highlightthickness': 0
}

class Login:
    def __init__(self, parent, on_login: Callable):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Speedrun.com authentication")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        self.on_login = on_login
        
        self._setup_ui()
        center_window(self.dialog)
        
    def _setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="Username:").grid(row=0, column=0, sticky="e", pady=6, padx=(0, 8))
        self.username_entry = ttk.Entry(frame, width=20)
        self.username_entry.grid(row=0, column=1, pady=6, sticky="w")
        self.username_entry.focus()
        
        ttk.Label(frame, text="Password:").grid(row=1, column=0, sticky="e", pady=6, padx=(0, 8))
        self.password_entry = ttk.Entry(frame, show="*", width=20)
        self.password_entry.grid(row=1, column=1, pady=6, sticky="w")
        
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(button_frame, text="Login", command=self._do_login, width=10).pack(side="left", padx=4)
        ttk.Button(button_frame, text="Cancel", command=self.dialog.destroy, width=10).pack(side="left", padx=4)
        
        self.password_entry.bind('<Return>', lambda e: self._do_login())
        self.username_entry.bind('<Return>', lambda e: self.password_entry.focus())
        
    def _do_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not username or not password:
            messagebox.showerror("Error", "You gotta put your details in for the thing to work bro.", parent=self.dialog)
            return
        
        self.on_login(username, password, self.dialog)
    
    def withdraw(self):
        self.dialog.withdraw()
        
    def deiconify(self):
        self.dialog.deiconify()
        
    def destroy(self):
        self.dialog.destroy()


class TwoFactor:
    def __init__(self, parent):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("2FA Required")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.resizable(False, False)
        
        self.result = {'token': None}
        
        self._setup_ui()
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (300 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (160 // 2)
        self.dialog.geometry(f"300x160+{x}+{y}")
        
    def _setup_ui(self):
        frame = ttk.Frame(self.dialog, padding="20")
        frame.pack(fill="both", expand=True)
        
        ttk.Label(frame, text="You have 2FA on your account.\nPlease enter your 2FA token:").pack(pady=(0, 15))
        
        self.token_var = tk.StringVar()
        self.token_entry = ttk.Entry(frame, textvariable=self.token_var, width=20, justify="center")
        self.token_entry.pack(pady=(0, 15))
        self.token_entry.focus()
        
        button_frame = ttk.Frame(frame)
        button_frame.pack()
        ttk.Button(button_frame, text="Submit", command=self._on_submit, width=10).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel, width=10).pack(side="left", padx=5)
        
        self.token_entry.bind('<Return>', lambda e: self._on_submit())
        
    def _on_submit(self):
        self.result['token'] = self.token_var.get().strip()
        self.dialog.destroy()
        
    def _on_cancel(self):
        self.dialog.destroy()
        
    def show(self) -> Optional[str]:
        self.dialog.wait_window()
        return self.result['token']


class Window:
    def __init__(self, root):
        self.root = root
        self.root.title("Scribble")
        self.root.geometry("800x520")
        self.root.resizable(False, False)
        
        self.api = API(GAME_ID)
        self.runs_list = []
        self.categories = CATEGORIES.copy()
        self.levels = {}
        self.variables = VARIABLES.copy()
        
        self._setup_ui()
        self.root.after(100, self._fetch_game_data)
        
    def _setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="12")
        main_frame.pack(fill="both", expand=True)
        
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill="both", expand=True)
        
        self._create_left_panel(content_frame)
        self._create_right_panel(content_frame)
        self._create_auth_panel(main_frame)
        
    def _create_left_panel(self, parent):
        left_frame = ttk.LabelFrame(parent, text="Add Run", padding="12")
        left_frame.pack(side="left", fill="both", expand=False, padx=(0, 8))
        
        fields = [
            ("Category:", "category"),
            ("Map:", "map"),
            ("Gear:", "gear"),
            ("Players:", "players"),
            ("Time:", "time"),
            ("Video URL:", "video"),
        ]
        
        for idx, (label, field) in enumerate(fields):
            ttk.Label(left_frame, text=label, width=10, anchor="w").grid(
                row=idx, column=0, sticky="w", pady=3, padx=(0, 8))
            
            widget = self._create_field_widget(left_frame, field)
            widget.grid(row=idx, column=1, sticky="ew", pady=3)
        
        ttk.Label(left_frame, text="Description:", width=10, anchor="nw").grid(
            row=6, column=0, sticky="nw", pady=3, padx=(0, 8))
        self.description_text = self._create_text_widget(left_frame, height=10, width=25)
        self.description_text.grid(row=6, column=1, sticky="ew", pady=3)
        
        btn_frame = ttk.Frame(left_frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=(10, 0))
        ttk.Button(btn_frame, text="Add Run", command=self._add_run, width=13).pack(side="left", padx=2)
        ttk.Button(btn_frame, text="Import Text", command=self._import_text, width=13).pack(side="left", padx=2)
        
        left_frame.columnconfigure(1, weight=1)
        
    def _create_field_widget(self, parent, field: str):
        if field == "category":
            self.category_var = tk.StringVar()
            widget = ttk.Combobox(parent, textvariable=self.category_var,
                values=list(self.categories.keys()), state="readonly", width=25)
            self.category_combo = widget
        elif field == "map":
            self.level_var = tk.StringVar()
            widget = ttk.Combobox(parent, textvariable=self.level_var, state="readonly", width=25)
            self.level_combo = widget
        elif field == "gear":
            self.variable_var = tk.StringVar()
            widget = ttk.Combobox(parent, textvariable=self.variable_var, state="readonly", width=25)
            self.variable_combo = widget
        elif field == "players":
            widget = self._create_text_widget(parent, height=3, width=25)
            self.players_entry = widget
        else:
            widget = ttk.Entry(parent, width=25)
            if field == "time":
                self.time_entry = widget
            elif field == "video":
                self.video_entry = widget
        
        return widget
    
    def _create_text_widget(self, parent, height: int, width: int):
        return tk.Text(parent, height=height, width=width, wrap="word", **TEXT_WIDGET_STYLE)
        
    def _create_right_panel(self, parent):
        right_frame = ttk.LabelFrame(parent, text="Runs to Submit (0)", padding="10")
        right_frame.pack(side="right", fill="both", expand=True)
        self.queue_label = right_frame
        
        columns = ("Category", "Map", "Gear", "Players", "Time")
        self.runs_tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=15)
        
        column_widths = {"Category": 70, "Map": 90, "Gear": 60, "Players": 100, "Time": 60}
        for col in columns:
            self.runs_tree.heading(col, text=col)
            self.runs_tree.column(col, width=column_widths[col], stretch=True)
        
        self.runs_tree.pack(fill="both", expand=True, pady=(0, 8))
        
        action_frame = ttk.Frame(right_frame)
        action_frame.pack(fill="x")
        ttk.Button(action_frame, text="Remove Selected", command=self._remove_run, width=16).pack(side="left", padx=2)
        self.submit_btn = ttk.Button(action_frame, text="Submit All Runs",
            command=self._submit_all_runs, state="disabled", width=16)
        self.submit_btn.pack(side="left", padx=2)
        
    def _create_auth_panel(self, parent):
        auth_frame = ttk.Frame(parent)
        auth_frame.pack(fill="x", pady=(10, 0))
        ttk.Button(auth_frame, text="Authenticate", command=self._show_login_dialog, width=13).pack(side="left")
        self.login_status = ttk.Label(auth_frame, text="Not logged in", foreground="red")
        self.login_status.pack(side="left", padx=10)
        
    def _show_login_dialog(self):
        Login(self.root, self._handle_login)
        
    def _handle_login(self, username: str, password: str, dialog):
        result = self.api.login(username, password)
        
        if result.tokenChallengeSent:
            dialog.withdraw()
            token = TwoFactor(self.root).show()
            
            if not token:
                dialog.destroy()
                return
            
            result = self.api.login(username, password, token)
            
            if not result.loggedIn:
                dialog.deiconify()
                messagebox.showerror("Error", "Invalid 2FA token, did you make a typo?", parent=dialog.dialog)
                return
        elif not result.loggedIn:
            messagebox.showerror("Error", "Login failed, probably mistyped your password?", parent=dialog.dialog)
            return
        
        self.api.get_csrf_token()
        self.login_status.config(text=f"Logged in as {username}", foreground="green")
        self.submit_btn.config(state="normal")
        dialog.destroy()
        messagebox.showinfo("Success", "Logged in successfully!")
            
    def _fetch_game_data(self):
        try:
            game_response = self.api.fetch_game_data()
            
            if 'categories' in game_response:
                for category in game_response['categories']:
                    if category.get('name') in self.categories:
                        self.categories[category['name']] = category['id']
            
            if 'levels' in game_response:
                for level in game_response['levels']:
                    self.levels[level['name']] = level['id']
                self.level_combo['values'] = list(self.levels.keys())
            
            self.variable_combo['values'] = list(self.variables['options'].keys())
        except:
            messagebox.showerror("Error", "Failed to fetch game data")
            
    def _add_run(self):
        category = self.category_var.get()
        level = self.level_var.get()
        variable = self.variable_var.get()
        players = self.players_entry.get("1.0", "end-1c").strip()
        time = self.time_entry.get().strip()
        video = self.video_entry.get().strip()
        description = self.description_text.get("1.0", "end-1c").strip()
        
        if not all([category, level, players, time, video]):
            messagebox.showwarning("Warning", "Please fill in all required fields")
            return
        
        run_data = self._build_run_data(category, level, variable, players, time, video, description)
        
        self.runs_list.append(run_data)
        self.runs_tree.insert('', 'end', values=(category, level, variable, players, time))
        self._update_run_counter()
        
        if len(self.runs_list) > 0:
            self.submit_btn.config(state="normal")
        
        self._clear_form()
        
    def _build_run_data(self, category: str, level: str, variable: str, players: str, 
                        time: str, video: str, description: str) -> Dict[str, Any]:
        return {
            'category': category,
            'category_id': self.categories.get(category),
            'level': level,
            'level_id': self.levels.get(level),
            'variable': variable,
            'variable_id': self.variables.get('variable_id') if variable else None,
            'variable_value_id': self.variables.get('options', {}).get(variable) if variable else None,
            'players': players,
            'time': time,
            'video': video,
            'description': description
        }
        
    def _clear_form(self):
        self.players_entry.delete("1.0", "end")
        self.time_entry.delete(0, 'end')
        self.video_entry.delete(0, 'end')
        self.description_text.delete("1.0", "end")
        
    def _remove_run(self):
        selected = self.runs_tree.selection()
        if selected:
            item = selected[0]
            index = self.runs_tree.index(item)
            self.runs_tree.delete(item)
            del self.runs_list[index]
            self._update_run_counter()
            
            if len(self.runs_list) == 0:
                self.submit_btn.config(state="disabled")
                
    def _update_run_counter(self):
        count = len(self.runs_list)
        self.queue_label.config(text=f"Runs to Submit ({count})")
        
    def _import_text(self):
        filepath = filedialog.askopenfilename(
            title="Select text file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not filepath:
            return
        
        try:
            with open(filepath, 'r') as f:
                content = f.read()
            
            lines = content.strip().split('\n')
            imported = 0
            errors = []
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                
                try:
                    run_data = self._parse_import_line(line)
                    if not run_data:
                        errors.append(f"Line {line_num}: Invalid format.")
                        continue
                    
                    error = validate_run(run_data, self.levels, self.variables)
                    if error:
                        errors.append(f"Line {line_num}: {error}")
                        continue
                    
                    self._import_run_data(run_data)
                    imported += 1
                    
                except Exception as e:
                    errors.append(f"Line {line_num}: {str(e)}")
                    continue
            
            self._show_import_results(imported, errors)
                
        except Exception as e:
            messagebox.showerror("Error", f"Text import failed: {str(e)}")
            
    def _parse_import_line(self, line: str) -> Optional[Dict[str, str]]:
        parts = [p.strip() for p in line.split('|')]
        
        if len(parts) < 5:
            return None
        
        return {
            'players': parts[0],
            'map': parts[1],
            'time': parts[2],
            'variable': parts[3],
            'video': parts[4],
            'description': parts[5] if len(parts) > 5 else '',
            'category': get_category(parts[0])
        }
        
    def _show_import_results(self, imported: int, errors: list):
        if errors:
            error_msg = f"Imported {imported} run(s) with {len(errors)} error(s):\n\n" + "\n".join(errors[:10])
            if len(errors) > 10:
                error_msg += f"\n\n...and {len(errors) - 10} more errors"
            messagebox.showwarning("Import Complete (with errors)", error_msg)
        else:
            messagebox.showinfo("Success", f"Imported {imported} run(s)")
            
    def _import_run_data(self, run_data: Dict[str, Any]):
        category = run_data.get('category', '')
        level = run_data.get('map', '')
        variable = run_data.get('variable', '')
        players = run_data.get('players', '')
        time = run_data.get('time', '')
        video = run_data.get('video', '')
        description = run_data.get('description', '')
        
        if not all([category, level, players, time]):
            return
        
        run = self._build_run_data(category, level, variable, players, time, video, description)
        
        self.runs_list.append(run)
        self.runs_tree.insert('', 'end', values=(category, level, variable, players, time, video))
        
    def _submit_all_runs(self):
        if not self.runs_list:
            messagebox.showwarning("Warning", "There's no runs to submit.")
            return
        
        if not self.api.csrf_token:
            messagebox.showerror("Error", "You're not logged in.")
            return
        
        successful = 0
        failed = 0
        
        for run in self.runs_list:
            try:
                time_obj = parse_time(run['time'])
                self.api.submit_run(run, time_obj)
                successful += 1
            except:
                failed += 1
        
        self._show_submission_results(successful, failed)
        
    def _show_submission_results(self, successful: int, failed: int):
        message = f"Submission complete! (s: {successful}/f: {failed})"
        if failed == 0:
            messagebox.showinfo("Success", message)
            self.runs_list.clear()
            for item in self.runs_tree.get_children():
                self.runs_tree.delete(item)
            self._update_run_counter()
        else:
            messagebox.showwarning("Success (some failed)", message)