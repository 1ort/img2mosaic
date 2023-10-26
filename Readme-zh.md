# img2mosaic
[Automatic1111' Stable Diffusion webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui) 生成马赛克图片的脚本. 这个脚本将图片按随机大小来切成块，并分别处理每个块。
![изображение](https://user-images.githubusercontent.com/83316072/200170437-160603de-e507-454b-8b68-69868255d7c5.png)
![изображение](https://user-images.githubusercontent.com/83316072/200170569-0e7131e4-1da8-4caf-9cd9-5b785c9d21b0.png)


## 安装 
用git克隆这个仓库或者是下载这个库的zip包， 然后把文件 `img2mosaic.py`放到你webUI的 `/scripts` 的目录.然后在设置里面选择“重新加载自定义脚本主体”（英语原文是"Reload custom script bodies (No ui updates, No restart)）
![图片](https://user-images.githubusercontent.com/25313785/201024105-72c36b67-bc30-4f2f-b28f-5c9eabc733ce.png)
## 使用方法


- The `Init image resize factor` 滑块将在剪切图像之前将图像放大很多倍。
- 使用标准的`宽度` 和`高度`滑块设置切片后的最小平铺大小。由于切片算法的特殊性，每个块都将大于指定的大小，所以不用害怕设置的太低。
- `Use -1 for seeds` 勾选就会使得每个图片的种子是否不同。
- 如果在标准界面字段中指定种子，则将在将图像剪切为平铺时使用该种子，哪怕你勾选了 `Use -1 for seeds` 。
-  `Tile border width` 设置为0以完全禁用平铺边框

## 示例
![grid-0386](https://user-images.githubusercontent.com/83316072/200169739-23588d1f-f151-4e6e-b5c5-666c663fd605.jpg)
![grid-0384](https://user-images.githubusercontent.com/83316072/200169758-89d14276-3514-41ca-bdcc-a4e66c2383b0.jpg)
![grid-0382](https://user-images.githubusercontent.com/83316072/200169743-470b3c6e-fe16-4234-a7dc-392d2fcd9083.png)
![grid-0383](https://user-images.githubusercontent.com/83316072/200169771-3dccb227-7bca-4c19-819c-a685a2d3666f.jpg)

## Credits
切割和组装马赛克的方法代码是根据我的指示使用GPT-3 Codex编写。
