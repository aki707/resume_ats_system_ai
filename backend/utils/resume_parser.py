import os
import logging
import PyPDF2
import docx
import pdfplumber
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ResumeParser:
    
    @staticmethod
    def extract_text_from_pdf(file_path: str) -> str:
        """
        Extract text from PDF file using multiple methods.
        
        Args:
            file_path (str): Path to the PDF file
        
        Returns:
            str: Extracted text from the PDF
        """
        try:
            # Method 1: PyPDF2
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                pdf_text = " ".join([
                    page.extract_text() or "" for page in reader.pages
                ])
                
                if pdf_text.strip():
                    return pdf_text
            
            # Method 2: pdfplumber (fallback)
            with pdfplumber.open(file_path) as pdf:
                plumber_text = " ".join([
                    page.extract_text() or "" for page in pdf.pages
                ])
                
                return plumber_text
        
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {e}")
            return ""

    @staticmethod
    def extract_text_from_docx(file_path: str) -> str:
        """
        Extract text from DOCX file.
        
        Args:
            file_path (str): Path to the DOCX file
        
        Returns:
            str: Extracted text from the document
        """
        try:
            doc = docx.Document(file_path)
            return " ".join([
                paragraph.text for paragraph in doc.paragraphs if paragraph.text
            ])
        except Exception as e:
            logger.error(f"Error extracting text from DOCX {file_path}: {e}")
            return ""

    @staticmethod
    def extract_text_from_txt(file_path: str) -> str:
        """
        Extract text from plain text file.
        
        Args:
            file_path (str): Path to the text file
        
        Returns:
            str: Text content of the file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except Exception as e:
            logger.error(f"Error reading text file {file_path}: {e}")
            return ""

    @staticmethod
    def extract_text(file_path: str) -> str:
        """
        Determine file type and extract text.
        
        Args:
            file_path (str): Path to the file
        
        Returns:
            str: Extracted text from the file
        
        Raises:
            ValueError: If unsupported file type is provided
        """
        file_extension = os.path.splitext(file_path)[1].lower()
        
        extraction_methods = {
            '.pdf': ResumeParser.extract_text_from_pdf,
            '.docx': ResumeParser.extract_text_from_docx,
            '.doc': ResumeParser.extract_text_from_docx,
            '.txt': ResumeParser.extract_text_from_txt
        }
        
        extraction_method = extraction_methods.get(file_extension)
        
        if extraction_method:
            return extraction_method(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

    @staticmethod
    def preprocess_resume_text(text: str) -> str:
        """
        Preprocess resume text for parsing.
        
        Args:
            text (str): Raw resume text
        
        Returns:
            str: Cleaned and preprocessed text
        """
        # Remove extra whitespaces
        text = " ".join(text.split())
        
        return text
    @staticmethod
    def extract_clickable_links_from_pdf(file_path: str) -> List[str]:
        """
        Extract clickable hyperlinks from PDF annotations.
        
        Args:
            file_path (str): Path to the PDF file
        
        Returns:
            List[str]: List of URLs extracted from annotations.
        """
        links = []
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    if "/Annots" in page:
                        annots = page["/Annots"]
                        for annot in annots:
                            annot_obj = annot.get_object()
                            if "/A" in annot_obj and "/URI" in annot_obj["/A"]:
                                links.append(annot_obj["/A"]["/URI"])
        except Exception as e:
            logger.error(f"Error extracting clickable links from PDF {file_path}: {e}")
        return links
    @staticmethod
    def extract_urls(text: str, file_path: str = None) -> List[str]:
        """
        Extract all URLs from text and, for PDFs, from clickable annotations.
        
        Args:
            text (str): Text containing embedded links.
            file_path (str, optional): Path to the file (used for PDFs).
        
        Returns:
            List[str]: List of extracted URLs.
        """
        url_pattern = r'(https?://[^\s]+)'
        urls = re.findall(url_pattern, text)
        
        # If file_path is provided and is a PDF, extract clickable links from annotations
        if file_path and os.path.splitext(file_path)[1].lower() == '.pdf':
            clickable_urls = ResumeParser.extract_clickable_links_from_pdf(file_path)
            urls.extend(clickable_urls)
        
        return list(set(urls))

    @staticmethod
    def extract_contact_information(text: str) -> Dict[str, Optional[str]]:
        """
        Extract contact information from resume text.
        
        Args:
            text (str): Preprocessed resume text
        
        Returns:
            Dict containing contact details
        """
        import re
        
        contact_info = {
            'email': None,
            'phone': None,
            'linkedin': None
        }
        
        # Email regex
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        contact_info['email'] = emails[0] if emails else None
        
        # Phone number regex (supports various formats)
        phone_pattern = r'(\+\d{1,2}\s?)?(\d{3}[-.]?)?\s?\d{3}[-.]?\d{4}'
        phones = re.findall(phone_pattern, text)
        contact_info['phone'] = phones[0][0] if phones else None
        
        # LinkedIn URL
        linkedin_pattern = r'linkedin\.com/in/[A-Za-z0-9-]+'
        linkedin_matches = re.findall(linkedin_pattern, text)
        contact_info['linkedin'] = linkedin_matches[0] if linkedin_matches else None
        
        return contact_info