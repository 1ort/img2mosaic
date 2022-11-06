# img2mosaic
Automatic1111' Stable Diffusion webui custom script to generate mosaics from images. The script cuts the image into tiles and processes each tile separately. The size of each tile is chosen randomly

## Installation & usage
Сlone or download this repo and put the `img2mosaic.py` file in a `/scripts` folder of your webui base dir.
After launching the interface, select img2mosaic from the list of scripts on the txt2img tab.

- The `Init image resize factor` slider will enlarge your image that many times before cutting it.
- Use the standard `Width` and `Height` sliders to set the minimum tile size after slicing. Due to the peculiarities of the slicing algorithm, each tile will be larger than the specified size, so do not be afraid of low values
- `Use -1 for seeds` determines whether the seeds for each picture will be different or not.
- If you specify a seed in the standard interface field, it will be used when cutting the image into tiles. Thus the shape of the mosaic will be the same across generations, even if `Use -1 for seeds` is set.
- Set `Tile border width` to 0 to completely disable tile borders

## Examples
![grid-0386](https://user-images.githubusercontent.com/83316072/200169739-23588d1f-f151-4e6e-b5c5-666c663fd605.jpg)
![grid-0384](https://user-images.githubusercontent.com/83316072/200169758-89d14276-3514-41ca-bdcc-a4e66c2383b0.jpg)
![grid-0382](https://user-images.githubusercontent.com/83316072/200169743-470b3c6e-fe16-4234-a7dc-392d2fcd9083.png)
![grid-0383](https://user-images.githubusercontent.com/83316072/200169771-3dccb227-7bca-4c19-819c-a685a2d3666f.jpg)

## Credits
The code of the algorithm for cutting and assembling the mosaic is written using the GPT-3 Code according to my instructions
