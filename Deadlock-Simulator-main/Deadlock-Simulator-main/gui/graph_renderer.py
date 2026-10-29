"""
Interactive Graph Renderer
──────────────────────────
Renders the Resource Allocation Graph (RAG) and Wait-For Graph (WFG)
with high-contrast cyber styling, zoom/pan controls, cycle path highlighting,
and anti-overlap circular layout.
"""

import math
import tkinter as tk
from typing import Dict, List, Optional, Tuple, Set
from gui.theme import (
    BG_BASE, BG_PANEL, BG_CARD, BG_INPUT, BORDER_DEFAULT, BORDER_FOCUS,
    CYAN, CYAN_DIM, PURPLE, SUCCESS, WARNING, DANGER,
    TEXT_PRIMARY, TEXT_SECONDARY, TEXT_MUTED, get_fonts
)


class GraphRenderer:
    """
    Renders high-definition interactive RAG/WFG graphs on a Tkinter Canvas.
    Supports viewport pan, zoom, fit-to-view, and deadlock cycle path glowing.
    """

    NODE_RADIUS = 30
    RESOURCE_WIDTH = 64
    RESOURCE_HEIGHT = 48

    def __init__(self, canvas: tk.Canvas):
        self.canvas = canvas
        self.fonts = get_fonts()
        
        # Viewport transform state
        self.zoom_scale = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        
        # Dragging state
        self._drag_start_x = 0
        self._drag_start_y = 0
        self._is_dragging = False

        # Node storage
        self._positions: Dict[str, Tuple[float, float]] = {}
        self._last_snapshot: dict = {}
        self._last_detection = None
        self._last_mode = "rag"

        self._bind_events()

    def _bind_events(self):
        """Bind mouse interactions for pan and zoom."""
        self.canvas.bind("<ButtonPress-1>", self._on_button_press)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_button_release)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Configure>", lambda e: self.render(self._last_snapshot, self._last_detection, self._last_mode))

    def _on_button_press(self, event):
        self._drag_start_x = event.x
        self._drag_start_y = event.y
        self._is_dragging = True

    def _on_mouse_drag(self, event):
        if self._is_dragging:
            dx = event.x - self._drag_start_x
            dy = event.y - self._drag_start_y
            self.pan_x += dx
            self.pan_y += dy
            self._drag_start_x = event.x
            self._drag_start_y = event.y
            self.render(self._last_snapshot, self._last_detection, self._last_mode)

    def _on_button_release(self, event):
        self._is_dragging = False

    def _on_mouse_wheel(self, event):
        """Zoom in or out centered at cursor position."""
        scale_factor = 1.1 if event.delta > 0 else 0.9
        self.zoom(scale_factor, event.x, event.y)

    def zoom(self, factor: float, center_x: float = None, center_y: float = None):
        """Applies zoom multiplier."""
        new_scale = max(0.4, min(3.0, self.zoom_scale * factor))
        if center_x is None or center_y is None:
            center_x = self.canvas.winfo_width() / 2
            center_y = self.canvas.winfo_height() / 2
            
        # Adjust pan so zoom centers around cursor
        self.pan_x = center_x - (center_x - self.pan_x) * (new_scale / self.zoom_scale)
        self.pan_y = center_y - (center_y - self.pan_y) * (new_scale / self.zoom_scale)
        self.zoom_scale = new_scale
        self.render(self._last_snapshot, self._last_detection, self._last_mode)

    def zoom_in(self):
        self.zoom(1.15)

    def zoom_out(self):
        self.zoom(0.85)

    def reset_view(self):
        """Reset pan and zoom to initial state."""
        self.zoom_scale = 1.0
        self.pan_x = 0.0
        self.pan_y = 0.0
        self.render(self._last_snapshot, self._last_detection, self._last_mode)

    # ── Render Pipeline ───────────────────────────────────────────────────────

    def render(self, snapshot: dict, detection_result=None, mode: str = "rag"):
        """Main rendering entry point."""
        self._last_snapshot = snapshot or {}
        self._last_detection = detection_result
        self._last_mode = mode

        self.canvas.delete("all")
        
        processes = self._last_snapshot.get("processes", {})
        resources = self._last_snapshot.get("resources", {})

        if not processes and not resources:
            self._draw_empty_state()
            self._draw_hud(mode)
            return

        # Extract deadlocked sets & cycle edges
        deadlocked_pids: Set[str] = set()
        deadlocked_rids: Set[str] = set()
        cycle_edges: Set[Tuple[str, str]] = set()

        if detection_result and detection_result.detected:
            deadlocked_pids = set(detection_result.deadlocked_processes)
            deadlocked_rids = set(detection_result.deadlocked_resources)
            # Parse cycle paths for exact edge highlighting
            for cpath in getattr(detection_result, "cycle_path", []):
                # e.g., 'P1 → [R1] → P2 → [R2] → P1' or 'P1 ⇒ P2 ⇒ P1'
                delims = [" → ", " ⇒ "]
                nodes = []
                for d in delims:
                    if d in cpath:
                        nodes = [n.strip("[]") for n in cpath.split(d)]
                        break
                if nodes:
                    for i in range(len(nodes) - 1):
                        cycle_edges.add((nodes[i], nodes[i+1]))

        # Compute layout positions
        base_positions = self._compute_layout(processes, resources)
        
        # Apply viewport transform (pan & zoom)
        transformed_positions = {}
        for nid, (bx, by) in base_positions.items():
            tx = bx * self.zoom_scale + self.pan_x
            ty = by * self.zoom_scale + self.pan_y
            transformed_positions[nid] = (tx, ty)
        self._positions = transformed_positions

        # Draw grid background dots for high-tech aesthetic
        self._draw_tech_grid()

        # 1. Draw Edges
        if mode == "wfg":
            self._draw_wfg_edges(processes, transformed_positions, cycle_edges)
        else:
            self._draw_rag_edges(processes, resources, transformed_positions, cycle_edges)

        # 2. Draw Resource Nodes (RAG mode only)
        if mode != "wfg":
            for rid, r in resources.items():
                if rid in transformed_positions:
                    rx, ry = transformed_positions[rid]
                    is_deadlocked = rid in deadlocked_rids or any(rid in c for c in getattr(detection_result, "cycle_path", []))
                    self._draw_resource_node(rid, r, rx, ry, is_deadlocked)

        # 3. Draw Process Nodes
        for pid, p in processes.items():
            if pid in transformed_positions:
                px, py = transformed_positions[pid]
                is_deadlocked = pid in deadlocked_pids
                self._draw_process_node(pid, p, px, py, is_deadlocked)

        # 4. Draw HUD controls & Legend
        self._draw_hud(mode)
        self._draw_legend(mode, detection_result)

    # ── Layout Calculations ───────────────────────────────────────────────────

    def _compute_layout(self, processes: dict, resources: dict) -> Dict[str, Tuple[float, float]]:
        """
        Computes 2-ring concentric circular layout:
        Processes on inner ring, Resources on outer ring.
        """
        w = max(600, self.canvas.winfo_width() or 700)
        h = max(400, self.canvas.winfo_height() or 500)
        cx, cy = w / 2, h / 2

        positions = {}
        pids = list(processes.keys())
        rids = list(resources.keys())

        r_inner = min(cx, cy) * 0.40
        r_outer = min(cx, cy) * 0.72

        # Distribute Processes
        num_p = max(len(pids), 1)
        for i, pid in enumerate(pids):
            angle = (2 * math.pi * i / num_p) - (math.pi / 2)
            positions[pid] = (cx + r_inner * math.cos(angle),
                              cy + r_inner * math.sin(angle))

        # Distribute Resources
        num_r = max(len(rids), 1)
        offset = math.pi / num_r if num_r > 0 else 0
        for i, rid in enumerate(rids):
            angle = (2 * math.pi * i / num_r) - (math.pi / 2) + offset
            positions[rid] = (cx + r_outer * math.cos(angle),
                              cy + r_outer * math.sin(angle))

        return positions

    # ── Background Tech Grid ──────────────────────────────────────────────────

    def _draw_tech_grid(self):
        """Draws subtle modern dot grid in the canvas background."""
        w = self.canvas.winfo_width() or 700
        h = self.canvas.winfo_height() or 500
        step = int(36 * self.zoom_scale)
        if step < 18:
            return

        ox = int(self.pan_x % step)
        oy = int(self.pan_y % step)

        for x in range(ox, w, step):
            for y in range(oy, h, step):
                self.canvas.create_rectangle(
                    x, y, x + 1, y + 1,
                    fill="#151E2B", outline=""
                )

    # ── Edge Drawing ──────────────────────────────────────────────────────────

    def _draw_rag_edges(self, processes: dict, resources: dict, pos: dict, cycle_edges: Set[Tuple[str, str]]):
        """Draws allocation and request edges in RAG mode."""
        for pid, p in processes.items():
            if pid not in pos:
                continue
            px, py = pos[pid]
            pname = p.get("name", pid)

            # 1. Request edges: Process -> Resource (wants)
            for rid, count in p.get("requested", {}).items():
                if rid in pos:
                    rx, ry = pos[rid]
                    rname = resources.get(rid, {}).get("name", rid)
                    is_cycle = (pid, rid) in cycle_edges or (pname, rname) in cycle_edges or (pid, f"[{rname}]") in cycle_edges
                    color = DANGER if is_cycle else WARNING
                    dash = None if is_cycle else (4, 3)
                    width = 3 if is_cycle else 2
                    self._draw_arrow(
                        px, py, rx, ry,
                        color=color,
                        dash=dash,
                        width=width,
                        start_radius=self.NODE_RADIUS * self.zoom_scale,
                        end_radius=(self.RESOURCE_WIDTH / 2) * self.zoom_scale,
                        label=f"{count}×" if count > 1 else ""
                    )

            # 2. Allocation edges: Resource -> Process (holds)
            for rid, count in p.get("allocated", {}).items():
                if rid in pos:
                    rx, ry = pos[rid]
                    rname = resources.get(rid, {}).get("name", rid)
                    is_cycle = (rid, pid) in cycle_edges or (rname, pname) in cycle_edges or (f"[{rname}]", pname) in cycle_edges
                    color = DANGER if is_cycle else CYAN
                    width = 3 if is_cycle else 2
                    self._draw_arrow(
                        rx, ry, px, py,
                        color=color,
                        dash=None,
                        width=width,
                        start_radius=(self.RESOURCE_WIDTH / 2) * self.zoom_scale,
                        end_radius=self.NODE_RADIUS * self.zoom_scale,
                        label=f"{count}×" if count > 1 else ""
                    )

    def _draw_wfg_edges(self, processes: dict, pos: dict, cycle_edges: Set[Tuple[str, str]]):
        """Draws wait-for dependencies between processes in WFG mode."""
        # Find holders
        holder: Dict[str, List[str]] = {}
        for pid, p in processes.items():
            for rid in p.get("allocated", {}):
                holder.setdefault(rid, []).append(pid)

        for pid, p in processes.items():
            if pid not in pos:
                continue
            px, py = pos[pid]
            pname = p.get("name", pid)

            for rid in p.get("requested", {}):
                for hpid in holder.get(rid, []):
                    if hpid != pid and hpid in pos:
                        hx, hy = pos[hpid]
                        hname = processes.get(hpid, {}).get("name", hpid)
                        is_cycle = (pid, hpid) in cycle_edges or (pname, hname) in cycle_edges
                        color = DANGER if is_cycle else PURPLE
                        width = 3 if is_cycle else 2
                        self._draw_arrow(
                            px, py, hx, hy,
                            color=color,
                            dash=None,
                            width=width,
                            start_radius=self.NODE_RADIUS * self.zoom_scale,
                            end_radius=self.NODE_RADIUS * self.zoom_scale,
                            label="waits"
                        )

    def _draw_arrow(self, x1, y1, x2, y2, color: str, dash=None, width: int = 2,
                    start_radius: float = 26, end_radius: float = 26, label: str = ""):
        """Draws a directed arrow with clipped endpoints at node boundaries."""
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy) or 1
        ux, uy = dx / length, dy / length

        sx, sy = x1 + ux * (start_radius + 4), y1 + uy * (start_radius + 4)
        ex, ey = x2 - ux * (end_radius + 6), y2 - uy * (end_radius + 6)

        # Draw glowing background line if danger
        if color == DANGER:
            self.canvas.create_line(
                sx, sy, ex, ey,
                fill="#4D141A",
                width=width + 4
            )

        kw = {
            "fill": color,
            "width": width,
            "arrow": tk.LAST,
            "arrowshape": (12 * max(0.8, self.zoom_scale), 14 * max(0.8, self.zoom_scale), 5)
        }
        if dash:
            kw["dash"] = dash

        self.canvas.create_line(sx, sy, ex, ey, **kw)

        if label:
            mx, my = (sx + ex) / 2, (sy + ey) / 2
            self.canvas.create_text(
                mx + 6, my - 6,
                text=label,
                fill=color,
                font=self.fonts["mono_sm_bold"]
            )

    # ── Node Drawing ──────────────────────────────────────────────────────────

    def _draw_process_node(self, pid: str, p: dict, x: float, y: float, deadlocked: bool):
        """Draws circular Process node with status dot, priority badge, and name."""
        r = self.NODE_RADIUS * self.zoom_scale
        state = p.get("state", "running")
        base_color = p.get("color", CYAN)

        state_border = {
            "running": SUCCESS,
            "waiting": WARNING,
            "blocked": DANGER,
            "terminated": TEXT_MUTED,
            "rolled_back": PURPLE,
        }.get(state, CYAN)

        # Deadlock Crimson Halo Glow
        if deadlocked:
            for glow_r, glow_color in [(r + 10, "#4A1218"), (r + 5, DANGER)]:
                self.canvas.create_oval(
                    x - glow_r, y - glow_r, x + glow_r, y + glow_r,
                    outline=glow_color, width=2, fill=""
                )

        # Main Process Circle Body
        fill_color = BG_CARD if not deadlocked else "#240E13"
        border_color = DANGER if deadlocked else state_border
        border_width = 3 if deadlocked else 2

        self.canvas.create_oval(
            x - r, y - r, x + r, y + r,
            fill=fill_color,
            outline=border_color,
            width=border_width
        )

        # Process ID
        self.canvas.create_text(
            x, y - 6 * self.zoom_scale,
            text=pid,
            fill=TEXT_PRIMARY if not deadlocked else DANGER,
            font=self.fonts["mono_bold"]
        )

        # Process Name
        name = p.get("name", "")
        if len(name) > 12:
            name = name[:10] + "…"
        self.canvas.create_text(
            x, y + 8 * self.zoom_scale,
            text=name,
            fill=TEXT_SECONDARY,
            font=self.fonts["caption"]
        )

        # Priority Pill at Top-Right
        pri = p.get("priority", 1)
        px_pos = x + r * 0.65
        py_pos = y - r * 0.65
        self.canvas.create_oval(
            px_pos - 7, py_pos - 7, px_pos + 7, py_pos + 7,
            fill=BG_INPUT, outline=BORDER_DEFAULT, width=1
        )
        self.canvas.create_text(
            px_pos, py_pos,
            text=f"P{pri}",
            fill=CYAN,
            font=self.fonts["mono_badge"]
        )

    def _draw_resource_node(self, rid: str, r: dict, x: float, y: float, deadlocked: bool):
        """Draws rounded-look Resource Card with instances status slots."""
        hw = (self.RESOURCE_WIDTH / 2) * self.zoom_scale
        hh = (self.RESOURCE_HEIGHT / 2) * self.zoom_scale

        # Deadlock Crimson Halo Glow
        if deadlocked:
            self.canvas.create_rectangle(
                x - hw - 6, y - hh - 6, x + hw + 6, y + hh + 6,
                outline=DANGER, width=2, fill="#3A1016"
            )

        fill_color = BG_CARD if not deadlocked else "#260E13"
        border_color = DANGER if deadlocked else BORDER_DEFAULT

        # Card body
        self.canvas.create_rectangle(
            x - hw, y - hh, x + hw, y + hh,
            fill=fill_color,
            outline=border_color,
            width=2
        )

        # Resource ID
        self.canvas.create_text(
            x, y - 10 * self.zoom_scale,
            text=rid,
            fill=CYAN if not deadlocked else DANGER,
            font=self.fonts["mono_bold"]
        )

        # Resource Name
        rname = r.get("name", "")
        if len(rname) > 10:
            rname = rname[:8] + "…"
        self.canvas.create_text(
            x, y + 2 * self.zoom_scale,
            text=rname,
            fill=TEXT_SECONDARY,
            font=self.fonts["caption"]
        )

        # Instance dots/slots
        total = r.get("total", 1)
        avail = r.get("available", 0)
        dot_r = max(2, int(3 * self.zoom_scale))
        spacing = 8 * self.zoom_scale
        max_visible_dots = min(total, 6)
        start_x = x - (max_visible_dots - 1) * spacing / 2
        dot_y = y + 14 * self.zoom_scale

        for i in range(max_visible_dots):
            dx = start_x + i * spacing
            d_color = SUCCESS if i < avail else DANGER
            self.canvas.create_oval(
                dx - dot_r, dot_y - dot_r, dx + dot_r, dot_y + dot_r,
                fill=d_color, outline=""
            )

    # ── HUD Controls & Legend ─────────────────────────────────────────────────

    def _draw_hud(self, mode: str):
        """Draws top on-canvas HUD toolbar."""
        mode_text = "Resource Allocation Graph (RAG)" if mode == "rag" else "Wait-For Graph (WFG)"
        self.canvas.create_text(
            16, 22,
            text=mode_text,
            fill=TEXT_SECONDARY,
            font=self.fonts["body_bold"],
            anchor="w"
        )

        zoom_pct = f"{int(self.zoom_scale * 100)}%"
        self.canvas.create_text(
            self.canvas.winfo_width() - 20 if self.canvas.winfo_width() > 100 else 600, 22,
            text=f"Zoom: {zoom_pct}",
            fill=TEXT_MUTED,
            font=self.fonts["mono_sm"],
            anchor="e"
        )

    def _draw_legend(self, mode: str, detection_result=None):
        """Draws compact technical legend."""
        y = 44
        x = 16

        items = [
            (CYAN, "─────", "Allocation (Resource → Process)"),
            (WARNING, "- - -", "Request (Process → Resource)"),
            (DANGER, "━━━━━", "Detected Deadlock Cycle"),
            (SUCCESS, "●", "Available Instance"),
            (DANGER, "●", "Allocated Instance"),
        ] if mode == "rag" else [
            (PURPLE, "─────", "Wait-For Dependency (P_i → P_j)"),
            (DANGER, "━━━━━", "Detected Deadlock Cycle"),
        ]

        curr_y = y
        for color, sym, label in items:
            self.canvas.create_text(
                x, curr_y,
                text=sym,
                fill=color,
                font=self.fonts["mono_sm_bold"],
                anchor="w"
            )
            self.canvas.create_text(
                x + 36, curr_y,
                text=label,
                fill=TEXT_MUTED,
                font=self.fonts["caption"],
                anchor="w"
            )
            curr_y += 16

    def _draw_empty_state(self):
        """Draws simple, clear instructions when graph is empty."""
        w = self.canvas.winfo_width() or 700
        h = self.canvas.winfo_height() or 500
        
        self.canvas.create_text(
            w // 2, h // 2 - 14,
            text="No processes or resources in system.",
            fill=TEXT_SECONDARY,
            font=self.fonts["body_bold"]
        )
        self.canvas.create_text(
            w // 2, h // 2 + 12,
            text="Add processes and resources manually or load a scenario from the Scenarios tab.",
            fill=TEXT_MUTED,
            font=self.fonts["caption"],
            justify="center"
        )
