from bs4 import BeautifulSoup
import httpx
import asyncio

async def get_page_title(url: str) -> str:
    """
    Visits a URL and extracts the <title> text.
    Returns specific text if it fails, so the AI still has something to work with.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; MyShortener/1.0)"
    }
    
    try:
        # asynchrounus requests to urls to handle scale times load
        async with httpx.AsyncClient(follow_redirects=True, timeout=5.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status() # Check for 404 errors

            # Parse HTML
            soup = BeautifulSoup(response.text,'html.parser')
            # print(soup.contents)
            # Return the title if it exists, or a fallback
            if soup.title and soup.title.string:
                return soup.title.string.strip()
            
            return "Website content" # Fallback if no title found

    except Exception as e:
        print(f"Scraping failed: {e}")
        return "General website" # Fallback if scraping fails


# print(get_page_title('https://supabase.com/dashboard/project/ynxgnwdlumzcnzfobwfi/database/settings#connection-pooling'))
# asyncio.run(get_page_title("https://supabase.com/dashboard/project/ynxgnwdlumzcnzfobwfi"))