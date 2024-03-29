import numpy as np
import matplotlib.pyplot as plt
import scipy.ndimage
from PIL import Image
import sys
from numba import njit

# [-- Custom figure plotting with labels
fig = plt.figure(figsize=(16, 8))
def plot(img, index, show_text=True, cmap="coolwarm"):
    global fig
    ax = fig.add_subplot(2, 4, index)
    im = ax.imshow(img, cmap=cmap)
    if show_text:
        for (j,i),label in np.ndenumerate(img):
            ax.text(i,j,label,ha='center',va='center', color='limegreen')
            ax.text(i,j,label,ha='center',va='center', color='limegreen')
    ax.axis('off')
    return ax
# --]

@njit
def evaluate_parabolla(height, px, x):
    return (px-x)*(px-x)+height

@njit
def compute_rows(img):
    new_img = np.ones_like(img)
    rows, cols = img.shape
    for y in range(0, rows): # for each row
        for x in range(0, cols): # for each cell
            sdf_min = img[y,x]
            for px in range(0, cols): # for each parabolla on this row
                pheight = img[y,px]
                sdf_min = min(sdf_min, evaluate_parabolla(pheight, px, x))
            new_img[y,x] = sdf_min
    return new_img

@njit
def compute_euclidian_distance(img):
    img = compute_rows(img)
    img = img.transpose()
    img = compute_rows(img)
    img = img.transpose()
    return img


image = Image.open(sys.argv[1])
image_bw = image.convert("L")

img = np.array(image_bw, np.float32) # [0., 255.] f32
img = np.where(img < 128, 1.0, 0.0)

# plt.imshow(img)
# plt.show()

def edt_encode(img):
    img = img.copy()
    img[img == 0] = np.inf
    img[img == 1] = 0
    return img

img_positive = edt_encode(img)
img_negative = edt_encode(1 - img)

edt_positive = compute_euclidian_distance(img_positive)
edt_negative = compute_euclidian_distance(img_negative)

# NOTE: Data would normally be stored as "squared" integers and normalised as floats
sdf = np.sqrt(edt_positive) - np.sqrt(edt_negative)

biggest_dim = max(np.amax(sdf), abs(np.amin(sdf)))
sdf_gray = sdf / biggest_dim # remap to [-1, 1] range
sdf_gray = (sdf_gray / 2.0) + 0.5 # remap to [0, 1]  range
sdf_gray = (sdf_gray * 255.0).astype(np.uint8)  # Convert to grayscale [0, 255]

# Save
im = Image.fromarray(sdf_gray)
import os
pre, ext = os.path.splitext(sys.argv[1])
im.save(f"{pre}-sdf.png")


ax = plt.subplot(1,1,1)
ax.imshow(sdf_gray, cmap="gray")
ε = 1
ax.contourf(sdf_gray, [255-128-ε, 255-128+ε], colors=["red"])
ax.set_title('Grayscale /w bilinear contour y=128')

plt.tight_layout()
plt.show()
