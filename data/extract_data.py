import pdfplumber
import json


def extract_text_from_pdf(file_path):
    data = []
    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                # Split the text into paragraphs or lines for chunking
                chunks = text.split("\n\n")  # Adjust based on text structure
                for chunk_num, chunk in enumerate(chunks):
                    data.append(
                        {
                            "id": f"{file_path}_page{page_num}_chunk{chunk_num}",
                            "text": chunk.strip(),
                            "source": file_path,
                            "page": page_num,
                        }
                    )
    return data


# Extract text from both PDFs and save as JSON
pdf_data_2023 = extract_text_from_pdf("./SOFI-2023.pdf")
pdf_data_2024 = extract_text_from_pdf("./SOFI-2024.pdf")

# Combine and save the extracted data
combined_data = pdf_data_2023 + pdf_data_2024
with open("data/extracted_data.json", "w") as f:
    json.dump(combined_data, f, indent=4)
