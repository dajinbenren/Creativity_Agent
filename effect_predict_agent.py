import random
from typing import List
from src.core import BaseAgent
from src.models import CreativeVersion, PredictionResult


class EffectPredictionAgent(BaseAgent):
    """效果预估 Agent：基于历史数据预测各创意版本的点击率和转化率"""

    PLATFORM_BASE_CTR = {
        "douyin": 0.08,
        "taobao": 0.05,
        "pinduoduo": 0.10
    }

    PLATFORM_BASE_CVR = {
        "douyin": 0.03,
        "taobao": 0.04,
        "pinduoduo": 0.06
    }

    STYLE_BONUS = {
        "情感共鸣型": 0.02,
        "数据专业型": 0.01,
        "平衡综合型": 0.015
    }

    def __init__(self, historical_data: dict = None):
        super().__init__("效果预估Agent")
        self.historical_data = historical_data or {}

    def run(self, creatives: List[CreativeVersion]) -> List[PredictionResult]:
        """
        预测各创意版本的效果

        Args:
            creatives: 创意版本列表

        Returns:
            预测结果列表
        """
        predictions = []

        for creative in creatives:
            result = self._predict(creative)
            predictions.append(result)

        return predictions

    def _predict(self, creative: CreativeVersion) -> PredictionResult:
        platform = creative.platform
        persona = creative.target_persona

        ctr = self._predict_ctr(platform, persona, creative)
        cvr = self._predict_cvr(platform, persona, creative)
        confidence = self._calc_confidence(platform, creative)
        factors = self._identify_key_factors(creative)
        risks = self._identify_risks(creative)

        return PredictionResult(
            version_id=creative.version_id,
            predicted_ctr=round(ctr, 4),
            predicted_cvr=round(cvr, 4),
            confidence_score=round(confidence, 2),
            key_factors=factors,
            risk_notes=risks
        )

    def _predict_ctr(self, platform: str, persona, creative: CreativeVersion) -> float:
        base_ctr = self.PLATFORM_BASE_CTR.get(platform, 0.05)

        style_bonus = self.STYLE_BONUS.get(persona.preferred_content_style, 0)

        selling_point_bonus = min(len(creative.main_selling_points) * 0.005, 0.02)

        persona_match_bonus = 0
        if persona.avg_order_value > 200:
            persona_match_bonus = 0.01
        if persona.repurchase_rate > 0.2:
            persona_match_bonus += 0.01

        historical_bonus = self._get_historical_platform_bonus(platform)

        noise = random.uniform(-0.01, 0.01)

        ctr = base_ctr + style_bonus + selling_point_bonus + persona_match_bonus + historical_bonus + noise

        return max(0.01, min(ctr, 0.25))

    def _predict_cvr(self, platform: str, persona, creative: CreativeVersion) -> float:
        base_cvr = self.PLATFORM_BASE_CVR.get(platform, 0.04)

        interest_match = len(set(creative.style_tags) & set(persona.top_interests)) * 0.01

        pain_point_match = 0
        if persona.pain_points and persona.pain_points[0] != "无明显痛点":
            pain_point_match = 0.015

        price_sensitivity = 0
        if persona.income_level in ["中等收入", "中低收入"]:
            if creative.platform == "pinduoduo":
                price_sensitivity = 0.02

        historical_cvr_bonus = self.historical_data.get(f"{platform}_cvr_bonus", 0)

        noise = random.uniform(-0.005, 0.005)

        cvr = base_cvr + interest_match + pain_point_match + price_sensitivity + historical_cvr_bonus + noise

        return max(0.005, min(cvr, 0.20))

    def _calc_confidence(self, platform: str, creative: CreativeVersion) -> float:
        base_confidence = 0.75

        if platform in self.historical_data:
            base_confidence += 0.1

        if len(creative.main_selling_points) >= 3:
            base_confidence += 0.05

        if creative.target_persona.repurchase_rate > 0.2:
            base_confidence += 0.05

        return min(base_confidence, 0.95)

    def _identify_key_factors(self, creative: CreativeVersion) -> list:
        factors = []
        persona = creative.target_persona

        if persona.repurchase_rate > 0.2:
            factors.append("高复购率用户群")
        if persona.avg_order_value > 300:
            factors.append("高客单价潜力")
        if persona.preferred_content_style == "情感共鸣型":
            factors.append("情感化文案更易转化")
        if len(creative.main_selling_points) >= 3:
            factors.append("卖点丰富度佳")
        if "性价比" in persona.top_interests:
            factors.append("性价比敏感型用户")

        return factors or ["标准表现预期"]

    def _identify_risks(self, creative: CreativeVersion) -> list:
        risks = []
        persona = creative.target_persona

        if persona.repurchase_rate < 0.1:
            risks.append("用户忠诚度较低，转化难度高")
        if creative.platform == "douyin" and len(creative.main_selling_points) < 3:
            risks.append("抖音平台卖点不足，可能影响即时转化")
        if persona.income_level == "高收入" and creative.platform == "pinduoduo":
            risks.append("高收入用户在拼多多转化率可能低于预期")
        if persona.preferred_content_style == "数据专业型" and creative.platform == "douyin":
            risks.append("专业型内容在抖音传播力可能受限")

        return risks or ["无明显风险"]

    def _get_historical_platform_bonus(self, platform: str) -> float:
        platform_history = self.historical_data.get(platform, {})
        if not platform_history:
            return 0
        avg_performance = platform_history.get("avg_ctr_performance", 0)
        return avg_performance * 0.1
