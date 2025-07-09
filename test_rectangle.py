import cv2
import os
from datetime import datetime

def draw_rectangle_and_crop(image_path, coords, output_root):
    """
    在图片上绘制矩形框，并裁剪出矩形框区域保存
    :param image_path: 图片的文件路径
    :param coords: 四个坐标，元组形式 (x1, y1, x2, y2)
    :param output_root: 保存目录（文件夹路径）
    :return: 返回裁剪图像保存路径
    """
    # 读取图片
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"无法读取图片: {image_path}")

    # 提取四个坐标
    x1, y1, x2, y2 = coords

    # 绘制矩形框（颜色为红色，BGR: (0,0,255)，线宽2）
    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)

    # 裁剪出矩形框部分
    cropped_img = img[y1:y2, x1:x2]

    # 获取文件名和扩展名
    filename, ext = os.path.splitext(os.path.basename(image_path))

    # 获取当前时间戳
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

    # 生成带时间戳的文件名
    boxed_img_name = f"{timestamp}_boxed_{filename}{ext}"
    cropped_img_name = f"{timestamp}_cropped_{filename}{ext}"

    # 确保保存目录存在
    os.makedirs(output_root, exist_ok=True)

    # 定义保存路径
    box_img_path = os.path.join(output_root, boxed_img_name)
    cropped_img_path = os.path.join(output_root, cropped_img_name)

    # 保存图片
    cv2.imwrite(box_img_path, img)
    cv2.imwrite(cropped_img_path, cropped_img)

    return box_img_path, cropped_img_path


# 示例调用
if __name__ == '__main__':
    image_path = r"D:\goodwe_test\Machine_backup\20250626163340\NGPartImage\1@259.jpg"
    coords = (100, 160, 200, 220)
    output_root = r"D:\goodwe_test"  # 输出文件夹路径

    output, cropped_output = draw_rectangle_and_crop(image_path, coords, output_root)

    print(f"保存的带框图像路径：{output}")
    print(f"裁剪后的图像路径：{cropped_output}")
