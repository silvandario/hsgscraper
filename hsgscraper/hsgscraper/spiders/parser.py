import os
import fitz  # PyMuPDF

# Paths
pdf_path = os.path.join("pdfs", "8,000,1.00.pdf")
output_dir = "raw"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "8,000,1.00.txt")

# Extract text from PDF
with fitz.open(pdf_path) as doc:
    text = ""
    for page in doc:
        text += page.get_text()

# Save extracted text to .txt file
with open(output_path, "w", encoding="utf-8") as f:
    f.write(text)

print(f"✅ Text extracted and saved to {output_path}")