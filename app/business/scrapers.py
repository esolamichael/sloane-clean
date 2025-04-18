# ~/Desktop/clean-code/app/business/scrapers.py

import requests
from bs4 import BeautifulSoup
import json
import re
import logging
from urllib.parse import urlparse
from ..repositories.business_repository import BusinessRepository
from ..repositories.training_repository import TrainingRepository
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from ..utils.secrets import get_secret
import os
import pandas as pd
from typing import Optional, Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebsiteScraper:
    """Class for scraping business websites to extract relevant information"""
    
    def __init__(self, business_repo=None, training_repo=None):
        try:
            self.business_repo = business_repo or BusinessRepository()
            self.training_repo = training_repo or TrainingRepository()
        except Exception as e:
            logger.error(f"Failed to initialize repositories: {str(e)}")
            raise
        
    def scrape_website(self, business_id, url):
        """
        Scrape a business website to extract useful information
        
        Args:
            business_id: The ID of the business in the database
            url: The website URL to scrape
            
        Returns:
            dict: Extracted information
        """
        try:
            logger.info(f"Scraping website: {url} for business_id: {business_id}")
            
            # Basic validation
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                
            # Parse domain for later use
            domain = urlparse(url).netloc
            
            # Fetch the website
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract relevant information
            extracted_data = {
                'business_id': business_id,
                'source': 'website',
                'url': url,
                'domain': domain,
                'title': self._get_title(soup),
                'description': self._get_meta_description(soup),
                'services': self._extract_services(soup),
                'contact_info': self._extract_contact_info(soup, domain),
                'hours': self._extract_hours(soup),
                'faq': self._extract_faq(soup),
                'about': self._extract_about(soup),
                'raw_text': self._extract_clean_text(soup)
            }
            
            # Store in MongoDB through the repository
            self.business_repo.save_website_data(business_id, extracted_data)
            
            # Also save relevant parts to the training repository
            training_data = self._prepare_training_data(extracted_data)
            self.training_repo.save_training_data(business_id, training_data)
            
            logger.info(f"Successfully scraped website for business_id: {business_id}")
            return extracted_data
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB connection error while scraping website: {str(e)}")
            return {"error": "Database connection error", "url": url}
        except Exception as e:
            logger.error(f"Error scraping website {url}: {str(e)}")
            return {"error": str(e), "url": url}
    
    def _get_title(self, soup):
        """Extract the website title"""
        title_tag = soup.find('title')
        return title_tag.text.strip() if title_tag else ""
    
    def _get_meta_description(self, soup):
        """Extract meta description"""
        meta = soup.find('meta', attrs={'name': 'description'})
        return meta['content'].strip() if meta and 'content' in meta.attrs else ""
    
    def _extract_services(self, soup):
        """Extract services offered by the business"""
        services = []
        
        # Look for common service indicators
        service_sections = soup.find_all(['section', 'div'], class_=lambda c: c and any(x in c.lower() for x in ['service', 'offering', 'product']))
        
        for section in service_sections:
            headings = section.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            for heading in headings:
                services.append(heading.text.strip())
                
        # If no structured services found, try to extract from list items
        if not services:
            service_lists = soup.find_all('ul', class_=lambda c: c and 'service' in c.lower())
            for ul in service_lists:
                items = ul.find_all('li')
                for item in items:
                    services.append(item.text.strip())
        
        return services
    
    def _extract_contact_info(self, soup, domain):
        """Extract contact information"""
        contact_info = {
            'email': self._extract_email(soup, domain),
            'phone': self._extract_phone(soup),
            'address': self._extract_address(soup)
        }
        return contact_info
    
    def _extract_email(self, soup, domain):
        """Extract email addresses"""
        # First look for mailto links
        email_links = soup.select('a[href^=mailto]')
        emails = [link['href'].replace('mailto:', '').strip() for link in email_links]
        
        # If no emails found in links, try regex on text
        if not emails:
            # Look for domain-specific emails first for better quality
            domain_name = domain.split('.')[-2] if len(domain.split('.')) > 1 else domain
            email_pattern = rf'\b[A-Za-z0-9._%+-]+@{re.escape(domain)}\b'
            domain_emails = re.findall(email_pattern, soup.text)
            
            if domain_emails:
                emails = domain_emails
            else:
                # Fall back to any email pattern
                general_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(general_pattern, soup.text)
        
        return emails
    
    def _extract_phone(self, soup):
        """Extract phone numbers"""
        # Look for tel links first
        phone_links = soup.select('a[href^=tel]')
        phones = [link['href'].replace('tel:', '').strip() for link in phone_links]
        
        # If no phones found in links, try regex
        if not phones:
            # US phone pattern - can be expanded for international
            patterns = [
                r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (123) 456-7890 or 123-456-7890
                r'\+\d{1,3}\s?\(?\d{1,4}\)?[-.\s]?\d{3}[-.\s]?\d{4}'  # +1 (123) 456-7890
            ]
            
            all_text = soup.text
            for pattern in patterns:
                found_phones = re.findall(pattern, all_text)
                if found_phones:
                    phones.extend(found_phones)
        
        return phones
    
    def _extract_address(self, soup):
        """Extract physical address"""
        address = ""
        
        # Look for address in structured data
        address_elements = soup.find_all(itemtype="http://schema.org/PostalAddress")
        if address_elements:
            address = " ".join(elem.text.strip() for elem in address_elements)
        
        # Look for address in common containers
        if not address:
            address_containers = soup.find_all(['div', 'p'], class_=lambda c: c and 'address' in c.lower())
            if address_containers:
                address = address_containers[0].text.strip()
        
        # Look for footer address
        if not address:
            footer = soup.find('footer')
            if footer:
                # Common US address pattern
                address_pattern = r'\d+\s+[A-Za-z0-9\s,.-]+\s+[A-Za-z]{2}\s+\d{5}'
                matches = re.search(address_pattern, footer.text)
                if matches:
                    address = matches.group(0)
        
        return address
    
    def _extract_hours(self, soup):
        """Extract business hours"""
        hours = {}
        
        # Look for schema.org structured data
        hours_elements = soup.find_all(itemtype="http://schema.org/OpeningHoursSpecification")
        if hours_elements:
            for elem in hours_elements:
                day = elem.find(itemprop="dayOfWeek")
                opens = elem.find(itemprop="opens")
                closes = elem.find(itemprop="closes")
                
                if day and opens and closes:
                    day_text = day.text.strip()
                    hours[day_text] = {
                        "opens": opens.text.strip(),
                        "closes": closes.text.strip()
                    }
        
        # Look for hours in text
        if not hours:
            hours_section = soup.find_all(['section', 'div'], class_=lambda c: c and any(x in c.lower() for x in ['hour', 'time', 'schedule']))
            
            if hours_section:
                days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
                for day in days:
                    pattern = rf'{day}\s*:?\s*(\d+(?::\d+)?\s*(?:am|pm)?\s*-\s*\d+(?::\d+)?\s*(?:am|pm)?)'
                    matches = re.search(pattern, hours_section[0].text.lower())
                    if matches:
                        hours[day] = matches.group(1)
        
        return hours
    
    def _extract_faq(self, soup):
        """Extract FAQ content"""
        faqs = []
        
        # Look for schema.org structured FAQs
        faq_elements = soup.find_all(itemtype="http://schema.org/FAQPage")
        if faq_elements:
            for elem in faq_elements:
                questions = elem.find_all(itemtype="http://schema.org/Question")
                for q in questions:
                    question = q.find(itemprop="name")
                    answer = q.find(itemprop="text")
                    
                    if question and answer:
                        faqs.append({
                            "question": question.text.strip(),
                            "answer": answer.text.strip()
                        })
        
        # If no structured FAQs, look for FAQ sections
        if not faqs:
            faq_section = soup.find_all(['section', 'div'], class_=lambda c: c and 'faq' in c.lower())
            
            if faq_section:
                # Look for question-answer pairs
                questions = faq_section[0].find_all(['h3', 'h4', 'strong', 'dt'])
                
                for q in questions:
                    # The answer is likely in the next sibling
                    answer = q.find_next(['p', 'div', 'dd'])
                    if answer:
                        faqs.append({
                            "question": q.text.strip(),
                            "answer": answer.text.strip()
                        })
        
        return faqs
    
    def _extract_about(self, soup):
        """Extract 'About us' content"""
        about_text = ""
        
        # Look for about sections
        about_sections = soup.find_all(['section', 'div'], id=lambda i: i and 'about' in i.lower())
        if not about_sections:
            about_sections = soup.find_all(['section', 'div'], class_=lambda c: c and 'about' in c.lower())
        
        if about_sections:
            paragraphs = about_sections[0].find_all('p')
            about_text = "\n".join(p.text.strip() for p in paragraphs)
        
        # If still empty, try looking for about pages
        if not about_text:
            about_links = soup.find_all('a', text=lambda t: t and 'about' in t.lower())
            if about_links:
                # Would ideally follow this link and extract content
                about_text = "About page available at: " + about_links[0].get('href', '')
        
        return about_text
    
    def _extract_clean_text(self, soup):
        """Extract clean text content from the website"""
        # Remove script and style elements
        for script in soup(["script", "style", "header", "footer", "nav"]):
            script.extract()
            
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading and trailing space on each
        lines = (line.strip() for line in text.splitlines())
        
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _prepare_training_data(self, extracted_data):
        """Prepare training data for the AI from extracted website data"""
        training_data = {
            "source": "website",
            "business_name": extracted_data.get('title', ''),
            "business_description": extracted_data.get('description', ''),
            "services": extracted_data.get('services', []),
            "contact_info": extracted_data.get('contact_info', {}),
            "hours": extracted_data.get('hours', {}),
            "faqs": extracted_data.get('faq', []),
            "about": extracted_data.get('about', '')
        }
        
        # Generate example Q&A pairs for training
        example_qa = []
        
        # Add service-related questions
        for service in extracted_data.get('services', []):
            example_qa.append({
                "question": f"Do you offer {service}?",
                "answer": f"Yes, we do offer {service}."
            })
            
        # Add hours-related questions
        if extracted_data.get('hours'):
            example_qa.append({
                "question": "What are your business hours?",
                "answer": "Our hours are: " + json.dumps(extracted_data.get('hours', {}))
            })
            
        # Add contact-related questions
        if extracted_data.get('contact_info', {}).get('phone'):
            phones = extracted_data['contact_info']['phone']
            if phones:
                example_qa.append({
                    "question": "What is your phone number?",
                    "answer": f"You can reach us at {phones[0]}."
                })
                
        # Add location questions
        if extracted_data.get('contact_info', {}).get('address'):
            example_qa.append({
                "question": "Where are you located?",
                "answer": f"We are located at {extracted_data['contact_info']['address']}."
            })
            
        # Add existing FAQs
        example_qa.extend(extracted_data.get('faq', []))
        
        training_data["example_qa"] = example_qa
        
        return training_data


