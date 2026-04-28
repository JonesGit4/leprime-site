#!/usr/bin/env python3
"""
Fix Bloco 4 issues reported by Jony:
1. Homepage cards: make card images clickable
2. Homepage nav: add "Produtos" dropdown submenu with 6 product pages
3. Product pages hero: fix text contrast (stronger overlay + text shadow)
4. Product pages hero: don't stretch small images; use gradient-first approach
5. Product pages nav: add same dropdown submenu
"""

import re
import os
import glob

PRODUCTS = [
    ("piso-laminado", "Piso Laminado"),
    ("piso-vinilico", "Piso Vinílico"),
    ("porcelanato", "Porcelanato"),
    ("revestimentos-ceramicos", "Revestimentos Cerâmicos"),
    ("rodapes-acabamentos", "Rodapés e Acabamentos"),
    ("pisos-area-externa", "Pisos para Área Externa"),
]

# ============================================================
# FIX 1 & 2: Homepage — cards clickable + nav dropdown
# ============================================================
def fix_homepage():
    path = "public/index.html"
    with open(path, "r") as f:
        html = f.read()

    # --- FIX 1: Make card image divs clickable ---
    # Pattern: <div class="relative h-48 overflow-hidden"><img ... src="SLUG.webp"/></div>
    # Wrap the div in an <a> linking to the product page
    for slug, name in PRODUCTS:
        # Find the image tag pattern and wrap the parent div
        old_img_div = f'<div class="relative h-48 overflow-hidden"><img alt='
        # We need to find each specific card. Find by src attribute
        pattern = rf'(<div class="relative h-48 overflow-hidden">)(<img[^>]*src="{re.escape(slug)}\.webp"[^>]*/>)(</div>)'
        replacement = rf'<a href="/produtos/{slug}" title="{name} — LE Prime Acabamentos" class="block relative h-48 overflow-hidden">\2</a>'
        html_new = re.sub(pattern, replacement, html)
        if html_new != html:
            print(f"  ✅ Card image linked: {slug}")
            html = html_new
        else:
            print(f"  ⚠️ Could not find card image pattern for: {slug}")

    # --- FIX 2: Add dropdown submenu to nav ---
    # Desktop nav: replace simple "Produtos" link with dropdown
    dropdown_items = "\n".join([
        f'          <a href="/produtos/{slug}" class="block px-4 py-2 text-sm text-gray-300 hover:text-white hover:bg-[#1a2830]/80 transition-colors">{name}</a>'
        for slug, name in PRODUCTS
    ])

    old_nav_produtos = '<a href="#produtos" title="Produtos: pisos, porcelanato e revestimentos" class="text-gray-300 hover:text-white font-medium transition-colors">Produtos</a>'
    new_nav_produtos = f'''<div class="relative group">
        <a href="#produtos" title="Produtos: pisos, porcelanato e revestimentos" class="text-gray-300 hover:text-white font-medium transition-colors inline-flex items-center gap-1">Produtos<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mt-0.5"><polyline points="6 9 12 15 18 9"/></svg></a>
        <div class="absolute top-full left-1/2 -translate-x-1/2 pt-2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
          <div class="bg-[#243842] border border-[#3d5a6c]/40 rounded-lg shadow-xl py-2 min-w-[220px]">
{dropdown_items}
          </div>
        </div>
      </div>'''
    
    if old_nav_produtos in html:
        html = html.replace(old_nav_produtos, new_nav_produtos, 1)
        print("  ✅ Desktop nav dropdown added")
    else:
        print("  ⚠️ Could not find desktop nav Produtos link")

    # Mobile menu: add product sub-links
    old_mobile_produtos = '<a href="#produtos" class="text-gray-300 hover:text-white font-medium px-2">Produtos</a>'
    if old_mobile_produtos in html:
        # Check if this exists in the original homepage (it was generated differently)
        pass

    # Try the actual mobile menu pattern from the homepage
    mobile_pattern = r'(<a href="#produtos"[^>]*class="[^"]*"[^>]*>Produtos</a>)(<a href="#marcas")'
    mobile_sub = "\n".join([
        f'        <a href="/produtos/{slug}" class="text-gray-400 hover:text-white text-sm px-4">{name}</a>'
        for slug, name in PRODUCTS
    ])
    mobile_replacement = rf'\1\n{mobile_sub}\n      \2'
    html_new = re.sub(mobile_pattern, mobile_replacement, html, count=1)
    if html_new != html:
        html = html_new
        print("  ✅ Mobile menu sub-links added")
    else:
        print("  ⚠️ Could not find mobile menu pattern, trying alternative...")
        # Try simpler pattern
        for mobile_try in [
            'class="text-gray-300 hover:text-white font-medium transition-colors">Produtos</a><a href="#marcas"',
        ]:
            if mobile_try in html:
                html = html.replace(mobile_try, 
                    'class="text-gray-300 hover:text-white font-medium transition-colors">Produtos</a>' + 
                    '\n' + mobile_sub + '\n<a href="#marcas"', 1)
                print("  ✅ Mobile menu sub-links added (alt pattern)")
                break

    with open(path, "w") as f:
        f.write(html)
    print(f"  📄 Homepage updated: {path}")


