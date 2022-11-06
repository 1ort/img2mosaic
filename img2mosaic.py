import math

import modules.scripts as scripts
import gradio as gr
from PIL import Image, ImageDraw

from modules import processing, images, devices
from modules.processing import Processed
from modules.shared import state

import random
from collections import namedtuple
from PIL import Image, ImageDraw

Tile = namedtuple('Tile', ['x_pos', 'y_pos', 'width', 'height'])
ImageTile = namedtuple('ImageTile', ['tile', 'image'])
LANCZOS = (Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.LANCZOS)

#Check if tile is vertical or horizontal or square. returns 0, 1 or 2
def check_tile_type(tile) -> int:
    if tile.width == tile.height:
        return 'square'
    elif tile.width > tile.height:
        return 'vertical'
    else:
        return 'horizontal'

#split tile into two separated tiles. The separation should be across the long side. If tile is a square, choose side randomly Each side of them must be divisible by divider and be bigger or equal than min_tile_size. 
def split_tile(tile, divider, min_tile_size):
    if check_tile_type(tile) == 'square':
        if random.random() > 0.5:
            return split_tile_vertical(tile, divider, min_tile_size)
        else:
            return split_tile_horizontal(tile, divider, min_tile_size)
    elif check_tile_type(tile) == 'vertical':
        return split_tile_vertical(tile, divider, min_tile_size)
    else:
        return split_tile_horizontal(tile, divider, min_tile_size)

#split tile into two separated tiles. The separation should be across the long side. Each side of them must be divisible by divider and be bigger or equal than min_tile_size. 
def split_tile_vertical(tile, divider, min_tile_size):
    if tile.width < min_tile_size[0] * 2:
        return None
    else:
        split_point = random.randint(min_tile_size[0], tile.width - min_tile_size[0])
        if split_point % divider != 0:
            split_point = split_point - split_point % divider
        return [Tile(tile.x_pos, tile.y_pos, split_point, tile.height), Tile(tile.x_pos + split_point, tile.y_pos, tile.width - split_point, tile.height)]

#split tile into two separated tiles. The separation should be across the long side. Each side of them must be divisible by divider and be bigger or equal than min_tile_size. 
def split_tile_horizontal(tile, divider, min_tile_size):
    if tile.height < min_tile_size[1] * 2:
        return None
    else:
        split_point = random.randint(min_tile_size[1], tile.height - min_tile_size[1])
        if split_point % divider != 0:
            split_point = split_point - split_point % divider
        return [Tile(tile.x_pos, tile.y_pos, tile.width, split_point), Tile(tile.x_pos, tile.y_pos + split_point, tile.width, tile.height - split_point)]

#sorts the tiles in the list by perimeter length
sort_func = lambda x: x.width + x.height

#apply split_tile to the biggest tile in the list recursively
def split_into_tiles(init_tile, divider, min_tile_size):
    assert min_tile_size[0] >= divider and min_tile_size[1] >= divider
    tiles = [init_tile]
    while True:
        tiles.sort(key=sort_func, reverse=True)
        new_tiles = split_tile(tiles[0], divider, min_tile_size)
        if new_tiles is None:
            break
        tiles.pop(0)
        tiles.extend(new_tiles)
    return tiles

#split PIL image into tiles
def split_image(image, divider, min_tile_size):
    tiles = split_into_tiles(Tile(0, 0, image.width, image.height), divider, min_tile_size)
    image_tiles = []
    for tile in tiles:
        image_tiles.append(ImageTile(tile, image.crop((tile.x_pos, tile.y_pos, tile.x_pos + tile.width, tile.y_pos + tile.height))))
    return image_tiles


#Draw a border of a certain color and width on each ImageTile from the list
def draw_borders(image_tiles, border_width, border_color):
    for image_tile in image_tiles:
        draw = ImageDraw.Draw(image_tile.image)
        draw.rectangle([(0, 0), (image_tile.image.width - 1, image_tile.image.height - 1)], outline=border_color, width=border_width)

#merge tiles from the list into one image
def merge_tiles(image_tiles, image_size):
    image = Image.new('RGB', image_size, color='black')
    for image_tile in image_tiles:
        image.paste(image_tile.image, (image_tile.tile.x_pos, image_tile.tile.y_pos))
    return image

