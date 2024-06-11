import requests
import re
from bs4 import BeautifulSoup

URLS = ['https://scale.com/', 'https://www.deel.com/', 'https://webflow.com/']
DEEL_NAME_PATTERN = re.compile(r'/([^/_]+(?:_[^/_]+)*)_\w+\.svg$')


def get_customer_name(customer_url, image_url):
  """Extracts and formats the company name from the image URL."""
  if customer_url == 'https://www.deel.com/':
    match = DEEL_NAME_PATTERN.search(image_url)
    if match: return match.group(1).replace('_', ' ')
  
  return image_url


def parse_customers_page(content, prefix=''):
  """Parses the customers page to extract logos."""
  images = content.find_all('img')
  customer_logos = {}

  for img in images:
    class_text = ' '.join(img.get('class', [])).lower()
    if any(keyword in class_text for keyword in ['invert', 'ρi ρoigxs', 'customers_logos']):
      alt_text = img.get('alt', 'Unknown').strip()
      customer_logos[alt_text] = prefix + img['src']
  
  return list(customer_logos.items())


def parse_landing_page(url, content):
  """Parses the landing page to extract logos."""
  divs = content.find_all('div')
  customer_logos = {}

  for div in divs:
    class_text = ' '.join(div.get('class', [])).lower()
    images = div.find_all('img')
    
    if len(images) > 5 and not div.get_text(strip=True):
      for img in images:
        src = img.get('src')
        if src:
          company_name = get_customer_name(url, src)
          customer_logos[company_name] = src
  
  return list(customer_logos.items())


def get_customer_logos(url):
  """Fetches and parses the customer logos from the given URL."""
  if url == 'https://webflow.com/':
    response = requests.get('https://webflow.com/customers?page=4')
    return parse_customers_page(BeautifulSoup(response.content, 'html.parser')) if response.status_code == 200 else []
  elif url == 'https://scale.com/':
    response = requests.get(url + 'customers')
    return parse_customers_page(BeautifulSoup(response.content, 'html.parser'), 'https://scale.com') if response.status_code == 200 else []
  else:
    response = requests.get(url)
    return parse_landing_page(url, BeautifulSoup(response.content, 'html.parser')) if response.status_code == 200 else []


def main():
  print('Scraping client logos...')
  
  all_customer_logos = {}

  for url in URLS:
    logos = get_customer_logos(url)
    all_customer_logos[url] = logos

  with open('customers.txt', 'w') as f:
    for url, logos in all_customer_logos.items():
      f.write(f"\n\nCustomer logos from {url}:\n\n")
      for company, logo_url in logos:
        f.write(f"{company} ({logo_url})\n")


if __name__=="__main__": 
  main() 
