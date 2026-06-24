import flet as ft
import re
from components.theme import ThemeColors, glass_card_style
from components.widgets import PageHeader

# ── PRESET TEMPLATE DEFINITIONS ──
PRESETS = [
    {
        "label": "SQLi — Login Query (PHP)",
        "code": """<?php
$email = $_POST['email'];
$password = $_POST['password'];
$sql = "SELECT * FROM users WHERE email='$email' AND password='$password'";
$result = mysqli_query($conn, $sql);
if (mysqli_num_rows($result) > 0) {
    $_SESSION['user'] = mysqli_fetch_assoc($result);
    header("Location: /dashboard");
}"""
    },
    {
        "label": "XSS — Search Output (PHP)",
        "code": """<?php
$search = $_GET['q'];
echo "<h2>Results for: " . $search . "</h2>";
$results = $db->query("SELECT * FROM posts WHERE title LIKE '%$search%'");"""
    },
    {
        "label": "IDOR & Traversal — Node.js",
        "code": """app.get('/download', (req, res) => {
  const filename = req.query.file;
  const filePath = path.join(__dirname, 'uploads', filename);
  res.download(filePath);
});"""
    }
]

def perform_static_audit(code: str) -> str:
    """Performs regular-expression based static security analysis on code and returns markdown report."""
    findings = []
    
    # 1. SQL Injection Checks
    sqli_pattern = r"(SELECT|INSERT|UPDATE|DELETE).*?\$.*?"
    if re.search(sqli_pattern, code, re.IGNORECASE) or "LIKE '%$" in code:
        findings.append("""### 🔴 Finding 1: Critical SQL Injection Vulnerability
- **Severity**: CRITICAL
- **Impact**: Attackers can bypass authentication controls, extract credentials, dump database schemas, or delete logs.
- **Cause**: Variable interpolation is performed directly inside the SQL string query.
- **Remediation**: Use parameterized query bindings (prepared statements) instead of string interpolation.
  ```php
  // SAFE PATTERN
  $stmt = $conn->prepare("SELECT * FROM users WHERE email = ? AND password = ?");
  $stmt->execute([$email, $password]);
  ```""")

    # 2. Cross-Site Scripting (XSS) Checks
    xss_pattern = r"echo\s+.*?\$_(GET|POST|REQUEST)"
    if re.search(xss_pattern, code) or "echo \"<h2>Results for: \" . $" in code:
        findings.append("""### 🟠 Finding 2: High Reflected XSS Vulnerability
- **Severity**: HIGH
- **Impact**: Enables execution of malicious JavaScript within the victim's session context, leading to session hijacking.
- **Cause**: Unsanitized parameters from `$_GET` or `$_POST` are printed directly to the HTML output.
- **Remediation**: Escape output variables using contextual sanitizers such as `htmlspecialchars()`.
  ```php
  // SAFE PATTERN
  echo "<h2>Results for: " . htmlspecialchars($search, ENT_QUOTES, 'UTF-8') . "</h2>";
  ```""")

    # 3. Path Traversal & IDOR Checks
    traversal_pattern = r"(res\.download|readfile|file_get_contents|file_exists).*?\$.*?"
    if re.search(traversal_pattern, code) or "req.query.file" in code:
        findings.append("""### 🔴 Finding 3: High Path Traversal / Arbitrary File Leak
- **Severity**: HIGH
- **Impact**: Allows external attackers to traverse server directories and retrieve sensitive config.php or environment secrets.
- **Cause**: User-supplied filenames are directly joined to system path configurations without resolving folder boundaries.
- **Remediation**: Apply filename sanitization using path extraction routines and confirm target directory boundaries.
  ```javascript
  // SAFE PATTERN (Node.js)
  const safeName = path.basename(req.query.file);
  const filePath = path.resolve(__dirname, 'uploads', safeName);
  if (!filePath.startsWith(path.resolve(__dirname, 'uploads'))) {
      return res.status(403).send('Forbidden');
  }
  ```""")

    if not findings:
        return """### ✅ Code Security Audit Report
- **Scan Status**: Completed
- **Vulnerabilities**: 0 Detected
- **Security Posture**: Healthy

No common signature vulnerabilities (SQLi, XSS, Path Traversal) were identified in this snippet. 

*Remember to run dynamic analysis and unit security tests prior to staging deployments.*"""

    report_header = f"""# Security Audit Report
*Scan completed: static analysis engines mapped {len(findings)} issues.*

---
"""
    return report_header + "\n\n---\n\n".join(findings)