class GBPScraper:
    """Class for scraping Google Business Profile data"""
    
    def __init__(self):
        self.api_key = self._get_api_key()
        
    def _get_api_key(self) -> str:
        """Get Google Maps API key from Secret Manager or environment variable."""
        try:
            # Get API key directly using the correct hyphenated name
            api_key = get_secret("google-maps-api-key")
            if api_key:
                logger.info("Successfully retrieved Google Maps API key from Secret Manager using correct name")
                return api_key
                
            # Fall back to environment variable
            api_key = os.getenv("GOOGLE_MAPS_API_KEY")
            if api_key:
                logger.info("Using Google Maps API key from environment variable")
                return api_key
                
            logger.error("No Google Maps API key found in Secret Manager or environment variables")
            raise ValueError("Google Maps API key not found. Make sure it's set in the Secret Manager or environment variables.")
            
        except Exception as e:
            logger.error(f"Error getting Google Maps API key: {str(e)}")
            raise ValueError(f"Failed to retrieve Google Maps API key: {str(e)}")
            
    def scrape_gbp(self, business_id: str, business_name: str, location: Optional[str] = None) -> Dict[str, Any]:
        """
        Scrape business data from Google Business Profile using Places API.
        
        Args:
            business_id: The ID of the business in our database
            business_name: Name of the business to search for
            location: Optional location to narrow down the search
            
        Returns:
            Dict containing the scraped data or error information
        """
        try:
            # The API key is already validated in the constructor
            api_key = self.api_key
            
            # Construct search query
            search_query = business_name
            if location:
                search_query = f"{business_name} {location}"
            search_query = requests.utils.quote(search_query)
            
            # First, search for the business
            places_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={search_query}&key={api_key}"
            logger.info(f"Searching for business: {business_name}")
            
            response = requests.get(places_url, timeout=10)
            response.raise_for_status()
            search_data = response.json()
            
            if search_data.get('status') != 'OK':
                error_msg = f"Places API error: {search_data.get('status')}"
                details = search_data.get('error_message', '')
                logger.error(f"{error_msg} - {details}")
                return {
                    "success": False,
                    "error": error_msg,
                    "details": details
                }
            
            if not search_data.get('results'):
                logger.error("No results found for the business")
                return {
                    "success": False,
                    "error": "No results found for the business"
                }
            
            # Get the first result (most relevant)
            place = search_data['results'][0]
            place_id = place['place_id']
            
            # Get detailed information about the place
            fields = [
                "name",
                "formatted_address",
                "formatted_phone_number",
                "website",
                "rating",
                "user_ratings_total",
                "types",
                "opening_hours",
                "reviews",
                "photos"
            ]
            
            details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields={','.join(fields)}&key={api_key}"
            logger.info(f"Getting details for place_id: {place_id}")
            
            response = requests.get(details_url, timeout=10)
            response.raise_for_status()
            details_data = response.json()
            
            if details_data.get('status') != 'OK':
                error_msg = f"Places API error: {details_data.get('status')}"
                details = details_data.get('error_message', '')
                logger.error(f"{error_msg} - {details}")
                return {
                    "success": False,
                    "error": error_msg,
                    "details": details
                }
            
            result = details_data['result']
            
            # Process photos if available
            photos = []
            if result.get('photos'):
                for photo in result['photos'][:5]:  # Limit to 5 photos
                    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo['photo_reference']}&key={api_key}"
                    photos.append({
                        'url': photo_url,
                        'height': photo['height'],
                        'width': photo['width']
                    })
            
            # Construct the final response
            business_data = {
                'business_id': business_id,
                'name': result.get('name'),
                'address': result.get('formatted_address'),
                'phone': result.get('formatted_phone_number'),
                'website': result.get('website'),
                'rating': result.get('rating'),
                'total_ratings': result.get('user_ratings_total'),
                'types': result.get('types', []),
                'opening_hours': result.get('opening_hours', {}).get('periods', []),
                'reviews': result.get('reviews', []),
                'photos': photos
            }
            
            logger.info(f"Successfully scraped GBP data for {business_name}")
            return {
                "success": True,
                "data": business_data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error while scraping GBP: {str(e)}")
            return {
                "success": False,
                "error": "Failed to connect to Google Places API",
                "details": str(e)
            }
        except Exception as e:
            logger.error(f"Error scraping GBP: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
