import os
import requests
from bs4 import BeautifulSoup
import threading
import tkinter as tk
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import shutil
import glob


def scrape_images():
    # Get the URL entered by the user
    url = url_entry.get()

    # Send a GET request to the webpage and get the HTML content
    console.insert('end', f'发送请求...\n')
    response = requests.get(url)
    html_content = response.content

    # Parse the HTML content using BeautifulSoup
    console.insert('end', '获取网页信息...\n')
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find all the image tags in the HTML content that have the 'data-src' attribute
    image_tags = soup.find_all('img', attrs={'data-src': True})

    # Create a directory to store the downloaded images
    if not os.path.exists('images'):
        os.makedirs('images')
    else:
        shutil.rmtree('images')
        os.makedirs('images')

    # Download each image and save it to the directory
    console.insert('end', f'总共 {len(image_tags)} 张图片等待下载...\n')
    for i, image_tag in enumerate(image_tags):
        image_url = image_tag['data-src']
        if image_url.startswith('//'):
            image_url = 'https:' + image_url
        image_response = requests.get(image_url)
        with open(f'images/image_{i+1}.jpg', 'wb') as f:
            f.write(image_response.content)
        console.insert('end', f'保存 image_{i+1}.jpg\n')
        console.see('end')
    console.insert('end', '所有图片下载完成！\n')
    console.see('end')

def scrape_images_thread():
    # Create a new thread to run the scrape_images function
    console.delete('1.0', tk.END)

    if len(url_entry.get()) > 0:
        t = threading.Thread(target=scrape_images)
        t.start()
    else:
        console.insert('end', '请先输入目标网址..')
        console.see('end')

def restore_images():
    console.insert('end', f'开始批量增强...\n')
    console.see('end')

    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1920, 1080)

    # Load the face restoration demo webpage
    driver.get('https://arc.tencent.com/zh/ai-demos/faceRestoration')
    wait = WebDriverWait(driver, 60)
    
    # Process each image and download the restored image
    console.insert('end', f'共 {len(os.listdir("images"))} 张图片待增强...\n')    
    console.see('end')
    for i, image_path in enumerate(os.listdir('images')):
        console.insert('end', f'处理 {image_path}...\n')
        console.see('end') # Auto-scroll to the end of the console text widget

        image_file = os.path.abspath(os.path.join('images', image_path))

        # Error handle
        num_retries = 3
        retry_count = 0
        while retry_count < num_retries:
            try:
                time.sleep(3)
                file_upload_input = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'uploadInput')))
                file_upload_input.clear()
                file_upload_input.send_keys(image_file)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.el-message--success'))) #el-image__error
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.newimgUrl img')))        
                download_link = driver.find_element(By.CSS_SELECTOR, '.newimgUrl img')
                download_url = download_link.get_attribute('src')
                download_response = requests.get(download_url)
                with open(f"images/{image_path.split('.')[0]}_修复后.jpg", 'wb') as f:
                    f.write(download_response.content)
                break
            except Exception as e:
                console.insert('end', f'增强 {image_path} 出错!\n 重试第{retry_count+1}次')
                console.see('end')
                retry_count += 1
                driver.refresh()
        else:
            console.insert('end',f"增强 {image_path} 失败，需手动上传.")
            console.see('end')

    console.insert('end', '所有图片增强完成!\n')
    console.see('end')
    driver.quit()

    files = [f for f in os.listdir('images') if not f.endswith("_修复后.jpg")]
    for file in files:
        os.remove(os.path.join('images', file))
                            
def restore_images_thread():
    jpg_count = len(glob.glob("images/*.jpg"))

    if jpg_count > 0:
        t = threading.Thread(target=restore_images)
        t.start()
    else:
        console.insert('end', '还没有下载的图片可以增强!')
        console.see('end')

# Create the GUI window
window = tk.Tk()
window.title('网页图片资料下载增强')

left_frame = tk.Frame(window)
left_frame.pack(side=tk.LEFT, padx=5, pady=5)

# Create the Scrape button
scrape_button = tk.Button(left_frame, text='开始处理', command=scrape_images_thread)
scrape_button.pack(side=tk.TOP, padx=5, pady=5, anchor=tk.N)

# Create the Restore Images button
restore_button = tk.Button(left_frame, text='图片强化', command=restore_images_thread)
restore_button.pack(side=tk.TOP, padx=5, pady=5)

# Create the URL label and entry
url_label = tk.Label(window, text='输入目标网址:')
url_label.pack(side=tk.TOP, anchor=tk.W)
url_entry = tk.Entry(window)
url_entry.pack(side=tk.TOP, fill=tk.X, expand=True)

# Create the console text widget and scrollbar
console_label = tk.Label(window, text='进度日志:')
console_label.pack(side=tk.TOP, anchor=tk.W)
console_scrollbar = tk.Scrollbar(window)
console_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
console = tk.Text(window, wrap=tk.WORD, yscrollcommand=console_scrollbar.set)
console.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
console_scrollbar.config(command=console.yview)

# Run the GUI loop
window.mainloop()

# restore_images()
