from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint, jsonify
import os
import pyodbc
import time
from datetime import datetime
from PIL import Image
import jieba
from jieba import analyse
import torch
import torchvision
from torchvision import transforms
import numpy as np
import cv2

from db_config import config

def allowed_imgformat(img_name):
    allowed_format = ['png', 'jpg', 'gif', 'zip']
    return '.' in img_name and img_name.rsplit('.', 1)[1].lower() in allowed_format

def unique_imgname():
    return str(int(time.time()))

def get_image_size(img_path):
    with Image.open(img_path) as img:
        width, height = img.size
    return width, height

#蓝图
upload_bp = Blueprint('upload', __name__)

# 添加图片分类相关的代码
class ImageClassifier:
    def __init__(self):
        try:
            print("\n正在初始化MobileNetV3模型...")
            # 加载预训练的MobileNetV3
            self.model = torchvision.models.detection.fasterrcnn_mobilenet_v3_large_320_fpn(pretrained=True)
            self.model.eval()
            
            # 设置图像预处理
            self.transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])
            
            # COCO数据集类别映射
            self.categories = {
                1: '人',
                2: '自行车',
                3: '汽车',
                4: '摩托车',
                5: '飞机',
                6: '公交车',
                7: '火车',
                8: '卡车',
                9: '船',
                10: '交通灯',
                11: '消防栓',
                13: '停车标志',
                14: '停车计时器',
                15: '长椅',
                16: '鸟',
                17: '猫',
                18: '狗',
                19: '马',
                20: '羊',
                21: '牛',
                22: '大象',
                23: '熊',
                24: '斑马',
                25: '长颈鹿',
                27: '背包',
                28: '雨伞',
                31: '手提包',
                32: '领带',
                33: '行李箱',
                34: '飞盘',
                35: '滑雪板',
                36: '雪板',
                37: '运动球',
                38: '风筝',
                39: '棒球棒',
                40: '棒球手套',
                41: '滑板',
                42: '冲浪板',
                43: '网球拍',
                44: '瓶子',
                46: '酒杯',
                47: '杯子',
                48: '叉子',
                49: '刀',
                50: '勺子',
                51: '碗',
                52: '香蕉',
                53: '苹果',
                54: '三明治',
                55: '橙子',
                56: '西兰花',
                57: '胡萝卜',
                58: '热狗',
                59: '披萨',
                60: '甜甜圈',
                61: '蛋糕',
                62: '椅子',
                63: '沙发',
                64: '盆栽',
                65: '床',
                67: '餐桌',
                70: '马桶',
                72: '电视',
                73: '笔记本电脑',
                74: '鼠标',
                75: '遥控器',
                76: '键盘',
                77: '手机',
                78: '微波炉',
                79: '烤箱',
                80: '烤面包机',
                81: '水槽',
                82: '冰箱',
                84: '书',
                85: '时钟',
                86: '花瓶',
                87: '剪刀',
                88: '泰迪熊',
                89: '吹风机',
                90: '牙刷'
            }
            print(f"成功加载 {len(self.categories)} 个类别标签")
            
        except Exception as e:
            print(f"模型初始化错误: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def classify_image(self, image_path):
        try:
            print("\n" + "="*50)
            print(f"开始处理图片: {image_path}")
            
            # 读取图片
            image = Image.open(image_path).convert('RGB')
            if image is None:
                print("无法读取图片")
                return []
            
            print(f"图片尺寸: {image.size[0]}x{image.size[1]}")
            
            # 预处理图片
            input_tensor = self.transform(image)
            input_batch = input_tensor.unsqueeze(0)
            
            # 使用模型进行预测
            with torch.no_grad():
                predictions = self.model(input_batch)
            
            # 处理预测结果
            detections = {}
            for prediction in predictions:
                boxes = prediction['boxes']
                labels = prediction['labels']
                scores = prediction['scores']
                
                for box, label, score in zip(boxes, labels, scores):
                    if score > 0.5:  # 置信度阈值
                        class_id = int(label.item())
                        if class_id in self.categories:
                            category = self.categories[class_id]
                            if category not in detections:
                                detections[category] = []
                            detections[category].append(float(score))
                            print(f"检测到: {category} (置信度: {float(score):.2%})")
            
            # 计算每个类别的平均置信度
            final_predictions = {}
            for category, confidences in detections.items():
                avg_confidence = sum(confidences) / len(confidences)
                final_predictions[category] = avg_confidence
            
            # 按置信度排序
            sorted_predictions = sorted(final_predictions.items(), key=lambda x: x[1], reverse=True)
            
            print("\n检测结果:")
            print("-"*30)
            
            results = []
            for category, confidence in sorted_predictions[:5]:
                print(f"类别: {category:<6} - 平均置信度: {confidence:.2%}")
                results.append({
                    'category': category,
                    'confidence': confidence
                })
            
            return results[:3]
            
        except Exception as e:
            print(f"图片检测错误: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return []

# 创建分类器实例
classifier = ImageClassifier()

@upload_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'GET':
        return render_template('upload.html')

    else:
        # 用户输入的标题和描述
        title = request.form['title']
        description = request.form['describe']
        if title == '请输入你的图像标题' or description == '请输入你的图像描述':
            flash('图片上传失败。请输入你的图像标题和描述。', 'error')
            return jsonify({'status': 'error', 'message': '图片上传失败。请输入你的图像标题和描述。'})

        # 判断是否正确上传
        if 'upl' not in request.files:
            flash('图片上传失败。未选择文件。', 'error')
            return jsonify({'status': 'error', 'message': '未选择文件'})

        img = request.files['upl']

        if img and allowed_imgformat(img.filename):  # 判断文件是否符合要求
            # 图像信息
            upload_time = datetime.now().strftime('%Y-%m-%d')
            img_format = os.path.splitext(img.filename)[1][1:]  # 获取文件扩展名

            # 保存图片到指定路径
            upload_path = 'static/images/user_upload/'
            img_name = unique_imgname()
            upload_filepath = os.path.join(upload_path, img_name + f'.{img_format}')
            img.save(upload_filepath)
            width, height = get_image_size(upload_filepath)

            # 打开图像文件
            with Image.open(img) as img:
                # 调整图像大小为 460x460 像素
                img = img.resize((460, 460))
                img.save(upload_filepath)
            
            # 连接数据库
            connection_string = config(True)
            cn = pyodbc.connect(connection_string)
            cursor = cn.cursor()

            # 获取当前最大的img_id
            cursor.execute("SELECT MAX(img_id) FROM Image")
            max_img_id = cursor.fetchone()[0] or 0
            new_img_id = max_img_id + 1

            # 前用户ID
            user_id = session['user_id']

            # 将图像数据插入Image表
            cursor.execute(
                "INSERT INTO Image (img_id, img_width, img_height, img_format, img_upload_time, img_path, user_id, img_name, img_description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (new_img_id, width, height, img_format, upload_time, img_name, user_id, title, description)
            )
            cn.commit()

            # 获取用户手动选择的标签数据
            tags = request.form.get('tags', '').split(',')
            if tags:
                for tag in tags:
                    if tag.strip():  # 确保标签不为空
                        # 查询标签表中是否包含当前标签
                        cursor.execute("SELECT tag_id FROM Tag WHERE tag_name = ?", tag.strip())
                        row = cursor.fetchone()

                        # 如果标签不在标签表中，插入新的标签记录
                        if not row:
                            cursor.execute("INSERT INTO Tag (tag_name) VALUES (?)", tag.strip())
                            cn.commit()
                            
                        # 建立标签索引
                        cursor.execute("Select tag_id from Tag Where tag_name=?", tag.strip())
                        tag_id = cursor.fetchone()[0]
                        cursor.execute("INSERT INTO Tag_index (img_id,tag_id) Values (?,?) ", (new_img_id, tag_id))
                        cn.commit()

            # 设置上传成功的flash消息
            flash('图片上传成功！', 'success')

            # 返回 JSON 响应
            return jsonify({'status': 'success', 'message': '图片上传成功'})

        else:
            # 显示错误消息
            flash('图片上传失败。请检查图片格式。', 'error')
            return jsonify({'status': 'error', 'message': '图片上传失败。请检查图片格式。'})

# 在 routes/upload.py 中修改 get_suggested_tags 函数
@upload_bp.route('/get_suggested_tags', methods=['POST'])
def get_suggested_tags():
    try:
        print("\n" + "="*50)
        print("开始处理标签请求")
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        print(f"标题: {title}")
        print(f"描述: {description}")
        
        # 处理图片分类
        image_predictions = []
        if 'upl' in request.files:
            img = request.files['upl']
            print(f"收到图片文件: {img.filename if img else 'None'}")
            
            if img and allowed_imgformat(img.filename):
                temp_dir = 'static/images/temp'
                os.makedirs(temp_dir, exist_ok=True)
                
                temp_path = os.path.join(temp_dir, unique_imgname() + '.jpg')
                print(f"保存临时文件到: {temp_path}")
                img.save(temp_path)
                
                try:
                    # 获取分类结果
                    print("开始图片分类...")
                    predictions = classifier.classify_image(temp_path)
                    print("分类结果:", predictions)
                    
                    # 确保返回前三名的预测结果
                    image_predictions = predictions[:3]
                    print("最终选择的图片标签:", image_predictions)
                except Exception as e:
                    print(f"图片分类出错: {str(e)}")
                    import traceback
                    print(traceback.format_exc())
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                        print("临时文件已删除")
        
        # 处理文本分析
        text_tags = []
        if title and title.strip():
            print("分析标题文本...")
            text_tags.extend(jieba.analyse.extract_tags(title, topK=2))
        if description and description.strip():
            print("分析描述文本...")
            text_tags.extend(jieba.analyse.extract_tags(description, topK=3))
        print("文本分析结果:", text_tags)
        
        # 返回结果
        result = {
            'image_tags': [
                {
                    'name': pred['category'],
                    'confidence': f"{pred['confidence']:.1%}"
                }
                for pred in image_predictions
            ],
            'text_tags': list(set(text_tags))
        }
        print("返回结果:", result)
        print("="*50 + "\n")
        
        return jsonify(result)
    except Exception as e:
        print(f"处理标签请求时出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'image_tags': [],
            'text_tags': []
        })