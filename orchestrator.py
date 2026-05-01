import json
import logging
from typing import Dict, List
from src.agents import (
    UserPersonaAgent,
    CreativeGenerationAgent,
    EffectPredictionAgent,
    ExecutionAgent,
)


class AgentOrchestrator:
    """Agent 编排器：串联 4 个 Agent 完成完整工作流"""

    def __init__(self, historical_data: dict = None):
        self.user_persona_agent = UserPersonaAgent()
        self.creative_gen_agent = CreativeGenerationAgent()
        self.effect_predict_agent = EffectPredictionAgent(historical_data or {})
        self.execution_agent = ExecutionAgent()

        self.logger = logging.getLogger("Orchestrator")

        self._pipeline_results = {}

    def run(self, orders: list, reviews: list, channels: list, product_info: dict, platforms: list) -> dict:
        """
        执行完整的工作流

        Args:
            orders: 订单数据
            reviews: 评价数据
            channels: 渠道列表
            product_info: 商品信息
            platforms: 目标平台列表

        Returns:
            完整工作流结果
        """
        self.logger.info("=" * 60)
        self.logger.info("电商商品详情页创意生成与 A/B 测试工作流启动")
        self.logger.info("=" * 60)

        self._print_header(product_info)

        step1 = self._run_user_persona_analysis(orders, reviews, channels)
        step2 = self._run_creative_generation(step1["personas"], product_info, platforms)
        step3 = self._run_effect_prediction(step2["creatives"])
        step4 = self._run_execution(step2["creatives"], step3["predictions"], product_info)

        self._pipeline_results = {
            "product_info": product_info,
            "user_personas": step1["personas"],
            "creatives": self._serialize_creatives(step2["creatives"]),
            "predictions": self._serialize_predictions(step3["predictions"]),
            "execution_result": step4,
            "summary": self._generate_summary(step1, step2, step3, step4)
        }

        self._print_summary(self._pipeline_results["summary"])

        return self._pipeline_results

    def _run_user_persona_analysis(self, orders: list, reviews: list, channels: list) -> dict:
        self.logger.info("\n[Step 1] 用户画像分析...")

        personas = self.user_persona_agent.execute(
            orders=orders,
            reviews=reviews,
            channels=channels
        )

        self.logger.info(f"  -> 完成 {len(personas)} 个渠道的用户画像分析")
        for channel, persona in personas.items():
            self.logger.info(f"  -> {channel}: 年龄段={persona.age_range}, 客单价={persona.avg_order_value}, 复购率={persona.repurchase_rate}")

        return {"personas": personas}

    def _run_creative_generation(self, personas: dict, product_info: dict, platforms: list) -> dict:
        self.logger.info("\n[Step 2] 多平台创意生成...")

        creatives = self.creative_gen_agent.execute(
            personas=personas,
            product_info=product_info,
            platforms=platforms
        )

        self.logger.info(f"  -> 生成 {len(creatives)} 个创意版本")
        for creative in creatives:
            self.logger.info(f"  -> [{creative.platform}] {creative.version_id}: {creative.title}")

        return {"creatives": creatives}

    def _run_effect_prediction(self, creatives: list) -> dict:
        self.logger.info("\n[Step 3] 效果预估...")

        self.effect_predict_agent._predictions_buffer = []

        predictions = self.effect_predict_agent.execute(creatives=creatives)

        self.effect_predict_agent._predictions_buffer = predictions

        self.logger.info(f"  -> 完成 {len(predictions)} 个版本的效果预测")
        for pred in predictions:
            self.logger.info(f"  -> {pred.version_id}: 预估CTR={pred.predicted_ctr:.2%}, CVR={pred.predicted_cvr:.2%}, 置信度={pred.confidence_score}")

        return {"predictions": predictions}

    def _run_execution(self, creatives: list, predictions: list, product_info: dict) -> dict:
        self.logger.info("\n[Step 4] 执行 A/B 测试...")

        result = self.execution_agent.execute(
            creatives=creatives,
            predictions=predictions,
            product_info=product_info
        )

        test_result = result["test_result"]
        self.logger.info(f"  -> 测试ID: {test_result.test_id}")
        self.logger.info(f"  -> 胜出版本: {test_result.winner_version}")
        self.logger.info(f"  -> 统计显著性: {test_result.statistical_significance:.2%}")
        self.logger.info(f"  -> 建议: {test_result.recommendation}")

        return result

    def _serialize_creatives(self, creatives: list) -> list:
        return [
            {
                "version_id": c.version_id,
                "platform": c.platform,
                "title": c.title,
                "main_selling_points": c.main_selling_points,
                "detail_page_copy": c.detail_page_copy,
                "image_copy": c.image_copy,
                "style_tags": c.style_tags
            }
            for c in creatives
        ]

    def _serialize_predictions(self, predictions: list) -> list:
        return [
            {
                "version_id": p.version_id,
                "predicted_ctr": p.predicted_ctr,
                "predicted_cvr": p.predicted_cvr,
                "confidence_score": p.confidence_score,
                "key_factors": p.key_factors,
                "risk_notes": p.risk_notes
            }
            for p in predictions
        ]

    def _generate_summary(self, step1, step2, step3, step4) -> dict:
        execution_result = step4
        test_result = execution_result["test_result"]

        return {
            "channels_analyzed": len(step1["personas"]),
            "creatives_generated": len(step2["creatives"]),
            "test_id": test_result.test_id,
            "winner_version": test_result.winner_version,
            "winner_performance": test_result.version_results.get(test_result.winner_version, {}),
            "statistical_significance": test_result.statistical_significance,
            "recommendation": test_result.recommendation
        }

    def _print_header(self, product_info: dict):
        print("\n" + "=" * 60)
        print(f"  电商商品详情页创意生成与 A/B 测试 Agent")
        print(f"  商品: {product_info.get('name', '未知')}")
        print(f"  品牌: {product_info.get('brand', '未知')}")
        print(f"  价格: {product_info.get('price', '未知')}元")
        print("=" * 60)

    def _print_summary(self, summary: dict):
        print("\n" + "=" * 60)
        print("  工作流执行摘要")
        print("=" * 60)
        print(f"  分析渠道数: {summary['channels_analyzed']}")
        print(f"  生成创意数: {summary['creatives_generated']}")
        print(f"  测试ID: {summary['test_id']}")
        print(f"  胜出版本: {summary['winner_version']}")

        winner_perf = summary['winner_performance']
        if winner_perf:
            print(f"  胜出版本表现:")
            print(f"    CTR: {winner_perf.get('ctr', 0):.2%}")
            print(f"    CVR: {winner_perf.get('cvr', 0):.2%}")
            print(f"    加购率: {winner_perf.get('add_to_cart_rate', 0):.2%}")

        print(f"  统计显著性: {summary['statistical_significance']:.2%}")
        print(f"\n  建议:")
        print(f"  {summary['recommendation']}")
        print("=" * 60 + "\n")

    def export_report(self, filepath: str = "output/report.json"):
        """导出完整报告"""
        import os
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self._pipeline_results, f, ensure_ascii=False, indent=2, default=str)

        print(f"报告已导出至: {filepath}")
