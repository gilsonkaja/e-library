import requests, io, os, json
from fpdf import FPDF

BASE = 'http://127.0.0.1:5000'

def make_sample_pdf(path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', size=12)
    pdf.cell(0, 10, 'Cloud eLibrary Demo PDF', ln=True)
    pdf.ln(4)
    pdf.multi_cell(0, 8, 'This is a small sample PDF used for demoing the Cloud eLibrary summarization path.\n' * 5)
    pdf.output(path)

def main():
    tmp = os.path.join(os.path.dirname(__file__), 'tmp')
    os.makedirs(tmp, exist_ok=True)
    pdfpath = os.path.join(tmp, 'sample_demo.pdf')
    print('Creating sample PDF:', pdfpath)
    make_sample_pdf(pdfpath)

    # 1) Login as known admin test user (exists in data/users.json)
    print('\n1) Logging in as admin user e2e@example.com')
    login_payload = {'email':'e2e@example.com','password':'StrongPass123'}
    r = requests.post(BASE + '/api/auth/login', json=login_payload)
    print('login status', r.status_code)
    js = r.json(); print(js)
    token = js.get('token')
    headers = {'Authorization': 'Bearer '+token} if token else {}

    # 2) Create book (admin)
    print('\n2) Creating a book (admin)')
    r = requests.post(BASE + '/api/books/', json={'title':'Demo Book','author':'Demo Author'}, headers=headers)
    print('create book status', r.status_code)
    book = r.json(); print(book)
    book_id = book.get('id')

    # 3) Upload PDF
    print('\n3) Uploading sample PDF')
    with open(pdfpath, 'rb') as fh:
        files = {'file': ('sample_demo.pdf', fh, 'application/pdf')}
        r = requests.post(BASE + '/api/upload/', files=files, headers=headers)
    print('upload status', r.status_code)
    upl = r.json(); print(upl)

    # 4) Update book to point to uploaded file (use internal filename for local storage)
    print('\n4) Updating book with uploaded filename/url')
    filename = upl.get('filename') or upl.get('url')
    if filename and book_id:
        r = requests.put(BASE + f'/api/books/{book_id}', json={'filename': filename}, headers=headers)
        print('update status', r.status_code); print(r.json())

    # 5) Summarize
    print('\n5) Requesting summarize')
    r = requests.post(BASE + '/api/ai/summarize', json={'bookId': book_id}, headers=headers)
    print('summarize status', r.status_code)
    try:
        print(json.dumps(r.json(), indent=2))
    except Exception:
        print('No JSON response')

if __name__ == '__main__':
    main()
