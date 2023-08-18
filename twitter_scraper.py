from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import time
import db
from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv("TWITTER_USERNAME")
PASSWORD = os.getenv("TWITTER_PASSWORD")

print(f"{USERNAME}, {PASSWORD}")


def convert_to_int(text):
    # Remove commas
    text = text.replace(",", "")

    # Identify suffixes and corresponding multipliers
    suffixes = {"K": 1000, "M": 1000000}

    result = 0
    try:
        # Check if the last character is a suffix
        if text[-1] in suffixes:
            # Extract the numeric portion and the suffix
            numeric_part = float(text[:-1])
            suffix = text[-1]

            # Multiply the numeric portion by the multiplier
            multiplier = suffixes[suffix]
            result = int(numeric_part * multiplier)
        else:
            # No suffix, directly convert the text to integer
            result = int(text)
    except:
        pass

    return result


def scrape_user_data(search_name):
    print("scraper_user_data function being called")
    load_dotenv()

    USERNAME = os.getenv("TWITTER_USERNAME")
    PASSWORD = os.getenv("TWITTER_PASSWORD")

    # Create a new instance of the Chrome driver
    # options = Options()
    # options.add_argument('--headless')  # Comment this line if you want to see the browser window
    # options.add_argument("--start-maximized")

    # Initialize Chrome driver using webdriver_manager
    # driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    service = ChromeService(
        executable_path="/home/shupohan/Downloads/chromedriver-linux64"
    )
    driver = webdriver.Chrome(service=service)

    # Navigate to a specific URL
    # url = "https://twitter.com/"
    url = "https://twitter.com/i/flow/login"
    driver.get(url)

    time.sleep(5)
    search_bar = driver.find_element(
        By.XPATH,
        "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input",
    )
    search_bar.send_keys(USERNAME)
    time.sleep(5)
    # Rest of your web scraping code here...

    label_element = driver.find_element(
        By.XPATH,
        "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]",
    )
    label_element.click()
    time.sleep(5)

    password_bar = driver.find_element(
        By.XPATH,
        "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input",
    )
    password_bar.send_keys(PASSWORD)
    time.sleep(10)

    password_button = driver.find_element(
        By.XPATH,
        "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div",
    )
    password_button.click()
    time.sleep(5)

    search_button_after_login = driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div/div/div[2]/header/div/div/div/div[1]/div[2]/nav/a[2]/div",
    )
    search_button_after_login.click()
    time.sleep(5)

    serach_input_text_area = driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[1]/div[1]/div[1]/div/div/div/div/div[1]/div[2]/div/div/div/form/div[1]/div/div/div/label/div[2]/div/input",
    )
    serach_input_text_area.send_keys(search_name)
    time.sleep(5)

    search_input_start_button = driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[1]/div[1]/div[1]/div/div/div/div/div[1]/div[2]/div/div/div/form/div[2]/div/div[4]/div",
    )
    search_input_start_button.click()
    time.sleep(5)

    count = 0

    user = db.user()
    tweet = db.tweet()

    tweets_tag = driver.find_element(
        By.XPATH,
        "/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[1]/div[1]/div/div/div/div/div/div[2]/div/div",
    )
    print(f"total tweets = {tweets_tag.text}")

    try:
        followers_tag = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div[5]/div[2]/a/span[1]/span",
        )
    except:
        followers_tag = driver.find_element(
            By.XPATH,
            "/html/body/div[1]/div/div/div[2]/main/div/div/div/div/div/div[3]/div/div/div/div/div[4]/div[2]/a/span[1]/span",
        )
    print(f"total followers = {followers_tag.text}")
    followers = convert_to_int(followers_tag.text)

    user.insert(search_name[1:], followers)
    user_id = tweet.get_user_id(search_name[1:])

    while True:
        # Scroll to the bottom of the page
        # driver.find_element_by_tag_name('body').send_keys(Keys.END)

        html_code = driver.page_source
        soup = BeautifulSoup(html_code, "html.parser")

        article_tags = soup.find_all("article")

        # Iterate over the <article> tags
        for article in article_tags:
            replies = None
            retweets = None
            likes = None
            views = None
            event_time = None

            # event_time = soup.find('time')['datetime']
            if article.find("time") is None:
                break
            event_time = article.find("time").attrs["datetime"]

            # Get the text inside the <time> tag
            # text_value = soup.find('time').get_text()
            text_value = article.find("time").get_text()

            # Find all <span> elements with the specific class name inside each <article> tag
            span_elements = article.find_all(
                "span",
                class_="css-901oao css-16my406 r-poiln3 r-n6v787 r-1cwl3u0 r-1k6nrdp r-1e081e0 r-qvutc0",
            )

            # Iterate over the <span> elements
            for order, span_element in enumerate(span_elements):
                # Extract the text value
                text_value = span_element.get_text()
                # print(f"order = {order} ==> text_value = {text_value}", end=' ')
                print()
                if order == 0:
                    replies = convert_to_int(text_value)
                    # print(f"replies = {replies}")
                elif order == 1:
                    retweets = convert_to_int(text_value)
                    # print(f"retweets = {retweets}")
                elif order == 2:
                    likes = convert_to_int(text_value)
                    # print(f"likes = {likes}")
                else:
                    views = convert_to_int(text_value)
                    # print(f"views = {views}")
            # print("=======================================================================")
            tweet.insert(user_id, replies, retweets, likes, views, event_time)

        driver.find_element(By.XPATH, "/html/body").send_keys(Keys.END)

        # Wait for some time for new content to load
        time.sleep(2)  # Adjust the sleep duration as needed

        # Check if reaching the bottom of the page
        # You can modify this condition based on your specific webpage
        if driver.execute_script(
            "return window.innerHeight + window.pageYOffset >= document.body.scrollHeight"
        ):
            # if count > 3:
            break  # Stop scrolling if reached the bottom
        count += 1
    time.sleep(10)

    driver.quit()


# scrape_user_data("@Roger Federer")