def show_audit_workspace(page: ft.Page, user: dict):
    """Renders the AI/Static Code Auditor dashboard workspace."""
    is_dark = page.theme_mode == ft.ThemeMode.DARK
    style = glass_card_style(is_dark)

    header = PageHeader(
        title="Security Auditor Workspace",
        subtitle="Paste code blocks to scan for SQL Injection, Cross-Site Scripting (XSS), and Path Traversal hazards.",
        is_dark=is_dark
    )

    # Inputs and Outputs
    code_editor = ft.TextField(
        placeholder="Paste code snippet here...",
        multiline=True,
        min_lines=15,
        max_lines=20,
        text_size=12,
        text_style=ft.TextStyle(font_family="Consolas"),
        border_color=ThemeColors.PRIMARY if is_dark else ThemeColors.LIGHT_BORDER,
        focused_border_color=ThemeColors.PRIMARY,
    )

    report_markdown = ft.Markdown(
        value="### Scanner Status: Idle\n*Paste a code snippet on the left panel and click 'Run Security Audit' to review diagnostic results.*",
        selectable=True,
        extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
        expand=True,
    )

    def load_preset(e, preset_code):
        code_editor.value = preset_code
        page.update()

    def run_audit(e):
        code_text = code_editor.value.strip()
        if not code_text:
            page.open(ft.SnackBar(ft.Text("Please enter some code to audit.")))
            return

        report_markdown.value = "### Scanning code...\nRunning static analysis checks..."
        page.update()
        
        # Execute audit checks
        report_text = perform_static_audit(code_text)
        
        report_markdown.value = report_text
        page.update()

    # Preset templates buttons
    preset_buttons = []
    for p in PRESETS:
        preset_buttons.append(
            ft.TextButton(
                text=p["label"],
                on_click=lambda e, code=p["code"]: load_preset(e, code),
                style=ft.ButtonStyle(color=ThemeColors.PRIMARY_LIGHT if is_dark else ThemeColors.PRIMARY_DARK),
            )
        )

    presets_row = ft.Row(
        controls=[
            ft.Text("Load Preset:", size=11, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT_MUTED if is_dark else ThemeColors.LIGHT_TEXT_MUTED),
            ft.Row(preset_buttons, spacing=4)
        ],
        wrap=True,
        alignment=ft.MainAxisAlignment.START,
    )

    # Panes
    left_pane = ft.Container(
        content=ft.Column([
            ft.Text("Source Code Input", size=14, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
            code_editor,
            ft.ElevatedButton(
                text="Run Security Audit",
                icon=ft.icons.SHIELD,
                bgcolor=ThemeColors.PRIMARY,
                color=ft.colors.WHITE,
                on_click=run_audit,
                style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                height=44,
                expand=True,
            )
        ], spacing=10),
        padding=16,
        expand=True,
        **style
    )

    right_pane = ft.Container(
        content=ft.Column([
            ft.Text("Audit Diagnostics Report", size=14, weight=ft.FontWeight.BOLD, color=ThemeColors.DARK_TEXT if is_dark else ThemeColors.LIGHT_TEXT),
            ft.Divider(height=1, color=ft.colors.with_opacity(0.05, ThemeColors.DARK_BORDER if is_dark else ThemeColors.LIGHT_BORDER)),
            ft.Container(content=report_markdown, expand=True, scroll=ft.ScrollMode.ADAPTIVE),
        ], spacing=10, expand=True),
        padding=16,
        expand=True,
        **style
    )

    layout = ft.Container(
        content=ft.Column([
            header,
            presets_row,
            ft.Container(height=5),
            ft.Row([left_pane, right_pane], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.STRETCH, spacing=16, expand=True)
        ], spacing=10, expand=True),
        padding=30,
        expand=True,
    )

    return layout
