"""
Setup script to generate sample files for the collection directory.
Creates HTML, PNG, and PDF files for testing the HTTP server.
"""

import os
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch


def create_images():
    """Create sample PNG images"""
    print("Creating sample images...")
    
    # Logo image
    img = Image.new('RGB', (800, 600), color='#667eea')
    draw = ImageDraw.Draw(img)
    
    # Draw border
    draw.rectangle([50, 50, 750, 550], outline='white', width=5)
    
    # Draw text (using default font)
    try:
        font_large = ImageFont.truetype("arial.ttf", 60)
        font_medium = ImageFont.truetype("arial.ttf", 36)
        font_small = ImageFont.truetype("arial.ttf", 24)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    draw.text((400, 200), 'Lab 2', fill='white', anchor='mm', font=font_large)
    draw.text((400, 300), 'Multithreaded HTTP Server', fill='white', anchor='mm', font=font_medium)
    draw.text((400, 400), 'Concurrent Programming', fill='white', anchor='mm', font=font_small)
    
    img.save('collection/images/logo.png')
    print("  ✓ Created collection/images/logo.png")
    
    # Banner image
    banner = Image.new('RGB', (1200, 300), color='#764ba2')
    draw = ImageDraw.Draw(banner)
    draw.text((600, 150), 'Welcome to Lab 2!', fill='white', anchor='mm', font=font_large)
    banner.save('collection/images/banner.png')
    print("  ✓ Created collection/images/banner.png")
    
    # Icon image
    icon = Image.new('RGB', (256, 256), color='#3498db')
    draw = ImageDraw.Draw(icon)
    draw.ellipse([50, 50, 206, 206], fill='white')
    draw.text((128, 128), 'HTTP', fill='#3498db', anchor='mm', font=font_medium)
    icon.save('collection/images/icon.png')
    print("  ✓ Created collection/images/icon.png")


