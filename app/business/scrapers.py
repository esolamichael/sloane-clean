# ~/Desktop/clean-code/app/business/scrapers.py

import requests
from bs4 import BeautifulSoup
import json
import re
import logging
from urllib.parse import urlparse
from ..repositories.business_repository import BusinessRepository
from ..repositories.training_repository import TrainingRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebsiteScraper:
    """Class for scraping business websites to extract relevant information"""
    
    def __init__(self, business_repo=None, training_repo=None):
        self.business_repo = business_repo or BusinessRepository()
        self.training_repo = training_repo or TrainingRepository()
        
    async def scrape_website(self, business_id, url):
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
            await self.business_repo.save_website_data(business_id, extracted_data)
            
            # Also save relevant parts to the training repository
            training_data = self._prepare_training_data(extracted_data)
            await self.training_repo.save_training_data(business_id, training_data)
            
            logger.info(f"Successfully scraped website for business_id: {business_id}")
            return extracted_data
            
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
    
    def __init__(self, business_repo=None, training_repo=None):
        self.business_repo = business_repo or BusinessRepository()
        self.training_repo = training_repo or TrainingRepository()
        
    async def scrape_gbp(self, business_id, business_name, location=None):
        """
        Scrape Google Business Profile for a business
        
        Args:
            business_id: The ID of the business in the database
            business_name: The business name to search for
            location: Optional location to narrow search
            
        Returns:
            dict: Extracted GBP information
        """
        try:
            logger.info(f"Scraping GBP for: {business_name} in {location or 'any location'}")
            
            import os
            import aiohttp
            import urllib.parse
            
            # Get API key using Secret Manager in production or environment variables in development
            import os
            
            # Check if we're running in production with Secret Manager
            use_secret_manager = os.environ.get('USE_SECRET_MANAGER', 'false').lower() == 'true'
            api_key = None
            
            if use_secret_manager:
                try:
                    # Import Secret Manager client only when needed
                    from google.cloud import secretmanager
                    
                    # Get the project ID from the environment or compute from the service name
                    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
                    if not project_id:
                        # App Engine sets service name in environment
                        app_engine_service = os.environ.get('GAE_SERVICE', 'default')
                        if '-' in app_engine_service:
                            project_id = app_engine_service.split('-')[0]
                    
                    if not project_id:
                        # If still no project ID, try to get it from the metadata server
                        try:
                            import requests
                            # This URL is only available on Google Cloud
                            metadata_url = "http://metadata.google.internal/computeMetadata/v1/project/project-id"
                            project_id = requests.get(
                                metadata_url, 
                                headers={"Metadata-Flavor": "Google"}
                            ).text
                        except Exception as e:
                            logger.warning(f"Could not get project ID from metadata server: {str(e)}")
                    
                    if project_id:
                        # Create the Secret Manager client
                        client = secretmanager.SecretManagerServiceClient()
                        
                        # Access the secret by name - use conventional secret names
                        secret_name = "GOOGLE_MAPS_API_KEY"
                        secret_path = f"projects/{project_id}/secrets/{secret_name}/versions/latest"
                        
                        # Get the secret value
                        response = client.access_secret_version(request={"name": secret_path})
                        api_key = response.payload.data.decode("UTF-8")
                        logger.info(f"Successfully retrieved API key from Secret Manager")
                except Exception as e:
                    logger.error(f"Error accessing Secret Manager: {str(e)}")
            
            # Fall back to environment variables if Secret Manager fails or we're in development
            if not api_key:
                logger.info("Attempting to get API key from environment variables")
                api_key = os.environ.get('GOOGLE_MAPS_API_KEY')
                if not api_key:
                    # Fallback to potential other environment variables
                    api_key = os.environ.get('GOOGLE_PLACES_API_KEY') or os.environ.get('PLACES_API_KEY')
            
            # If still no API key, return an error
            if not api_key:
                # If no API key found, return a specific error message to indicate this issue
                logger.error("Could not retrieve Google Places API key from Secret Manager or environment variables")
                return {
                    "error": "Google Places API key not configured", 
                    "details": "The server could not access the necessary API key for Google's services.",
                    "business_name": business_name
                }
            
            # Format the query and location for search
            search_query = urllib.parse.quote(f"{business_name}")
            if location:
                search_query += f"+{urllib.parse.quote(location)}"
            
            # Step 1: Use Places API text search to find the business
            places_url = f"https://maps.googleapis.com/maps/api/place/textsearch/json?query={search_query}&key={api_key}"
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(places_url, timeout=10) as response:
                        places_data = await response.json()
                        
                        if places_data.get('status') != 'OK':
                            logger.error(f"Places API error: {places_data.get('status')}")
                            return {
                                "error": f"Google Places API error: {places_data.get('status')}",
                                "business_name": business_name
                            }
                        
                        if not places_data.get('results'):
                            logger.error(f"No results found for {business_name}")
                            return {
                                "error": f"No business found matching '{business_name}'", 
                                "business_name": business_name
                            }
                        
                        # Get the first (most relevant) result
                        place = places_data['results'][0]
                        place_id = place['place_id']
                        
                        # Step 2: Get detailed information using Place Details API
                        details_url = f"https://maps.googleapis.com/maps/api/place/details/json?place_id={place_id}&fields=name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,types,opening_hours,review,photos,address_component&key={api_key}"
                        
                        async with session.get(details_url, timeout=10) as details_response:
                            details_data = await details_response.json()
                            
                            if details_data.get('status') != 'OK':
                                logger.error(f"Place Details API error: {details_data.get('status')}")
                                return {
                                    "error": f"Google Place Details API error: {details_data.get('status')}",
                                    "business_name": business_name
                                }
                            
                            result = details_data['result']
                            
                            # Extract and format business hours
                            hours = {}
                            if 'opening_hours' in result and 'periods' in result['opening_hours']:
                                days = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday']
                                for period in result['opening_hours']['periods']:
                                    day_index = period.get('open', {}).get('day', 0)
                                    if day_index is not None and 0 <= day_index < len(days):
                                        day = days[day_index]
                                        
                                        # Get opening and closing times
                                        open_time = period.get('open', {}).get('time', '')
                                        close_time = period.get('close', {}).get('time', '')
                                        
                                        # Format times for readability
                                        if open_time and len(open_time) == 4:
                                            open_time = f"{open_time[:2]}:{open_time[2:]} AM" if int(open_time[:2]) < 12 else f"{int(open_time[:2]) - 12 if int(open_time[:2]) > 12 else 12}:{open_time[2:]} PM"
                                        
                                        if close_time and len(close_time) == 4:
                                            close_time = f"{close_time[:2]}:{close_time[2:]} AM" if int(close_time[:2]) < 12 else f"{int(close_time[:2]) - 12 if int(close_time[:2]) > 12 else 12}:{close_time[2:]} PM"
                                        
                                        hours[day] = {
                                            "isOpen": True,
                                            "openTime": open_time,
                                            "closeTime": close_time
                                        }
                            
                            # Format photos - create URLs
                            photo_urls = []
                            if 'photos' in result:
                                for photo in result['photos'][:5]:  # Limit to 5 photos
                                    if 'photo_reference' in photo:
                                        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photoreference={photo['photo_reference']}&key={api_key}"
                                        photo_urls.append(photo_url)
                            
                            # Extract reviews
                            reviews = []
                            if 'reviews' in result:
                                for review in result['reviews'][:3]:  # Limit to 3 reviews
                                    reviews.append({
                                        "author": review.get('author_name', 'Anonymous'),
                                        "rating": review.get('rating', 0),
                                        "text": review.get('text', '')
                                    })
                            
                            # Extract services from types 
                            services = []
                            types = result.get('types', [])
                            for type_name in types:
                                # Convert type to a readable service name
                                service_name = type_name.replace('_', ' ').title()
                                services.append({
                                    "name": service_name,
                                    "description": f"Service offered by {result.get('name', business_name)}",
                                    "price": "Contact for pricing"
                                })
                            
                            # Build structured business data
                            gbp_data = {
                                "business_id": business_id,
                                "source": "gbp",
                                "name": result.get('name', business_name),
                                "formatted_address": result.get('formatted_address', ''),
                                "phone": result.get('formatted_phone_number', ''),
                                "website": result.get('website', ''),
                                "rating": result.get('rating', 0),
                                "reviews_count": result.get('user_ratings_total', 0),
                                "categories": [t.replace('_', ' ').capitalize() for t in result.get('types', [])],
                                "opening_hours": hours,
                                "reviews": reviews,
                                "photos": photo_urls,
                                "services": services
                            }
                            
                            # Store in MongoDB through the repository
                            await self.business_repo.save_gbp_data(business_id, gbp_data)
                            
                            # Also save relevant parts to the training repository
                            training_data = self._prepare_training_data(gbp_data)
                            await self.training_repo.save_training_data(business_id, training_data)
                            
                            logger.info(f"Successfully scraped GBP for business_id: {business_id}")
                            return gbp_data
                except aiohttp.ClientError as e:
                    logger.error(f"Network error connecting to Google Places API: {str(e)}")
                    return {
                        "error": f"Network error: {str(e)}",
                        "business_name": business_name
                    }
        except Exception as e:
            logger.error(f"Error scraping GBP for {business_name}: {str(e)}")
            return {"error": str(e), "business_name": business_name}
    
    def _prepare_training_data(self, gbp_data):
        """Prepare training data from GBP data"""
        training_data = {
            "source": "gbp",
            "business_name": gbp_data.get('name', ''),
            "address": gbp_data.get('formatted_address', ''),
            "phone": gbp_data.get('phone', ''),
            "website": gbp_data.get('website', ''),
            "rating": gbp_data.get('rating', 0),
            "categories": gbp_data.get('categories', []),
            "hours": gbp_data.get('opening_hours', {})
        }
        
        # Generate example Q&A pairs for training
        example_qa = []
        
        # Add business info questions
        example_qa.append({
            "question": "What is your business name?",
            "answer": f"Our business is {gbp_data.get('name', '')}."
        })
        
        example_qa.append({
            "question": "Where are you located?",
            "answer": f"We are located at {gbp_data.get('formatted_address', '')}."
        })
        
        example_qa.append({
            "question": "What's your phone number?",
            "answer": f"You can reach us at {gbp_data.get('phone', '')}."
        })
        
        # Add hours questions
        example_qa.append({
            "question": "What are your hours?",
            "answer": "Our hours are: " + json.dumps(gbp_data.get('opening_hours', {}))
        })
        
        # Add categories/services
        for category in gbp_data.get('categories', []):
            example_qa.append({
                "question": f"Do you provide {category} services?",
                "answer": f"Yes, we specialize in {category}."
            })
        
        # Add review-based questions
        if gbp_data.get('reviews'):
            review_texts = [r.get('text', '') for r in gbp_data.get('reviews', [])]
            combined_reviews = " ".join(review_texts)
            
            example_qa.append({
                "question": "What do customers say about you?",
                "answer": f"Our customers say: {combined_reviews}"
            })
            
            example_qa.append({
                "question": "What's your rating?",
                "answer": f"We have a {gbp_data.get('rating', 0)} star rating from {gbp_data.get('reviews_count', 0)} reviews on Google."
            })
            
        training_data["example_qa"] = example_qa
        
        return training_data