#split image into tiles, draw borders on them and merge them back
def split_draw_borders_and_merge(image, divider, min_tile_size, border_width, border_color):
    image_tiles = split_image(image, divider, min_tile_size)
    draw_borders(image_tiles, border_width, border_color)
    img = merge_tiles(image_tiles, image.size)
    return img

#check if PIL image dimensions are divisible by N
def is_divisible_by_N(img, N):
    return img.size[0] % N == 0 and img.size[1] % N == 0

#Cut out a piece from the center of the picture so that its dimensions are divisible by N
def cut_out_center(img, N):
    width, height = img.size
    new_width = (width // N) * N
    new_height = (height // N) * N
    left = (width - new_width) // 2
    top = (height - new_height) // 2
    right = (width + new_width) // 2
    bottom = (height + new_height) // 2
    return img.crop((left, top, right, bottom))

#check if divisible and cut if needed
def check_and_cut(img, N):
    if is_divisible_by_N(img, N):
        return img
    else:
        return cut_out_center(img, N)

class Script(scripts.Script):
    def title(self):
        return "img2mosaic"

    def show(self, is_img2img):
        return is_img2img

    def ui(self, is_img2img):
        upscale_factor = gr.Slider(minimum=1, maximum=10, step=1,
                               label='Init image resize factor. Use the standard Width and Height sliders to adjust the minimum tile size', value=1, visible=True)
        use_random_seeds = gr.Checkbox(value=True, label='Use -1 for seeds', visible=True)
        save_tiles = gr.Checkbox(value=False, label='Save separate tiles', visible=True)

        tile_border_width = gr.Slider(minimum=0, maximum=256, step=1,
                                        label='Tile border width', value=0, visible=True)
        tile_border_color = gr.ColorPicker(label='Tile border color', visible=True)
        return [upscale_factor, tile_border_width, tile_border_color, use_random_seeds, save_tiles]


    def run(self, p, upscale_factor, tile_border_width, tile_border_color, use_random_seeds, save_tiles):
        p.do_not_save_samples = not save_tiles
        if use_random_seeds:
            p.seed = -1
        else:
            processing.fix_seed(p)

        if p.seed != -1:
            random.seed(p.seed)

        initial_info = None
        seed = p.seed

        divisor = 64
        minimal_tile_width = p.width
        minimal_tile_height = p.height

        init_img = p.init_images[0]
        if upscale_factor > 1:
            w = init_img.width * upscale_factor
            h = init_img.height * upscale_factor
            init_img = init_img.resize((w, h), resample=LANCZOS)

        img = check_and_cut(init_img, divisor)
        devices.torch_gc()

        min_tile_size = (minimal_tile_width, minimal_tile_height)

        all_tiles = split_image(img, divisor, min_tile_size)

        p.batch_size = 1
        batch_count = math.ceil(len(all_tiles))
        state.job_count = batch_count

        print(
            f"img2mosaic will process a total of {len(all_tiles)} tile images in a total of {state.job_count} batches.")

        result_images = []

        for i in range(batch_count):
            p.init_images = [all_tiles[i].image]
            p.width = all_tiles[i].image.width
            p.height = all_tiles[i].image.height
            state.job = f"Batch {i + 1 * batch_count} out of {state.job_count}"
            try:
                processed = processing.process_images(p)
                if initial_info is None:
                    initial_info = processed.info
                all_tiles[i] = ImageTile(
                    Tile(
                        all_tiles[i].tile.x_pos,
                        all_tiles[i].tile.y_pos,
                        all_tiles[i].tile.width,
                        all_tiles[i].tile.height,
                    ),
                    processed.images[0])
            except Exception as e:
                print(e)
                print(all_tiles[i].tile)
                all_tiles[i] = ImageTile(
                    Tile(
                        all_tiles[i].tile.x_pos,
                        all_tiles[i].tile.y_pos,
                        all_tiles[i].tile.width,
                        all_tiles[i].tile.height,
                    ),
                Image.new("RGB", (all_tiles[i].tile.width, all_tiles[i].tile.height), color=tile_border_color))

    
        draw_borders(all_tiles, tile_border_width, tile_border_color)
        combined_image = merge_tiles(all_tiles, (img.width, img.height))

        result_images.append(combined_image)
        images.save_image(combined_image, 'outputs/img2img-grids', basename='grid')
        processed = Processed(p, result_images, seed, initial_info)

        return processed
