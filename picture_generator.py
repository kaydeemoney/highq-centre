import requests
import os

# List of filenames
profile_pics = [
    "49cbc845-260b-4fc3-b7ec-db306779eab3.jpg",
    "74f59b8b-9b65-41b9-bc0e-6f3ad92b8526.jpg",
    "b624f88d-1f92-4e58-bad0-8d7b5ac163f7.jpg",
    "ab933b59-90ff-48d3-b4f9-82c22a455ac6.jpg",
    "d03217a5-4e6e-4402-a74d-e1f6263c8c75.jpg",
    "e3d47c98-003a-4d8e-9f66-6b8ed90fcdf4.jpg",
    "933e5f88-3500-4f9f-bac1-b167a2d8581b.jpg",
    "b502b957-dce2-4b13-a828-568b98d8a21a.jpg",
    "a90d4556-60e9-4f62-b180-5b93b3c5f567.jpg",
    "915e4b08-c8be-4f9d-a33b-d56e7f622b28.jpg",
    "79cbca85-1542-4024-913b-49845bd228ad.jpg",
    "4d1b32bf-53ed-40cf-a58b-c6eb47c4e946.jpg",
    "1f56bcb7-d2b9-47a9-82cf-1f12f71a98c6.jpg",
    "a4a279be-cb1d-42bb-8a7c-4590bc3886b9.jpg",
    "d4e14c44-75e0-4c4e-a6db-1b08d6c7fd4d.jpg",
    "46f8d28f-bfc2-4f59-b5c6-1e30990ecb42.jpg",
    "da3bcb56-d89a-42e0-9b9e-d9dfb23b6e85.jpg",
    "2204f0d3-6745-42d8-87bb-cbe7fcf9e051.jpg",
    "27639b23-04fc-44b7-9869-4fc4d6483786.jpg",
    "ed97fd9e-bd92-423d-b09c-3fbaed1b8ecf.jpg",
    "f33f86f0-d6ab-4680-b0f5-3bc9a937c7b2.jpg",
    "4ab544d2-bdcb-460d-bbb6-e098f7f33228.jpg",
    "4a5f5862-bdfa-47ac-b456-bfdd622dbd89.jpg",
    "347c5f23-8f73-4a6e-b634-80b477bded84.jpg"
]

# Ensure the directory exists
output_dir = "profile_pics"
os.makedirs(output_dir, exist_ok=True)

# Download images and save them with specified names
for index, pic_name in enumerate(profile_pics, start=1):
    image_url = f"https://picsum.photos/200/200?random={index}"
    
    try:
        response = requests.get(image_url)  # Fetch the image
        
        if response.status_code == 200:
            file_path = os.path.join(output_dir, pic_name)
            with open(file_path, "wb") as img_file:
                img_file.write(response.content)
            print(f"Saved: {file_path}")
        else:
            print(f"Failed to download image for {pic_name} (Status: {response.status_code})")
    
    except requests.RequestException as e:
        print(f"Error downloading {pic_name}: {e}")

print("Download complete!")
