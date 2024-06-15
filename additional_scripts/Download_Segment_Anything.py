import os
import requests

# URL to the file containing dataset URLs
urls_file_url = 'https://scontent.ftlv1-1.fna.fbcdn.net/m1/v/t6/An8MNcSV8eixKBYJ2kyw6sfPh-J9U4tH2BV7uPzibNa0pu4uHi6fyXdlbADVO4nfvsWpTwR8B0usCARHTz33cBQNrC0kWZsD1MbBWjw.txt?ccb=10-5&oh=00_AYB1m9-DO5CjAyPxald2lmCh0xrYrER2Vn9yDXQR2mKrmA&oe=66945758&_nc_sid=0fdd51'

# Directory to save files
save_dir = '/media/flog/240gb/segment_anything/'

# Create the directory if it doesn't exist
if not os.path.exists(save_dir):
    os.makedirs(save_dir)


def download_file(url, save_path):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
            print(f'Successfully downloaded {url}')
        else:
            print(f'Failed to download {url}, Status code: {response.status_code}')
    except Exception as e:
        print(f'Error downloading {url}: {e}')


# Download the file containing the URLs
response = requests.get(urls_file_url)
if response.status_code == 200:
    lines = response.text.splitlines()

    # Download each file
    for line in lines:
        try:
            if '\t' in line:
                file_name, url = line.split('\t')
                save_path = os.path.join(save_dir, file_name)

                # Check if the file already exists
                if os.path.exists(save_path):
                    print(f'File {save_path} already exists, skipping download.')
                    continue

                if not url.startswith('http://') and not url.startswith('https://'):
                    url = 'https://' + url
                print("downloading ",url, save_path,"\n to ",save_path)
                download_file(url, save_path)
            else:
                print(f"Skipping invalid line: {line}")
        except Exception as e:
            print(f"Error processing line '{line}': {e}")
else:
    print(f'Failed to download the URLs file, Status code: {response.status_code}')