def create_pdfs():
    """Create sample PDF documents"""
    print("\nCreating sample PDFs...")
    
    # Lab Manual PDF
    c = canvas.Canvas('collection/documents/lab_manual.pdf', pagesize=letter)
    width, height = letter
    
    # Page 1
    c.setFont("Helvetica-Bold", 24)
    c.drawString(inch, height - inch, "Lab 2 Manual")
    
    c.setFont("Helvetica", 12)
    y = height - 1.5*inch
    
    content = [
        "Multithreaded HTTP Server Implementation",
        "",
        "Objectives:",
        "1. Implement a multithreaded HTTP server",
        "2. Demonstrate race conditions and thread-safe solutions",
        "3. Implement rate limiting with sliding window algorithm",
        "",
        "Prerequisites:",
        "- Understanding of HTTP protocol",
        "- Knowledge of threading concepts",
        "- Python programming experience",
        "",
        "This manual provides step-by-step instructions for completing",
        "Lab 2 of the Protocols and Regulations course.",
    ]
    
    for line in content:
        c.drawString(inch, y, line)
        y -= 0.3*inch
    
    c.showPage()
    c.save()
    print("  ✓ Created collection/documents/lab_manual.pdf")
    
    # Research Paper PDF
    c = canvas.Canvas('collection/documents/concurrency_paper.pdf', pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 20)
    c.drawString(inch, height - inch, "Concurrency vs Parallelism")
    
    c.setFont("Helvetica-Oblique", 14)
    c.drawString(inch, height - 1.3*inch, "A Study in Programming Language Theory")
    
    c.setFont("Helvetica", 11)
    y = height - 2*inch
    
    paper_content = [
        "Abstract",
        "",
        "This paper examines the distinction between concurrency and parallelism",
        "in the context of Programming Language Theory (PLT). We demonstrate that",
        "these concepts are orthogonal and discuss their implications for",
        "concurrent program design.",
        "",
        "1. Introduction",
        "",
        "Concurrency is a language concept that deals with structuring programs",
        "as independent parts. Parallelism, on the other hand, is a hardware",
        "concept concerning the simultaneous execution of computations.",
        "",
        "2. Key Differences",
        "",
        "- Concurrency: About program structure and composition",
        "- Parallelism: About simultaneous execution on hardware",
        "- Orthogonality: One does not imply the other",
    ]
    
    for line in paper_content:
        c.drawString(inch, y, line)
        y -= 0.25*inch
    
    c.showPage()
    c.save()
    print("  ✓ Created collection/documents/concurrency_paper.pdf")
    
    # Book PDF
    c = canvas.Canvas('collection/Books/threading_guide.pdf', pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 28)
    c.drawString(inch, height - 1.5*inch, "Threading Guide")
    
    c.setFont("Helvetica", 16)
    c.drawString(inch, height - 2*inch, "A Practical Introduction to")
    c.drawString(inch, height - 2.3*inch, "Multithreaded Programming")
    
    c.setFont("Helvetica-Oblique", 12)
    c.drawString(inch, height - 3*inch, "Python Edition")
    
    c.showPage()
    
    # Table of Contents
    c.setFont("Helvetica-Bold", 18)
    c.drawString(inch, height - inch, "Table of Contents")
    
    c.setFont("Helvetica", 12)
    y = height - 1.5*inch
    toc = [
        "Chapter 1: Introduction to Threading ..................... 1",
        "Chapter 2: Thread Safety and Locks ....................... 15",
        "Chapter 3: Race Conditions ............................... 28",
        "Chapter 4: Synchronization Primitives .................... 42",
        "Chapter 5: Thread Pools .................................. 56",
        "Chapter 6: Concurrent Data Structures .................... 70",
        "Chapter 7: Performance Considerations .................... 85",
        "Appendix A: Code Examples ................................ 100",
    ]
    
    for line in toc:
        c.drawString(inch, y, line)
        y -= 0.4*inch
    
    c.showPage()
    c.save()
    print("  ✓ Created collection/Books/threading_guide.pdf")
    
    # Rate Limiting PDF
    c = canvas.Canvas('collection/Books/rate_limiting.pdf', pagesize=letter)
    width, height = letter
    
    c.setFont("Helvetica-Bold", 22)
    c.drawString(inch, height - inch, "Rate Limiting Algorithms")
    
    c.setFont("Helvetica", 12)
    y = height - 1.5*inch
    
    rl_content = [
        "Rate limiting is a technique to control the rate of requests sent or",
        "received by a system. This document covers common algorithms:",
        "",
        "1. Fixed Window",
        "   - Simple counter reset at fixed intervals",
        "   - Pros: Easy to implement",
        "   - Cons: Burst at window boundaries",
        "",
        "2. Sliding Window",
        "   - Track individual request timestamps",
        "   - Pros: Smooth rate limiting",
        "   - Cons: Higher memory usage",
        "",
        "3. Token Bucket",
        "   - Tokens added at fixed rate",
        "   - Each request consumes a token",
        "   - Pros: Allows controlled bursts",
        "",
        "4. Leaky Bucket",
        "   - Requests processed at fixed rate",
        "   - Queue for overflow",
        "   - Pros: Smooth output rate",
    ]
    
    for line in rl_content:
        c.drawString(inch, y, line)
        y -= 0.3*inch
    
    c.showPage()
    c.save()
    print("  ✓ Created collection/Books/rate_limiting.pdf")


