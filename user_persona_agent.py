import re
import random
from collections import Counter
from typing import List, Dict
from src.core import BaseAgent
from src.models import UserPersona


class UserPersonaAgent(BaseAgent):
    """用户画像 Agent：基于订单和评价数据提炼不同渠道用户偏好"""

    def __init__(self):
        super().__init__("用户画像Agent")

    def run(self, orders: list, reviews: list, channels: list) -> Dict[str, UserPersona]:
        """
        分析订单和评价数据，生成各渠道用户画像

        Args:
            orders: 订单数据列表
            reviews: 评价数据列表
            channels: 需要分析的渠道列表

        Returns:
            各渠道用户画像字典
        """
        personas = {}

        for channel in channels:
            channel_orders = [o for o in orders if o.get("channel") == channel]
            channel_reviews = [r for r in reviews if r.get("channel") == channel]

            personas[channel] = self._build_persona(channel, channel_orders, channel_reviews)

        return personas

    def _build_persona(self, channel: str, orders: list, reviews: list) -> UserPersona:
        if not orders and not reviews:
            return self._default_persona(channel)

        age_range = self._extract_age_distribution(orders)
        gender_ratio = self._extract_gender_ratio(orders)
        income_level = self._estimate_income_level(orders)
        interests = self._extract_interests(orders, reviews)
        drivers = self._extract_purchase_drivers(reviews)
        pain_points = self._extract_pain_points(reviews)
        style = self._infer_content_style(reviews)
        avg_order = self._calc_avg_order_value(orders)
        repurchase = self._calc_repurchase_rate(orders)
        behavior = self._extract_platform_behavior(orders, reviews)

        return UserPersona(
            channel=channel,
            age_range=age_range,
            gender_ratio=gender_ratio,
            income_level=income_level,
            top_interests=interests[:5],
            purchase_drivers=drivers[:4],
            pain_points=pain_points[:3],
            preferred_content_style=style,
            avg_order_value=avg_order,
            repurchase_rate=repurchase,
            platform_behavior=behavior
        )

    def _extract_age_distribution(self, orders: list) -> str:
        if not orders:
            return "25-35"
        ages = [o.get("user_age", 30) for o in orders]
        age_counts = Counter()
        for age in ages:
            if age < 18:
                age_counts["18岁以下"] += 1
            elif age < 25:
                age_counts["18-24"] += 1
            elif age < 35:
                age_counts["25-34"] += 1
            elif age < 45:
                age_counts["35-44"] += 1
            else:
                age_counts["45以上"] += 1
        return age_counts.most_common(1)[0][0]

    def _extract_gender_ratio(self, orders: list) -> dict:
        if not orders:
            return {"female": 0.6, "male": 0.4}
        genders = [o.get("user_gender", "female") for o in orders]
        counts = Counter(genders)
        total = len(genders)
        return {
            "female": round(counts.get("female", 0) / total, 2),
            "male": round(counts.get("male", 0) / total, 2)
        }

    def _estimate_income_level(self, orders: list) -> str:
        if not orders:
            return "中等收入"
        avg_price = sum(o.get("order_amount", 0) for o in orders) / len(orders)
        if avg_price > 500:
            return "高收入"
        elif avg_price > 200:
            return "中等收入"
        else:
            return "中低收入"

    def _extract_interests(self, orders: list, reviews: list) -> list:
        keywords = []
        review_texts = [r.get("content", "") for r in reviews]
        for text in review_texts:
            words = re.findall(r'[\u4e00-\u9fa5]{2,4}', text)
            keywords.extend(words)

        interest_candidates = ["性价比", "品质", "颜值", "实用", "时尚", "科技感", "健康", "母婴", "家居", "运动"]
        interest_scores = {}
        for interest in interest_candidates:
            score = sum(1 for kw in keywords if interest in kw)
            if score > 0:
                interest_scores[interest] = score

        sorted_interests = sorted(interest_scores.items(), key=lambda x: x[1], reverse=True)
        return [item[0] for item in sorted_interests] if sorted_interests else interest_candidates[:3]

    def _extract_purchase_drivers(self, reviews: list) -> list:
        positive_keywords = {
            "便宜": "价格实惠", "划算": "性价比高", "好用": "使用体验好",
            "质量": "品质可靠", "好看": "颜值高", "方便": "便捷实用",
            "推荐": "口碑推荐", "回购": "复购意愿强", "惊喜": "超出预期"
        }

        driver_scores = Counter()
        for review in reviews:
            content = review.get("content", "")
            rating = review.get("rating", 5)
            if rating >= 4:
                for keyword, driver in positive_keywords.items():
                    if keyword in content:
                        driver_scores[driver] += 1

        return [driver for driver, _ in driver_scores.most_common(4)] or ["性价比", "品质", "口碑"]

    def _extract_pain_points(self, reviews: list) -> list:
        negative_keywords = {
            "贵": "价格偏高", "慢": "物流/响应慢", "差": "质量不佳",
            "小": "尺寸/容量偏小", "重": "重量/体积过大", "复杂": "操作复杂",
            "褪色": "易褪色/变形", "噪音": "噪音问题"
        }

        pain_scores = Counter()
        for review in reviews:
            content = review.get("content", "")
            rating = review.get("rating", 5)
            if rating <= 3:
                for keyword, pain in negative_keywords.items():
                    if keyword in content:
                        pain_scores[pain] += 1

        return [pain for pain, _ in pain_scores.most_common(3)] or ["无明显痛点"]

    def _infer_content_style(self, reviews: list) -> str:
        if not reviews:
            return "简洁专业"

        emotional_words = sum(1 for r in reviews if any(w in r.get("content", "") for w in ["太棒了", "超喜欢", "绝绝子", "必须买", "种草"]))
        detail_words = sum(1 for r in reviews if any(w in r.get("content", "") for w in ["详细", "参数", "对比", "分析", "实测"]))

        if emotional_words > detail_words * 2:
            return "情感共鸣型"
        elif detail_words > emotional_words * 2:
            return "数据专业型"
        else:
            return "平衡综合型"

    def _calc_avg_order_value(self, orders: list) -> float:
        if not orders:
            return 150.0
        return round(sum(o.get("order_amount", 0) for o in orders) / len(orders), 2)

    def _calc_repurchase_rate(self, orders: list) -> float:
        if not orders:
            return 0.15
        users = Counter(o.get("user_id", "") for o in orders)
        repeat_users = sum(1 for count in users.values() if count > 1)
        return round(repeat_users / len(users), 2) if users else 0.15

    def _extract_platform_behavior(self, orders: list, reviews: list) -> dict:
        avg_review_len = sum(len(r.get("content", "")) for r in reviews) / max(len(reviews), 1)
        img_reviews = sum(1 for r in reviews if r.get("has_image", False))
        img_rate = img_reviews / max(len(reviews), 1)

        return {
            "avg_review_length": round(avg_review_len, 1),
            "image_review_rate": round(img_rate, 2),
            "peak_shopping_hour": self._guess_peak_hour(orders),
            "browsing_depth": random.choice(["浅", "中", "深"])
        }

    def _guess_peak_hour(self, orders: list) -> int:
        if not orders:
            return 20
        hours = [o.get("order_hour", 20) for o in orders]
        return Counter(hours).most_common(1)[0][0]

    def _default_persona(self, channel: str) -> UserPersona:
        return UserPersona(
            channel=channel,
            age_range="25-34",
            gender_ratio={"female": 0.6, "male": 0.4},
            income_level="中等收入",
            top_interests=["性价比", "品质", "颜值"],
            purchase_drivers=["性价比", "品质", "口碑"],
            pain_points=["无明显痛点"],
            preferred_content_style="平衡综合型",
            avg_order_value=150.0,
            repurchase_rate=0.15,
            platform_behavior={"avg_review_length": 50, "image_review_rate": 0.3, "peak_shopping_hour": 20}
        )
