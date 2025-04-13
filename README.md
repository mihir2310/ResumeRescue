# ResumeRescue

An AI-powered resume analysis tool that helps job seekers optimize their resumes for specific job descriptions. The application uses OCR to extract text from job description images and compares it with uploaded resumes to provide personalized recommendations.

## Features

- Upload job descriptions as images (JPG, PNG)
- Upload resumes in PDF format
- Automatic text extraction using OCR
- Smart requirement matching
- Personalized recommendations for resume improvement
- Modern, responsive UI

## Prerequisites

- Python 3.8+
- Tesseract OCR
- OpenCV
- Django 4.2+

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/ResumeRescue.git
cd ResumeRescue
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Tesseract OCR:

- macOS: `brew install tesseract`
- Ubuntu: `sudo apt-get install tesseract-ocr`
- Windows: Download from [Tesseract website](https://github.com/UB-Mannheim/tesseract/wiki)

4. Install Python dependencies:

```bash
pip install -r requirements.txt
```

5. Set up the Django project:

```bash
python manage.py migrate
python manage.py createsuperuser
```

6. Run the development server:

```bash
python manage.py runserver
```

## Project Structure

```
ResumeRescue/
├── ResumeRescue/          # Main project directory
│   ├── __init__.py
│   ├── settings.py        # Django settings
│   ├── urls.py           # URL configuration
│   ├── utils.py          # Utility functions
│   └── views.py          # View functions
├── templates/            # HTML templates
│   ├── base.html        # Main template
│   └── final.html       # Results template
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
└── README.md           # Project documentation
```

## Usage

1. Navigate to `http://localhost:8000` in your browser
2. Upload a job description image (JPG or PNG)
3. Upload your resume (PDF)
4. Click "Analyze Documents"
5. View your personalized recommendations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
