"""
Generate sample files for Lab 1
This script creates PNG images and a sample PDF for testing the HTTP server.
"""

def create_simple_png(filename, width, height, color_rgb):
    """Create a simple PNG image with a solid color"""
    import struct
    import zlib
    
    def png_chunk(chunk_type, data):
        chunk_data = chunk_type + data
        crc = zlib.crc32(chunk_data) & 0xffffffff
        return struct.pack('>I', len(data)) + chunk_data + struct.pack('>I', crc)
    
    # PNG signature
    png_signature = b'\x89PNG\r\n\x1a\n'
    
    # IHDR chunk (image header)
    ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
    ihdr_chunk = png_chunk(b'IHDR', ihdr_data)
    
    # IDAT chunk (image data)
    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # Filter type
        for x in range(width):
            raw_data += bytes(color_rgb)
    
    compressed_data = zlib.compress(raw_data, 9)
    idat_chunk = png_chunk(b'IDAT', compressed_data)
    
    # IEND chunk (image trailer)
    iend_chunk = png_chunk(b'IEND', b'')
    
    # Write PNG file
    with open(filename, 'wb') as f:
        f.write(png_signature)
        f.write(ihdr_chunk)
        f.write(idat_chunk)
        f.write(iend_chunk)
    
    print(f"Created PNG: {filename} ({width}x{height})")


def create_sample_pdf(filename, title, content):
    """Create a simple PDF document"""
    pdf_content = f"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj

2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj

3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
/F2 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica-Bold
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj

4 0 obj
<<
/Length 5 0 R
>>
stream
BT
/F2 24 Tf
50 720 Td
({title}) Tj
ET

BT
/F1 12 Tf
50 680 Td
({content}) Tj
ET

BT
/F1 10 Tf
50 640 Td
(This is a sample PDF document created for testing the HTTP file server.) Tj
ET

BT
/F1 10 Tf
50 620 Td
(Laboratory Work 1 - Network Programming) Tj
ET

BT
/F1 10 Tf
50 600 Td
(Technical University of Moldova) Tj
ET
endstream
endobj

5 0 obj
{len(content) + 400}
endobj

xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000364 00000 n
0000000668 00000 n
trailer
<<
/Size 6
/Root 1 0 R
>>
startxref
687
%%EOF"""
    
    with open(filename, 'w', encoding='latin-1') as f:
        f.write(pdf_content)
    
    print(f"Created PDF: {filename}")


if __name__ == '__main__':
    import os
    
    # Create directories if they don't exist
    os.makedirs('collection', exist_ok=True)
    os.makedirs('collection/Books', exist_ok=True)
    os.makedirs('collection/Books/Research_Papers', exist_ok=True)
    os.makedirs('downloads', exist_ok=True)
    
    # Create PNG images
    print("\n=== Creating PNG images ===")
    create_simple_png('collection/network_diagram.png', 400, 300, (100, 149, 237))  # Cornflower blue
    create_simple_png('collection/server_icon.png', 200, 200, (147, 112, 219))  # Medium purple
    create_simple_png('collection/Books/book_cover.png', 300, 400, (72, 209, 204))  # Medium turquoise
    
    # Create PDF documents
    print("\n=== Creating PDF documents ===")
    create_sample_pdf(
        'collection/Books/Computer_Networking_Kurose_Ross.pdf',
        'Computer Networking: A Top-Down Approach',
        'By James Kurose and Keith Ross - Sample excerpt for testing'
    )
    
    create_sample_pdf(
        'collection/Books/Python_Socket_Programming.pdf',
        'Python Socket Programming Guide',
        'A comprehensive guide to network programming with Python sockets'
    )
    
    create_sample_pdf(
        'collection/Books/HTTP_Protocol_RFC.pdf',
        'HTTP/1.1 Protocol Specification',
        'RFC 2616 - Hypertext Transfer Protocol -- HTTP/1.1'
    )
    
    create_sample_pdf(
        'collection/Books/Research_Papers/TCP_IP_Model.pdf',
        'The TCP/IP Network Model',
        'Research paper on the TCP/IP protocol suite and network architecture'
    )
    
    create_sample_pdf(
        'collection/Books/Research_Papers/Web_Server_Performance.pdf',
        'Web Server Performance Analysis',
        'Study on optimizing HTTP server performance and scalability'
    )
    
    print("\n=== Setup complete! ===")
    print("\nYou can now run the server with:")
    print("  python server.py collection")
    print("\nOr use Docker Compose:")
    print("  docker-compose up --build")