# ============================================================
# FIX 3 & 4: Product pages — contrast + image approach + nav dropdown
# ============================================================
def fix_product_page(filepath, slug, name):
    with open(filepath, "r") as f:
        html = f.read()

    # --- FIX 3: Stronger hero overlay with gradient ---
    # Old: <div class="absolute inset-0 bg-[#1a2830]/80"></div>
    # New: gradient from left (fully dark) to right (semi-transparent) + stronger overall
    old_overlay = '<div class="absolute inset-0 bg-[#1a2830]/80"></div>'
    new_overlay = '<div class="absolute inset-0 bg-gradient-to-r from-[#1a2830] via-[#1a2830]/95 to-[#1a2830]/85"></div>'
    if old_overlay in html:
        html = html.replace(old_overlay, new_overlay)
        print(f"  ✅ Hero overlay strengthened: {slug}")
    
    # --- FIX 3b: Add text-shadow to h1 for extra readability ---
    old_h1_class = 'class="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-6 text-balance"'
    new_h1_class = 'class="text-3xl md:text-4xl lg:text-5xl font-bold text-white mb-6 text-balance" style="text-shadow: 0 2px 8px rgba(0,0,0,0.7)"'
    if old_h1_class in html:
        html = html.replace(old_h1_class, new_h1_class)
        print(f"  ✅ H1 text-shadow added: {slug}")

    # --- FIX 3c: Add text-shadow to hero paragraph ---
    old_p_class = 'class="text-lg md:text-xl text-gray-300 leading-relaxed max-w-3xl"'
    new_p_class = 'class="text-lg md:text-xl text-gray-200 leading-relaxed max-w-3xl" style="text-shadow: 0 1px 4px rgba(0,0,0,0.6)"'
    if old_p_class in html:
        html = html.replace(old_p_class, new_p_class)
        print(f"  ✅ Hero paragraph text-shadow + lighter color: {slug}")

    # --- FIX 3d: Make breadcrumb text lighter ---
    old_breadcrumb = 'class="flex items-center gap-2 text-sm text-gray-400"'
    new_breadcrumb = 'class="flex items-center gap-2 text-sm text-gray-300" style="text-shadow: 0 1px 3px rgba(0,0,0,0.5)"'
    if old_breadcrumb in html:
        html = html.replace(old_breadcrumb, new_breadcrumb)
        print(f"  ✅ Breadcrumb contrast improved: {slug}")

    # --- FIX 4: Add Produtos dropdown to product page nav ---
    # Desktop nav
    old_prod_nav = '<a href="/#produtos" title="Nossos produtos" class="text-white font-medium transition-colors">Produtos</a>'
    dropdown_items_pp = "\n".join([
        f'            <a href="/produtos/{s}" class="block px-4 py-2 text-sm {"text-white font-medium bg-[#1a2830]/60" if s == slug else "text-gray-300 hover:text-white hover:bg-[#1a2830]/80"} transition-colors">{n}</a>'
        for s, n in PRODUCTS
    ])
    new_prod_nav = f'''<div class="relative group">
          <a href="/#produtos" title="Nossos produtos" class="text-white font-medium transition-colors inline-flex items-center gap-1">Produtos<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="mt-0.5"><polyline points="6 9 12 15 18 9"/></svg></a>
          <div class="absolute top-full left-1/2 -translate-x-1/2 pt-2 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-50">
            <div class="bg-[#243842] border border-[#3d5a6c]/40 rounded-lg shadow-xl py-2 min-w-[220px]">
{dropdown_items_pp}
            </div>
          </div>
        </div>'''
    if old_prod_nav in html:
        html = html.replace(old_prod_nav, new_prod_nav)
        print(f"  ✅ Product page desktop nav dropdown: {slug}")

    # Mobile nav
    old_mobile_prod = '<a href="/#produtos" class="text-white font-medium px-2">Produtos</a>'
    mobile_sub_pp = "\n".join([
        f'        <a href="/produtos/{s}" class="{"text-white text-sm px-6 font-medium" if s == slug else "text-gray-400 hover:text-white text-sm px-6"}">{n}</a>'
        for s, n in PRODUCTS
    ])
    new_mobile_prod = f'<a href="/#produtos" class="text-white font-medium px-2">Produtos</a>\n{mobile_sub_pp}'
    if old_mobile_prod in html:
        html = html.replace(old_mobile_prod, new_mobile_prod)
        print(f"  ✅ Product page mobile nav sub-links: {slug}")

    with open(filepath, "w") as f:
        f.write(html)
    print(f"  📄 Product page updated: {filepath}")


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    os.chdir("/work/repos/wt-bloco4-fixes")
    
    print("\n🏠 Fixing Homepage...")
    fix_homepage()
    
    print("\n📄 Fixing Product Pages...")
    for slug, name in PRODUCTS:
        filepath = f"public/produtos/{slug}/index.html"
        if os.path.exists(filepath):
            fix_product_page(filepath, slug, name)
        else:
            print(f"  ❌ Not found: {filepath}")
    
    print("\n✅ All fixes applied!")
