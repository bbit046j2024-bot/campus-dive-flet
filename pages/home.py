import flet as ft
from components.theme import ThemeColors, glass_card_style
from components.navbar import Navbar

def show_home(page: ft.Page):
    """Renders the public landing page."""
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    style = glass_card_style(is_dark)

    # 1. Hero Section
    hero_title = ft.Text(
        "Find where you belong.",
        size=46,
        weight=ft.FontWeight.W_900,
        color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT,
        text_align=ft.TextAlign.CENTER,
    )
    
    hero_subtitle = ft.Text(
        "Campus Dive is a premium recruitment management platform & social workspace for students, managers, and code security auditors.",
        size=16,
        color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED,
        text_align=ft.TextAlign.CENTER,
        max_lines=3,
        overflow=ft.TextOverflow.ELLIPSIS,
    )

    cta_buttons = ft.Row(
        controls=[
            ft.ElevatedButton(
                text="Apply Now",
                on_click=lambda _: page.go("/register"),
                bgcolor=ThemeColors.PRIMARY,
                color=ft.colors.WHITE,
                height=48,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=10)),
            ),
            ft.OutlinedButton(
                text="Sign In",
                on_click=lambda _: page.go("/login"),
                height=48,
                style=ft.ButtonStyle(
                    shape=ft.RoundedRectangleBorder(radius=10),
                    color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT,
                ),
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=16,
    )

    hero_container = ft.Container(
        content=ft.Column(
            controls=[
                hero_title,
                ft.Container(height=10),
                hero_subtitle,
                ft.Container(height=20),
                cta_buttons,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        ),
        padding=ft.padding.symmetric(vertical=60, horizontal=20),
        alignment=ft.alignment.center,
    )

    # 2. Features Section
    features_list = [
        (ft.Icons.ASSIGNMENT, "Recruitment Pipeline", "Submit applications, track reviews, and schedule interviews with a visual tracker."),
        (ft.Icons.UPLOAD_FILE, "Secure Document Vault", "Upload resumes and transcripts protected against directory traversal attacks."),
        (ft.Icons.CHAT, "Direct Messaging", "Real-time direct communications between students, coordinators, and interviewers."),
        (ft.Icons.SHARE, "Social Hub Feed", "Create posts, join groups, comment and like inside a sandbox campus social feed."),
        (ft.Icons.SHIELD, "AI Security Audit", "Analyze code snippets for security vulnerabilities like SQL injection and path traversal."),
        (ft.Icons.ANALYTICS, "System Analytics", "Detailed charts and tracking logs for coordinators to monitor application stages.")
    ]

    features_grid = ft.Row(
        wrap=True,
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=20,
        controls=[
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Container(
                            content=ft.Icon(icon, color=ThemeColors.PRIMARY, size=28),
                            bgcolor=ft.colors.with_opacity(0.1, ThemeColors.PRIMARY),
                            padding=12,
                            border_radius=10,
                        ),
                        ft.Text(title, size=16, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
                        ft.Text(desc, size=12, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                    ],
                    spacing=12,
                ),
                width=280,
                height=180,
                padding=20,
                **style
            ) for icon, title, desc in features_list
        ]
    )

    features_header = ft.Column(
        controls=[
            ft.Text("Features & Capabilities", size=24, weight=ft.FontWeight.W_900, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
            ft.Text("Everything you need for student onboarding and campus community management", size=13, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=4,
    )

    features_container = ft.Container(
        content=ft.Column(
            controls=[
                features_header,
                ft.Container(height=30),
                features_grid,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        padding=ft.padding.symmetric(vertical=40, horizontal=20),
    )

    # 3. Stats Section
    stats = [
        ("500+", "Active Students"),
        ("95%", "Onboarding Rate"),
        ("24h", "Average Review Time"),
        ("100%", "Secure Platform")
    ]
    
    stats_row = ft.Row(
        alignment=ft.MainAxisAlignment.SPACE_AROUND,
        controls=[
            ft.Column(
                controls=[
                    ft.Text(val, size=32, weight=ft.FontWeight.W_900, color=ThemeColors.PRIMARY),
                    ft.Text(label, size=12, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            ) for val, label in stats
        ]
    )

    stats_container = ft.Container(
        content=stats_row,
        padding=30,
        border_radius=16,
        bgcolor=ft.colors.with_opacity(0.03, ft.colors.WHITE if is_dark else ft.colors.W_900),
        border=ft.border.all(1, ft.colors.with_opacity(0.05, ft.colors.WHITE if is_dark else ft.colors.W_900)),
        margin=ft.margin.symmetric(vertical=20, horizontal=40),
    )

    # Main layout scrollable container
    layout = ft.Column(
        controls=[
            Navbar(page, "/"),
            ft.Container(
                content=ft.Column(
                    controls=[
                        hero_container,
                        stats_container,
                        features_container,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=20,
                ),
                expand=True,
            )
        ],
        spacing=0,
        scroll=ft.ScrollMode.ADAPTIVE,
    )
    
    return layout
