import flet as ft

# ── DESIGN SYSTEM CONSTANTS ──
# Harmonious, modern color palette matching Campus Dive V2 UI

class ThemeColors:
    # Core Colors
    PRIMARY = "#6366F1"        # Premium Indigo
    PRIMARY_LIGHT = "#818CF8"  # Indigo 400
    PRIMARY_DARK = "#4F46E5"   # Indigo 600
    
    ACCENT = "#8B5CF6"         # Premium Purple
    ACCENT_LIGHT = "#A78BFA"   # Purple 400
    ACCENT_DARK = "#7C3AED"    # Purple 600
    
    # Semantic Colors
    SUCCESS = "#10B981"        # Emerald 500
    SUCCESS_BG = "#064E3B"     # Emerald 900
    WARNING = "#F59E0B"        # Amber 500
    WARNING_BG = "#78350F"     # Amber 900
    DANGER = "#EF4444"         # Rose 500
    DANGER_BG = "#7F1D1D"      # Rose 900
    INFO = "#3B82F6"           # Blue 500
    INFO_BG = "#1E3A8A"        # Blue 900

    # Dark Mode Surfaces (Glassmorphic & Sleek)
    DARK_BG = "#09090B"        # Zinc 950
    DARK_SURFACE = "#18181B"   # Zinc 900
    DARK_SURFACE_LIGHT = "#27272A" # Zinc 800
    DARK_BORDER = "#3F3F46"    # Zinc 700
    DARK_TEXT = "#F4F4F5"      # Zinc 100
    DARK_TEXT_MUTED = "#A1A1AA" # Zinc 400
    DARK_TEXT_FAINT = "#71717A" # Zinc 500

    # Light Mode Surfaces
    LIGHT_BG = "#F9FAFB"       # Gray 50
    LIGHT_SURFACE = "#FFFFFF"  # White
    LIGHT_SURFACE_LIGHT = "#F3F4F6" # Gray 100
    LIGHT_BORDER = "#E5E7EB"   # Gray 200
    LIGHT_TEXT = "#111827"     # Gray 900
    LIGHT_TEXT_MUTED = "#4B5563" # Gray 600
    LIGHT_TEXT_FAINT = "#9CA3AF" # Gray 400

# ── SHARED STYLES & WIDGET HELPERS ──

def get_theme(is_dark=True):
    """Returns a Flet Theme configuration based on selection."""
    if is_dark:
        return ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ThemeColors.PRIMARY,
                primary_container=ThemeColors.PRIMARY_DARK,
                secondary=ThemeColors.ACCENT,
                surface=ThemeColors.DARK_SURFACE,
                surface_container=ThemeColors.DARK_SURFACE_LIGHT,
                outline=ThemeColors.DARK_BORDER,
                on_surface=ThemeColors.DARK_TEXT,
                error=ThemeColors.DANGER,
            ),
            font_family="Inter",
        )
    else:
        return ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ThemeColors.PRIMARY,
                primary_container=ThemeColors.PRIMARY_LIGHT,
                secondary=ThemeColors.ACCENT,
                surface=ThemeColors.LIGHT_SURFACE,
                surface_container=ThemeColors.LIGHT_SURFACE_LIGHT,
                outline=ThemeColors.LIGHT_BORDER,
                on_surface=ThemeColors.LIGHT_TEXT,
                error=ThemeColors.DANGER,
            ),
            font_family="Inter",
        )

# Glassmorphic Box Decoration Helper
def glass_card_style(is_dark=True):
    """Returns background and border details for a sleek glassmorphic look."""
    if is_dark:
        return {
            "bgcolor": ft.colors.with_opacity(0.6, ThemeColors.DARK_SURFACE),
            "border": ft.border.all(1, ft.colors.with_opacity(0.1, ThemeColors.DARK_BORDER)),
            "border_radius": ft.border_radius.all(16),
            "shadow": ft.BoxShadow(
                blur_radius=20,
                color=ft.colors.with_opacity(0.2, ft.colors.BLACK),
                offset=ft.Offset(0, 8),
            )
        }
    else:
        return {
            "bgcolor": ft.colors.with_opacity(0.8, ThemeColors.LIGHT_SURFACE),
            "border": ft.border.all(1, ft.colors.with_opacity(0.5, ThemeColors.LIGHT_BORDER)),
            "border_radius": ft.border_radius.all(16),
            "shadow": ft.BoxShadow(
                blur_radius=20,
                color=ft.colors.with_opacity(0.05, ft.colors.BLACK),
                offset=ft.Offset(0, 8),
            )
        }
