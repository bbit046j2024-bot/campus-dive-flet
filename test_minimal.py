import flet as ft

def main(page: ft.Page):
    page.title = "Test"
    page.theme_mode = ft.ThemeMode.DARK
    
    # Test 1: Direct add (no routing)
    page.add(ft.Text("Hello from page.add!", size=30, color="white"))
    
    print("main() executed successfully")

if __name__ == "__main__":
    ft.run(main)
