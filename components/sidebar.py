import flet as ft
from components.theme import ThemeColors
from components.widgets import UserAvatar

class Sidebar(ft.Container):
    """Authenticated views navigation sidebar, dynamically updated based on role."""
    def __init__(self, page: ft.Page, active_route: str, user: dict, on_logout, on_theme_toggle):
        self.page = page
        self.active_route = active_route
        self.user = user
        self.on_logout = on_logout
        self.on_theme_toggle = on_theme_toggle
        self.is_dark = page.theme_mode == ft.ThemeMode.DARK
        self.role = user.get("role", "student")

        super().__init__(
            width=260,
            bgcolor=ft.colors.with_opacity(0.85, ThemeColors.DARK_SURFACE) if self.is_dark else ft.colors.with_opacity(0.9, ThemeColors.LIGHT_SURFACE),
            border=ft.border.only(right=ft.border.BorderSide(1, ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if self.is_dark else ThemeColors.LIGHT_BORDER))),
            padding=ft.padding.symmetric(horizontal=12, vertical=20),
            alignment=ft.alignment.center,
        )
        self.build_sidebar()

    def build_sidebar(self):
        # 1. Platform Branding
        brand = ft.Row(
            controls=[
                ft.Icon(ft.icons.EXPLORE, color=ThemeColors.PRIMARY, size=28),
                ft.Text("Campus Dive", size=18, weight=ft.FontWeight.BLACK, color=ThemeColors.DARK_TEXT if self.is_dark else ThemeColors.LIGHT_TEXT),
            ],
            spacing=10,
            alignment=ft.MainAxisAlignment.START,
        )

        # 2. Navigation items based on role
        nav_items = []
        
        # Helper to define active styling
        def get_btn_style(route_path):
            is_active = self.active_route == route_path
            if is_active:
                return {
                    "bgcolor": ft.colors.with_opacity(0.1, ThemeColors.PRIMARY),
                    "icon_color": ThemeColors.PRIMARY,
                    "text_color": ThemeColors.PRIMARY if self.is_dark else ThemeColors.PRIMARY_DARK,
                    "weight": ft.FontWeight.BOLD,
                }
            else:
                return {
                    "bgcolor": ft.colors.TRANSPARENT,
                    "icon_color": ThemeColors.DARK_TEXT_MUTED if self.is_dark else ThemeColors.LIGHT_TEXT_MUTED,
                    "text_color": ThemeColors.DARK_TEXT if self.is_dark else ThemeColors.LIGHT_TEXT,
                    "weight": ft.FontWeight.NORMAL,
                }

        # Menu structures
        student_menu = [
            ("Dashboard", "/student/dashboard", ft.icons.DASHBOARD),
            ("My Documents", "/student/documents", ft.icons.ATTACHMENT),
            ("Direct Messages", "/messages", ft.icons.CHAT),
            ("Social Hub", "/social/feed", ft.icons.SHARE),
            ("Groups", "/social/groups", ft.icons.GROUP),
            ("Settings", "/student/settings", ft.icons.SETTINGS),
        ]

        admin_menu = [
            ("Dashboard", "/admin/dashboard", ft.icons.DASHBOARD),
            ("Students Manager", "/admin/students", ft.icons.SCHOOL),
            ("Direct Messages", "/messages", ft.icons.CHAT),
            ("Social Hub", "/social/feed", ft.icons.SHARE),
            ("Groups", "/social/groups", ft.icons.GROUP),
            ("Broadcast Panel", "/admin/broadcast", ft.icons.CAMPAIGN),
            ("AI Code Auditor", "/audit", ft.icons.SHIELD),
            ("Analytics Logs", "/admin/analytics", ft.icons.ANALYTICS),
            ("Role Config", "/admin/roles", ft.icons.ADMIN_PANEL_SETTINGS),
            ("Settings", "/student/settings", ft.icons.SETTINGS),
        ]

        active_menu = admin_menu if self.role in ("admin", "manager", "interviewer") else student_menu

        for title, route, icon in active_menu:
            btn_style = get_btn_style(route)
            
            nav_items.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(icon, color=btn_style["icon_color"], size=20),
                            ft.Text(title, color=btn_style["text_color"], weight=btn_style["weight"], size=13),
                        ],
                        spacing=12,
                    ),
                    padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    bgcolor=btn_style["bgcolor"],
                    border_radius=8,
                    on_click=lambda e, r=route: self.page.go(r),
                    hover_color=ft.colors.with_opacity(0.05, ThemeColors.PRIMARY),
                )
            )

        # 3. User Profile Card at bottom
        fullname = f"{self.user.get('firstname', '')} {self.user.get('lastname', '')}"
        user_card = ft.Container(
            content=ft.Row(
                controls=[
                    UserAvatar(self.user.get('firstname', ''), self.user.get('lastname', ''), size=36),
                    ft.Column(
                        controls=[
                            ft.Text(fullname, size=12, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if self.is_dark else ThemeColors.LIGHT_TEXT, overflow=ft.TextOverflow.ELLIPSIS, max_lines=1),
                            ft.Text(self.user.get('email', ''), size=10, color=ThemeColors.DARK_TEXT_MUTED if self.is_dark else ThemeColors.LIGHT_TEXT_MUTED, overflow=ft.TextOverflow.ELLIPSIS, max_lines=1),
                        ],
                        spacing=1,
                        tight=True,
                        expand=True,
                    )
                ],
                spacing=8,
            ),
            padding=ft.padding.all(8),
            bgcolor=ft.colors.with_opacity(0.05, ThemeColors.DARK_SURFACE_LIGHT if self.is_dark else ThemeColors.LIGHT_SURFACE_LIGHT),
            border_radius=8,
        )

        # 4. Settings Toggles (Theme, Logout)
        theme_toggle_icon = ft.icons.LIGHT_MODE if self.is_dark else ft.icons.DARK_MODE
        theme_toggle_text = "Light Mode" if self.is_dark else "Dark Mode"
        
        system_controls = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(theme_toggle_icon, color=ThemeColors.DARK_TEXT_MUTED if self.is_dark else ThemeColors.LIGHT_TEXT_MUTED, size=20),
                            ft.Text(theme_toggle_text, color=ThemeColors.DARK_TEXT if self.is_dark else ThemeColors.LIGHT_TEXT, size=13),
                        ],
                        spacing=12,
                    ),
                    padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    on_click=self.on_theme_toggle,
                    border_radius=8,
                    hover_color=ft.colors.with_opacity(0.05, ThemeColors.PRIMARY),
                ),
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Icon(ft.icons.EXIT_TO_APP, color=ThemeColors.DANGER, size=20),
                            ft.Text("Logout", color=ThemeColors.DANGER, size=13, weight=ft.FontWeight.BOLD),
                        ],
                        spacing=12,
                    ),
                    padding=ft.padding.symmetric(horizontal=12, vertical=10),
                    on_click=self.on_logout,
                    border_radius=8,
                    hover_color=ft.colors.with_opacity(0.1, ThemeColors.DANGER),
                )
            ],
            spacing=2,
        )

        # 5. Assemble everything in Column
        self.content = ft.Column(
            controls=[
                brand,
                ft.Divider(height=20, color=ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if self.is_dark else ThemeColors.LIGHT_BORDER)),
                ft.Column(controls=nav_items, spacing=2, expand=True), # Scrollable middle nav
                ft.Divider(height=20, color=ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER if self.is_dark else ThemeColors.LIGHT_BORDER)),
                user_card,
                ft.Container(height=10),
                system_controls,
            ],
            spacing=0,
            expand=True,
        )
