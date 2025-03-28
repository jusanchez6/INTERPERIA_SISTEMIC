from roboflow import Roboflow
import random


rf = Roboflow(api_key="pxBbr78gPQ3Bv0NKTL7i")
# List workspaces to ensure the key works
workspaces = rf.workspace("robocup-hdybz")
print(workspaces)

project = rf.workspace("robocup-hdybz").project("guns-project")

version = project.version(1)

dataset = version.download("yolov8")

# Get a list of image filenames in your dataset
image_list = dataset.images()

# Select a random image from the list
random_image = random.choice(image_list)

# Get the image URL
image_url = random_image['url']

# Print the image URL
print(f"Random image URL: {image_url}")