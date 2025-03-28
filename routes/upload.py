from flask import Flask, render_template, request, redirect, url_for, session, flash, Blueprint, jsonify
import os
import pyodbc
import time
from datetime import datetime
from PIL import Image
import jieba
from jieba import analyse
import torch
from torchvision import transforms, models
import numpy as np
from efficientnet_pytorch import EfficientNet
import timm  # 添加timm库支持更多模型
import torch.nn.functional as F


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
            print("\n正在初始化图像分类器...")
            # 使用多个模型集成
            self.models = {
                'efficientnet': EfficientNet.from_pretrained('efficientnet-b4'),
                'resnet': models.resnet101(pretrained=True),
                'vit': timm.create_model('vit_base_patch16_224', pretrained=True)
            }
            
            for model in self.models.values():
                model.eval()
            print("模型加载成功")
            
            print("设置图像预处理...")
            # 改进的图像预处理
            self.preprocess = {
                'efficientnet': transforms.Compose([
                    transforms.Resize(380),
                    transforms.CenterCrop(380),
                    transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ]),
                'resnet': transforms.Compose([
                    transforms.Resize(256),
                    transforms.CenterCrop(224),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ]),
                'vit': transforms.Compose([
                    transforms.Resize(256),
                    transforms.CenterCrop(224),
                    transforms.ToTensor(),
                    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
                ])
            }
            print("预处理设置完成")
            
            self.categories = self._load_categories()
            print(f"成功加载 {len(self.categories)} 个类别标签")
            
        except Exception as e:
            print(f"模型初始化错误: {str(e)}")
            import traceback
            print(traceback.format_exc())
    
    def _load_categories(self):
        # 扩展的分类标签，包含更多 ImageNet 类别
        return {
            # 动物类
            '281': '猫',        # tabby cat
            '282': '狗',        # dog
            '283': '兔子',      # rabbit
            '284': '仓鼠',      # hamster
            '285': '松鼠',      # squirrel
            '286': '牛',        # cow
            '287': '斑马',      # zebra
            '266': '老虎',      # tiger
            '265': '狮子',      # lion
            '194': '狐狸',      # fox
            '153': '吉娃娃',    # chihuahua
            '185': '熊猫',      # panda
            '295': '羊',        # sheep
            '296': '猴子',      # monkey
            '297': '大象',      # elephant
            '298': '长颈鹿',    # giraffe
            '299': '鸟类',      # bird
            
            # 人物类
            '370': '人物',      # person
            '401': '人像',      # portrait
            
            # 电子设备类
            '407': '电脑',      # computer
            '504': '键盘',      # keyboard
            '527': '手机',      # mobile phone
            '531': '显示器',    # monitor
            '532': '鼠标',      # mouse
            
            # 日常物品
            '573': '笔记本',    # notebook
            '920': '书本',      # book
            '924': '食物',      # food
            
            # 交通工具
            '765': '汽车',      # car
            '744': '火车',      # train
            '751': '飞机',      # airplane
            
            # 自然景观
            '833': '树木',      # tree
            '972': '风景',      # landscape
            '973': '建筑',      # building
            '974': '花卉',      # flower
            
            # 场景类
            '463': '办公',      # office
            '510': '运动',      # sports
            '742': '交通',      # transportation
            '834': '自然',      # nature
            '907': '艺术',      # art
            '975': '城市',      # city
            
            # 其他常见类别
            '150': '玩具',      # toy
            '300': '食品',      # food
            '400': '家具',      # furniture
            '500': '电器',      # appliance
            '600': '服装',      # clothing
            '700': '运动器材',  # sports equipment
            '800': '乐器',      # musical instrument
            '900': '工具',      # tool
        }
    
    def classify_image(self, image_path):
        try:
            print("\n" + "="*50)
            print(f"开始处理图片: {image_path}")
            image = Image.open(image_path).convert('RGB')
            
            if image.size[0] < 100 or image.size[1] < 100:
                print("图片分辨率过低")
                return []
            
            print(f"图片尺寸: {image.size[0]}x{image.size[1]}")
            
            # 存储所有模型的预测结果
            all_predictions = {}
            
            # 使用每个模型进行预测
            for model_name, model in self.models.items():
                input_tensor = self.preprocess[model_name](image)
                input_batch = input_tensor.unsqueeze(0)
                
                with torch.no_grad():
                    output = model(input_batch)
                    probabilities = F.softmax(output[0], dim=0)
                    top5_prob, top5_catid = torch.topk(probabilities, 5)
                    
                    # 存储每个模型的预测结果
                    for i in range(5):
                        category_id = str(top5_catid[i].item())
                        confidence = float(top5_prob[i].item())
                        if category_id in self.categories:
                            category = self.categories[category_id]
                            if category not in all_predictions:
                                all_predictions[category] = []
                            all_predictions[category].append(confidence)
            
            # 计算每个类别的平均置信度
            final_predictions = {}
            for category, confidences in all_predictions.items():
                avg_confidence = sum(confidences) / len(confidences)
                final_predictions[category] = avg_confidence
            
            # 按置信度排序
            sorted_predictions = sorted(final_predictions.items(), key=lambda x: x[1], reverse=True)
            
            print("\n集成预测结果:")
            print("-"*30)
            
            results = []
            for category, confidence in sorted_predictions[:5]:
                print(f"类别: {category:<6} - 平均置信度: {confidence:.2%}")
                # 移除置信度阈值，直接取前三名
                results.append({
                    'category': category,
                    'confidence': confidence
                })
            
            # 返回前三名结果
            final_results = results[:3]
            print("\n最终选择的标签:", ", ".join([r['category'] for r in final_results]))
            print("="*50 + "\n")
            
            return final_results
            
        except Exception as e:
            print(f"图片分类错误: {str(e)}")
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

            # 查询当前图片数量
            cursor.execute("SELECT count(*) FROM Image")
            img_num = cursor.fetchone()[0]

            # 前用户ID
            user_id = session['user_id']

            # 将图像数据插入Image表
            cursor.execute(
                "INSERT INTO Image (img_id, img_width, img_height, img_format, img_upload_time, img_path, user_id, img_name, img_description) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (img_num + 1, width, height, img_format, upload_time, img_name, user_id, title, description)
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
                        cursor.execute("INSERT INTO Tag_index (img_id,tag_id) Values (?,?) ", (img_num+1, tag_id))
                        cn.commit()

            # 设置上传成功的flash消息
            flash('图片上传成功！', 'success')

            # 返回 JSON 响应
            return jsonify({'status': 'success', 'message': '图片上传成功'})

        else:
            # 显示错误消息
            flash('图片上传失败。请检查图片格式。', 'error')
            return jsonify({'status': 'error', 'message': '图片上传失败。请检查图片格式。'})

@upload_bp.route('/get_suggested_tags', methods=['POST'])
def get_suggested_tags():
    try:
        print("开始处理标签请求")
        title = request.form.get('title', '')
        description = request.form.get('description', '')
        
        print(f"收到的标题: {title}")  # 添加调试信息
        print(f"收到的描述: {description}")  # 添加调试信息
        
        # 提取关键词
        title_keywords = []
        description_keywords = []
        
        if title and title != '请输入你的图像标题':
            title_keywords = jieba.analyse.extract_tags(title, topK=2, withWeight=False, allowPOS=('n', 'nr', 'ns'))
            print(f"标题关键词: {title_keywords}")  # 添加调试信息
        
        if description and description != '请输入你的图像描述':
            description_keywords = jieba.analyse.extract_tags(description, topK=3, withWeight=False, allowPOS=('n', 'nr', 'ns'))
            print(f"描述关键词: {description_keywords}")  # 添加调试信息
        
        # 处理图片分类
        image_predictions = []
        if 'upl' in request.files:
            img = request.files['upl']
            if img and allowed_imgformat(img.filename):
                temp_dir = 'static/images/temp'
                os.makedirs(temp_dir, exist_ok=True)
                
                temp_path = os.path.join(temp_dir, unique_imgname() + '.jpg')
                img.save(temp_path)
                
                try:
                    # 获取分类结果
                    predictions = classifier.classify_image(temp_path)
                    print("分类结果:", predictions)  # 添加调试信息
                    
                    # 确保返回前三名的预测结果
                    image_predictions = predictions[:3]
                finally:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
        
        # 打印返回的数据以便调试
        response_data = {
            'image_tags': [
                {
                    'name': pred['category'],
                    'confidence': f"{pred['confidence']:.1%}"
                }
                for pred in image_predictions
            ],
            'text_tags': list(set(title_keywords + description_keywords))
        }
        print("返回的数据:", response_data)
        
        return jsonify(response_data)
    except Exception as e:
        print(f"处理标签请求时出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'image_tags': [],
            'text_tags': []
        })
