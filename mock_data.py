import random
import datetime


def generate_mock_orders(n=500, channels=None):
    """生成模拟订单数据"""
    if channels is None:
        channels = ["douyin", "taobao", "pinduoduo"]

    orders = []
    for i in range(n):
        channel = random.choice(channels)

        if channel == "douyin":
            age = random.randint(18, 35)
            gender = random.choices(["female", "male"], weights=[0.7, 0.3])[0]
            amount = random.uniform(50, 200)
            hour = random.choices(range(24), weights=[1, 1, 1, 1, 1, 2, 3, 4, 5, 4, 3, 3, 4, 4, 5, 6, 7, 8, 10, 12, 15, 12, 8, 4])[0]

        elif channel == "taobao":
            age = random.randint(22, 45)
            gender = random.choices(["female", "male"], weights=[0.55, 0.45])[0]
            amount = random.uniform(100, 500)
            hour = random.choices(range(24), weights=[1, 1, 1, 1, 1, 1, 2, 4, 6, 8, 9, 8, 7, 6, 7, 8, 9, 10, 12, 14, 12, 8, 5, 2])[0]

        else:
            age = random.randint(20, 50)
            gender = random.choices(["female", "male"], weights=[0.5, 0.5])[0]
            amount = random.uniform(20, 150)
            hour = random.choices(range(24), weights=[1, 1, 1, 1, 1, 1, 2, 3, 5, 6, 7, 6, 5, 5, 6, 7, 8, 9, 11, 13, 14, 12, 8, 3])[0]

        orders.append({
            "order_id": f"ORD{i:06d}",
            "user_id": f"U{random.randint(1, 200):04d}",
            "channel": channel,
            "user_age": age,
            "user_gender": gender,
            "order_amount": round(amount, 2),
            "order_hour": hour,
            "order_date": (datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 90))).isoformat(),
            "product_id": "PROD001"
        })

    return orders


def generate_mock_reviews(n=300, channels=None):
    """生成模拟评价数据"""
    if channels is None:
        channels = ["douyin", "taobao", "pinduoduo"]

    positive_templates = [
        "太棒了，{feature}效果很好，{benefit}，值得推荐",
        "性价比超高，{feature}很满意，{benefit}，会回购",
        "质量不错，{feature}很实用，{benefit}，好评",
        "物流快，{feature}超预期，{benefit}，种草了",
        "绝绝子！{feature}太香了，{benefit}，必须买",
        "对比了很多家，这家{feature}最好，{benefit}，推荐购买",
        "包装精美，{feature}很好用，{benefit}，还会再来"
    ]

    negative_templates = [
        "价格有点贵，{feature}一般，希望改进",
        "物流太慢了，{feature}还可以，但是体验不好",
        "尺寸偏小，{feature}还行，总体一般",
        "操作太复杂，{feature}没想象中好",
        "质量一般，{feature}用了几次就出问题了"
    ]

    features = ["颜值", "质感", "功能", "包装", "物流", "客服", "效果", "设计", "做工", "材质"]
    benefits = ["性价比很高", "物超所值", "超出预期", "很实用", "好看又好用", "值得入手", "推荐给朋友"]

    reviews = []
    for i in range(n):
        channel = random.choice(channels)
        rating = random.choices([1, 2, 3, 4, 5], weights=[0.05, 0.05, 0.1, 0.25, 0.55])[0]

        if rating >= 4:
            template = random.choice(positive_templates)
            content = template.format(
                feature=random.choice(features),
                benefit=random.choice(benefits)
            )
        else:
            template = random.choice(negative_templates)
            content = template.format(feature=random.choice(features))

        reviews.append({
            "review_id": f"REV{i:06d}",
            "channel": channel,
            "rating": rating,
            "content": content,
            "has_image": random.random() < 0.4,
            "review_date": (datetime.datetime.now() - datetime.timedelta(days=random.randint(0, 60))).isoformat(),
            "product_id": "PROD001"
        })

    return reviews


def get_mock_product_info():
    """获取模拟商品信息"""
    return {
        "id": "PROD001",
        "name": "智能保温杯",
        "brand": "小米有品",
        "brand_desc": "专注智能家居与品质生活",
        "price": "129",
        "original_price": "199",
        "discount": "70",
        "key_feature": "温度显示+12小时保温",
        "certification": "国家食品级认证",
        "warranty": "1年质保",
        "category": "家居生活",
        "tags": ["智能", "保温", "便携", "高颜值"]
    }


def get_mock_historical_data():
    """获取模拟历史数据"""
    return {
        "douyin": {
            "avg_ctr_performance": 0.15,
            "total_tests": 45,
            "avg_winner_ctr": 0.092,
            "avg_winner_cvr": 0.035
        },
        "taobao": {
            "avg_ctr_performance": 0.08,
            "total_tests": 62,
            "avg_winner_ctr": 0.058,
            "avg_winner_cvr": 0.048
        },
        "pinduoduo": {
            "avg_ctr_performance": 0.20,
            "total_tests": 38,
            "avg_winner_ctr": 0.115,
            "avg_winner_cvr": 0.068
        },
        "douyin_cvr_bonus": 0.005,
        "taobao_cvr_bonus": 0.008,
        "pinduoduo_cvr_bonus": 0.012
    }
