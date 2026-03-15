#!/usr/bin/env python3
"""
Script de migração: limpa HTML do Weebly e corrige todos os paths para local.
"""
import os
import re
import shutil

SRC = "/home/user/fmmudancas/site_download/www.fmmudancas.com"
DEST = "/home/user/fmmudancas/migrated_site"

def fix_html(content, depth=0):
    prefix = "../" * depth

    # 1. CSS Weebly CDN → local
    content = re.sub(
        r'https://cdn11\.editmysite\.com/css/sites\.css[^"\']*',
        f"{prefix}assets/css/sites.css", content)
    content = re.sub(
        r'https://cdn11\.editmysite\.com/css/old/fancybox\.css[^"\']*',
        f"{prefix}assets/css/fancybox.css", content)
    content = re.sub(
        r'https://cdn11\.editmysite\.com/css/social-icons\.css[^"\']*',
        f"{prefix}assets/css/social-icons.css", content)
    content = re.sub(
        r'https://cdn2\.editmysite\.com/css/old/slideshow/slideshow\.css[^"\']*',
        f"{prefix}assets/css/slideshow.css", content)

    # 2. CSS local Weebly
    content = re.sub(
        r'files/main_style\.css[^"\']*',
        f"{prefix}assets/css/main_style.css", content)

    # 3. Fontes CDN Weebly → Google Fonts CDN (funciona sem login)
    content = re.sub(
        r'https://cdn2\.editmysite\.com/fonts/([^/]+)/font\.css[^"\']*',
        lambda m: f"https://fonts.googleapis.com/css2?family={m.group(1).replace('_', '+')}&display=swap",
        content)

    # 4. JS locais Weebly
    content = re.sub(r'files/theme/custom\.js[^"\']*', f"{prefix}assets/js/custom.js", content)
    content = re.sub(r'files/theme/jquery\.loadTemplate\.min\.js[^"\']*', f"{prefix}assets/js/jquery.loadTemplate.min.js", content)
    content = re.sub(r'files/theme/jquery\.pxuMenu\.js[^"\']*', f"{prefix}assets/js/jquery.pxuMenu.js", content)
    content = re.sub(r'files/theme/jquery\.revealer\.js[^"\']*', f"{prefix}assets/js/jquery.revealer.js", content)
    content = re.sub(r'files/theme/jquery\.trend\.js[^"\']*', f"{prefix}assets/js/jquery.trend.js", content)
    content = re.sub(r'files/theme/plugins\.js[^"\']*', f"{prefix}assets/js/plugins.js", content)
    content = re.sub(r'files/templateArtifacts\.js[^"\']*', f"{prefix}assets/js/templateArtifacts.js", content)

    # 5. JS CDN Weebly → local
    content = re.sub(
        r'https://cdn11\.editmysite\.com/js/site/main\.js[^"\']*',
        f"{prefix}assets/js/main.js", content)
    content = re.sub(
        r'https://cdn2\.editmysite\.com/js/old/slideshow-jq\.js[^"\']*',
        f"{prefix}assets/js/slideshow-jq.js", content)
    content = re.sub(
        r'https://cdn2\.editmysite\.com/js/lang/pt_PT/stl\.js[^"\'&]*(?:&amp;)?',
        f"{prefix}assets/js/stl.js", content)
    content = re.sub(
        r'https://cdn2\.editmysite\.com/js/site/main-customer-accounts-site\.js[^"\']*',
        f"{prefix}assets/js/main-customer-accounts-site.js", content)

    # 6. Remover scripts Cloudflare email protection
    content = re.sub(
        r'<script[^>]*cdn-cgi[^>]*>.*?</script>\s*',
        '', content, flags=re.DOTALL)
    content = re.sub(
        r'<script[^>]*email-decode[^>]*></script>\s*',
        '', content)

    # 7. Imagens tema local
    content = re.sub(
        r'files/theme/images/([^"\'?\s]+)',
        lambda m: f"{prefix}assets/images/{m.group(1).split('?')[0]}",
        content)

    # 8. Uploads absolutos (https://www.fmmudancas.com/uploads/...)
    content = re.sub(
        r'https://(?:www\.)?fmmudancas\.com/uploads/([^"\'?\s]+)',
        lambda m: f"{prefix}assets/images/uploads/{m.group(1).split('?')[0]}",
        content)

    # 9. Uploads relativos (/uploads/... ou uploads/...) — apenas se não já processados
    content = re.sub(
        r'(?<=["\'])/?uploads/([^"\'?\s]+)',
        lambda m: f"{prefix}assets/images/uploads/{m.group(1).split('?')[0]}",
        content)

    # 10. Links internos absolutos para o domínio
    content = re.sub(
        r'https://(?:www\.)?fmmudancas\.com/([^"\'?\s#]*)',
        lambda m: (f"{prefix}{m.group(1)}" if m.group(1) else f"{prefix}index.html"),
        content)

    # 11. jQuery CDN → local
    content = re.sub(
        r'https://cdn11\.editmysite\.com/js/jquery-1\.8\.3\.min\.js[^"\']*',
        f"{prefix}assets/js/jquery-1.8.3.min.js", content)

    # 12. ASSETS_BASE JS variable
    content = re.sub(
        r"var ASSETS_BASE = '//cdn11\.editmysite\.com/';",
        f"var ASSETS_BASE = '{prefix}assets/';", content)

    # 13. Snowday tracking script — remover completamente o bloco
    content = re.sub(
        r"<script[^>]*>\s*\(function\([^)]*\).*?snowday.*?\}\)\s*;?\s*</script>",
        '', content, flags=re.DOTALL)
    # Fallback: remover referência inline ao snowday
    content = re.sub(
        r"[^<]*snowday262[^;]*;?", '', content)

    # 14. Restantes cdn2.editmysite.com não críticos — comentar
    content = re.sub(
        r"(src=['\"]https://cdn2\.editmysite\.com/[^'\"]*['\"])",
        r'data-removed=\1', content)

    return content


def process_html_files():
    html_files = [f for f in os.listdir(SRC) if f.endswith('.html')]
    processed = 0
    for fname in html_files:
        src_path = os.path.join(SRC, fname)
        dest_path = os.path.join(DEST, fname)
        with open(src_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        content = fix_html(content, depth=0)
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(content)
        processed += 1

    print(f"✓ {processed} ficheiros HTML processados")
    return processed


def copy_extras():
    robots_src = os.path.join(SRC, "robots.txt")
    if os.path.exists(robots_src):
        shutil.copy2(robots_src, os.path.join(DEST, "robots.txt"))
        print("✓ robots.txt copiado")


if __name__ == "__main__":
    print("=== Iniciando migração FM Mudanças ===\n")
    n = process_html_files()
    copy_extras()

    # Verificação final
    import subprocess
    result = subprocess.run(
        ['grep', '-rl', 'cdn11.editmysite.com', DEST],
        capture_output=True, text=True)
    remaining = len([l for l in result.stdout.strip().split('\n') if l])
    print(f"\n{'✓ Zero' if remaining == 0 else f'⚠ {remaining}'} referências cdn11.editmysite.com restantes")

    result2 = subprocess.run(
        ['grep', '-rl', 'cdn2.editmysite.com', DEST],
        capture_output=True, text=True)
    remaining2 = len([l for l in result2.stdout.strip().split('\n') if l])
    print(f"{'✓ Zero' if remaining2 == 0 else f'⚠ {remaining2}'} referências cdn2.editmysite.com restantes")

    print(f"\n=== Migração concluída: {n} páginas processadas ===")