def create_nested_html():
    """Create HTML files in subdirectories"""
    print("\nCreating nested HTML files...")
    
    # Documents README
    with open('collection/documents/README.html', 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Documents</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
        .content { background: white; padding: 30px; border-radius: 8px; }
        h1 { color: #2c3e50; }
        a { color: #3498db; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="content">
        <h1>📄 Documents</h1>
        <p>This directory contains sample PDF documents for testing file serving.</p>
        <ul>
            <li><a href="lab_manual.pdf">Lab Manual</a> - Instructions for Lab 2</li>
            <li><a href="concurrency_paper.pdf">Concurrency Paper</a> - Research on concurrency vs parallelism</li>
        </ul>
        <p><a href="/">← Back to Home</a></p>
    </div>
</body>
</html>
""")
    print("  ✓ Created collection/documents/README.html")
    
    # Images README
    with open('collection/images/README.html', 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Images</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1000px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
        .content { background: white; padding: 30px; border-radius: 8px; }
        h1 { color: #2c3e50; }
        .gallery { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }
        .gallery img { width: 100%; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
        a { color: #3498db; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="content">
        <h1>🖼️ Image Gallery</h1>
        <p>Sample PNG images for testing image serving.</p>
        <div class="gallery">
            <div>
                <h3>Logo</h3>
                <img src="logo.png" alt="Logo">
                <p><a href="logo.png" download>Download</a></p>
            </div>
            <div>
                <h3>Banner</h3>
                <img src="banner.png" alt="Banner">
                <p><a href="banner.png" download>Download</a></p>
            </div>
            <div>
                <h3>Icon</h3>
                <img src="icon.png" alt="Icon">
                <p><a href="icon.png" download>Download</a></p>
            </div>
        </div>
        <p><a href="/">← Back to Home</a></p>
    </div>
</body>
</html>
""")
    print("  ✓ Created collection/images/README.html")
    
    # Books README
    with open('collection/Books/README.html', 'w', encoding='utf-8') as f:
        f.write("""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Books</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; background: #f5f5f5; }
        .content { background: white; padding: 30px; border-radius: 8px; }
        h1 { color: #2c3e50; }
        .book { background: #f8f9fa; padding: 20px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #3498db; }
        a { color: #3498db; text-decoration: none; }
        a:hover { text-decoration: underline; }
    </style>
</head>
<body>
    <div class="content">
        <h1>📚 Books</h1>
        <p>E-books and technical references for concurrent programming.</p>
        
        <div class="book">
            <h3>Threading Guide</h3>
            <p>A practical introduction to multithreaded programming in Python.</p>
            <p><a href="threading_guide.pdf">Download PDF</a></p>
        </div>
        
        <div class="book">
            <h3>Rate Limiting Algorithms</h3>
            <p>Comprehensive guide to rate limiting techniques and implementations.</p>
            <p><a href="rate_limiting.pdf">Download PDF</a></p>
        </div>
        
        <p><a href="/">← Back to Home</a></p>
    </div>
</body>
</html>
""")
    print("  ✓ Created collection/Books/README.html")


def main():
    """Main setup function"""
    print("=" * 60)
    print("Setting up Lab 2 collection directory")
    print("=" * 60)
    
    # Check if directories exist
    os.makedirs('collection/images', exist_ok=True)
    os.makedirs('collection/documents', exist_ok=True)
    os.makedirs('collection/Books', exist_ok=True)
    os.makedirs('downloads', exist_ok=True)
    
    try:
        create_images()
        create_pdfs()
        create_nested_html()
        
        print("\n" + "=" * 60)
        print("✅ Setup complete!")
        print("=" * 60)
        print("\nCollection directory structure:")
        print("collection/")
        print("  ├── index.html")
        print("  ├── about.html")
        print("  ├── images/")
        print("  │   ├── logo.png")
        print("  │   ├── banner.png")
        print("  │   ├── icon.png")
        print("  │   └── README.html")
        print("  ├── documents/")
        print("  │   ├── lab_manual.pdf")
        print("  │   ├── concurrency_paper.pdf")
        print("  │   └── README.html")
        print("  └── Books/")
        print("      ├── threading_guide.pdf")
        print("      ├── rate_limiting.pdf")
        print("      └── README.html")
        print("\nYou can now start the server:")
        print("  python server.py collection")
        print("\nOr use Docker:")
        print("  docker-compose up server")
        
    except Exception as e:
        print(f"\n❌ Error during setup: {e}")
        print("\nMake sure you have installed the required packages:")
        print("  pip install -r requirements.txt")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
