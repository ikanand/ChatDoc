import fitz  # PyMuPDF
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import pickle
import os
from typing import List, Dict


INDEX_PATH = "faiss_index.index1"
METADATA_PATH = "metadata1.pkl"
EMBEDDINGS_PATH = "embeddings1.npy"


def extract_clean_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []
    for page_num, page in enumerate(doc):
        text = page.get_text()
        cleaned = ' '.join(text.split())
        pages.append({"text": cleaned, "page": page_num + 1})
    return pages


def chunk_pdf_pages(pages, chunk_size=500, chunk_overlap=50):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""],
    )

    all_chunks = []
    for page in pages:
        chunks = splitter.split_text(page["text"])
        for chunk in chunks:
            all_chunks.append({
                "text": chunk,
                "page": page["page"]
            })
    return all_chunks


def embed_chunks(chunks, model):
    texts = [chunk["text"] for chunk in chunks]
    embeddings = model.encode(texts, convert_to_numpy=True)
    return embeddings


def load_metadata():
    if os.path.exists(METADATA_PATH):
        with open(METADATA_PATH, "rb") as f:
            return pickle.load(f)
    return []


def save_metadata(metadata):
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(metadata, f)


def save_embeddings(all_embeddings):
    np.save(EMBEDDINGS_PATH, all_embeddings)


def load_embeddings():
    if os.path.exists(EMBEDDINGS_PATH):
        return np.load(EMBEDDINGS_PATH)
    return np.empty((0, 768), dtype=np.float32)  # Adjust if using other models


def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    if embeddings.shape[0] > 0:
        index.add(embeddings)
    return index


def add_pdf_to_index(pdf_path, model_name="BAAI/bge-base-en-v1.5"):
    filename = os.path.basename(pdf_path)
    pages = extract_clean_text_from_pdf(pdf_path)
    chunks = chunk_pdf_pages(pages)

    for chunk in chunks:
        chunk["filename"] = filename

    model = SentenceTransformer(model_name)
    embeddings = embed_chunks(chunks, model)

    existing_embeddings = load_embeddings()
    updated_embeddings = np.vstack([existing_embeddings, embeddings])

    metadata = load_metadata()
    metadata.extend(chunks)

    index = build_faiss_index(updated_embeddings)
    faiss.write_index(index, INDEX_PATH)
    save_metadata(metadata)
    save_embeddings(updated_embeddings)
    print(f"✅ Added {len(chunks)} chunks from {filename}")


def delete_pdf_from_index(filename_to_delete):
    metadata = load_metadata()
    embeddings = load_embeddings()

    # Filter out entries
    new_metadata = []
    new_embeddings = []
    for i, entry in enumerate(metadata):
        if entry["filename"] != filename_to_delete:
            new_metadata.append(entry)
            new_embeddings.append(embeddings[i])

    new_embeddings = np.array(new_embeddings)
    index = build_faiss_index(new_embeddings)

    faiss.write_index(index, INDEX_PATH)
    save_metadata(new_metadata)
    save_embeddings(new_embeddings)
    print(f"🗑️ Deleted all chunks from {filename_to_delete}")


def search_faiss(query, model_name="BAAI/bge-base-en-v1.5", top_k=5):
    if not os.path.exists(INDEX_PATH):
        print("❌ FAISS index not found.")
        return []

    model = SentenceTransformer(model_name)
    query_embedding = model.encode([query])

    index = faiss.read_index(INDEX_PATH)
    metadata = load_metadata()

    D, I = index.search(query_embedding, top_k)
    results = []
    for i in I[0]:
        if i < len(metadata):
            results.append(metadata[i])
    return results

def get_all_pdfs():
    metadata = load_metadata()
    pdfs = set()
    for entry in metadata:
        pdfs.add(entry["filename"])
    return list(pdfs)

def get_pdf_chunks(filename):
    metadata = load_metadata()
    chunks = [entry for entry in metadata if entry["filename"] == filename]
    return chunks

def get_pdf_page_text(filename, page_number):
    metadata = load_metadata()
    for entry in metadata:
        if entry["filename"] == filename and entry["page"] == page_number:
            return entry["text"]
    return None 

def get_pdf_page_numbers(filename):
    metadata = load_metadata()
    page_numbers = set()
    for entry in metadata:
        if entry["filename"] == filename:
            page_numbers.add(entry["page"])
    return sorted(page_numbers)