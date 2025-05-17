import re

def fix_duplicate_routes():
    # Read the original file
    with open('app.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Find the admin routes section that was added at the end
    admin_routes_section = re.search(r'# ─── Admin Routes ─+\n\n@app\.route\(\'/admin\'\)(.*?)# ─── Run ─+', 
                                     content, re.DOTALL)
    
    if not admin_routes_section:
        print("Could not find the admin routes section")
        return False
    
    # Get the admin routes that were added at the end
    admin_routes = admin_routes_section.group(1)
    
    # Find and remove any duplicate route definitions
    # This is a list of route patterns to find and remove from the middle of the file
    routes_to_remove = [
        r'@app\.route\(\'/admin/support-tickets/<int:ticket_id>/reopen\', methods=\[\'POST\'\]\).*?def admin_reopen_ticket\(ticket_id\):.*?return redirect\(url_for\(\'admin_view_ticket\', ticket_id=ticket_id\)\)',
        r'@app\.route\(\'/admin/users\'\).*?def admin_users\(\):.*?return render_template\(\'admin/users\.html\', users=users\)',
        r'@app\.route\(\'/admin/users/<int:user_id>\'\).*?def admin_view_user\(user_id\):.*?return render_template\(\'admin/view_user\.html\', user=user\)',
        r'@app\.route\(\'/admin/users/<int:user_id>/toggle-admin\', methods=\[\'POST\'\]\).*?def admin_toggle_admin\(user_id\):.*?return redirect\(url_for\(\'admin_view_user\', user_id=user_id\)\)',
        r'@app\.route\(\'/admin/users/<int:user_id>/delete\', methods=\[\'POST\'\]\).*?def admin_delete_user\(user_id\):.*?return redirect\(url_for\(\'admin_users\'\)\)',
        r'@app\.route\(\'/admin/products\'\).*?def admin_products\(\):.*?return render_template\(\'admin/products\.html\', products=products\)',
        r'@app\.route\(\'/admin/products/<int:product_id>\'\).*?def admin_view_product\(product_id\):.*?return render_template\(\'admin/view_product\.html\', product=product\)',
        r'@app\.route\(\'/admin/products/<int:product_id>/delete\', methods=\[\'POST\'\]\).*?def admin_delete_product\(product_id\):.*?return redirect\(url_for\(\'admin_products\'\)\)'
    ]
    
    # Remove each duplicate route
    cleaned_content = content
    for route_pattern in routes_to_remove:
        # Find the first occurrence in the middle of the file (before the admin routes section)
        match = re.search(route_pattern, cleaned_content[:cleaned_content.find('# ─── Admin Routes ─')], re.DOTALL)
        if match:
            # Remove the matched route
            start, end = match.span()
            cleaned_content = cleaned_content[:start] + cleaned_content[end:]
            print(f"Removed duplicate route: {match.group(0)[:50]}...")
    
    # Write the cleaned content back to the file
    with open('app_fixed.py', 'w', encoding='utf-8') as file:
        file.write(cleaned_content)
    
    print("Fixed file saved as app_fixed.py")
    return True

if __name__ == "__main__":
    fix_duplicate_routes()
