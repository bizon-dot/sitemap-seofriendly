import aiohttp
import asyncio
import xml.etree.ElementTree as ET
import urllib.parse
import xml.dom.minidom 
import chardet
from colorama import Fore, Back, Style
from bs4 import BeautifulSoup

async def get_links(session, url, domains, visited_links):
    async with session.get(url) as response:
        content = await response.read()
        encoding = chardet.detect(content)['encoding']
        html = content.decode(encoding)
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        for link in soup.find_all('a'):
            href = link.get('href')
            if href is not None and href.startswith('http'):
                parsed_url = urllib.parse.urlparse(href)
                if parsed_url.netloc in domains and href not in visited_links:
                    links.add(href)
        return links

async def main():
    urls = []
    while True:
        url = input(Fore.RED + "Inserisci un URL (o lascia vuoto per uscire): " + Style.RESET_ALL)
        if url:
            urls.append(url)
        else:
            break
    
    # Estrai i domini degli URL iniziali
    domains = set()
    for url in urls:
        parsed_url = urllib.parse.urlparse(url)
        domains.add(parsed_url.netloc)

    sitemap = ET.Element('urlset', xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    async with aiohttp.ClientSession() as session:
        tasks = [get_links(session, url, domains, set(urls)) for url in urls]
        results = await asyncio.gather(*tasks)
        visited_links = set()
        for link_list in results:
            for link in link_list:
                visited_links.add(link)
                url = ET.SubElement(sitemap, 'url')
                ET.SubElement(url, 'loc').text = link
                ET.SubElement(url, 'lastmod').text = '2023-03-15T00:00:00+00:00'
                ET.SubElement(url, 'changefreq').text = 'weekly'
                ET.SubElement(url, 'priority').text = '0.5'

    #ET.ElementTree(sitemap).write('sitemap.xml', encoding='utf-8', xml_declaration=True)
    # Creare un'istanza di un minidom e ottenere l'output formattato
    xmlstr = xml.dom.minidom.parseString(ET.tostring(sitemap)).toprettyxml()

    # Scrivere il file di sitemap XML
    with open("sitemap.xml", "w") as f:
        f.write(xmlstr)

if __name__ == '__main__':
    asyncio.run(main())
