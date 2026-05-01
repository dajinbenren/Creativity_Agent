import json
import datetime
from typing import List, Dict
from src.core import BaseAgent
from src.models import CreativeVersion, PredictionResult, ABTestConfig, ABTestResult


class ExecutionAgent(BaseAgent):
    """执行 Agent：同步文案到店铺后台并收集 A/B 测试数据"""

    def __init__(self, store_api_mock=None):
        super().__init__("执行Agent")
        self.store_api = store_api_mock or MockStoreAPI()
        self.collected_data = {}

    def run(self, creatives: List[CreativeVersion], predictions: List[PredictionResult], product_info: dict) -> dict:
        """
        执行文案同步和 A/B 测试

        Args:
            creatives: 创意版本列表
            predictions: 预测结果列表
            product_info: 商品信息

        Returns:
            执行结果
        """
        test_config = self._create_ab_test_config(creatives, product_info)

        sync_results = self._sync_to_store(creatives, test_config)

        self._initialize_test_data(test_config)

        test_result = self._simulate_and_analyze(test_config, predictions)

        return {
            "test_config": test_config,
            "sync_results": sync_results,
            "test_result": test_result,
            "executed_at": datetime.datetime.now().isoformat()
        }

    def _create_ab_test_config(self, creatives: List[CreativeVersion], product_info: dict) -> ABTestConfig:
        version_ids = [c.version_id for c in creatives]
        n_versions = len(version_ids)
        split = round(1.0 / n_versions, 2)

        traffic_split = {vid: split for vid in version_ids}

        return ABTestConfig(
            test_id=f"AB_{product_info.get('id', 'unknown')}_{datetime.datetime.now().strftime('%Y%m%d')}",
            product_id=product_info.get("id", "unknown"),
            versions=version_ids,
            traffic_split=traffic_split,
            duration_days=2,
            primary_metric="conversion_rate",
            secondary_metrics=["click_through_rate", "add_to_cart_rate", "bounce_rate"]
        )

    def _sync_to_store(self, creatives: List[CreativeVersion], config: ABTestConfig) -> list:
        results = []

        for creative in creatives:
            payload = {
                "version_id": creative.version_id,
                "title": creative.title,
                "detail_page_copy": creative.detail_page_copy,
                "main_selling_points": creative.main_selling_points,
                "image_copy": creative.image_copy,
                "traffic_allocation": config.traffic_split.get(creative.version_id, 0)
            }

            sync_result = self.store_api.sync_creative(
                product_id=config.product_id,
                creative_data=payload
            )

            results.append({
                "version_id": creative.version_id,
                "platform": creative.platform,
                "sync_status": sync_result["status"],
                "sync_time": sync_result["timestamp"]
            })

        return results

    def _initialize_test_data(self, config: ABTestConfig):
        for version_id in config.versions:
            self.collected_data[version_id] = {
                "impressions": 0,
                "clicks": 0,
                "conversions": 0,
                "add_to_cart": 0,
                "bounce_count": 0,
                "hourly_data": {}
            }

    def _simulate_and_analyze(self, config: ABTestConfig, predictions: List[PredictionResult]) -> ABTestResult:
        self._simulate_traffic(config)

        version_results = {}
        for version_id in config.versions:
            data = self.collected_data[version_id]
            impressions = data["impressions"]

            ctr = data["clicks"] / impressions if impressions > 0 else 0
            cvr = data["conversions"] / data["clicks"] if data["clicks"] > 0 else 0

            version_results[version_id] = {
                "impressions": impressions,
                "clicks": data["clicks"],
                "conversions": data["conversions"],
                "ctr": round(ctr, 4),
                "cvr": round(cvr, 4),
                "add_to_cart_rate": round(data["add_to_cart"] / impressions if impressions > 0 else 0, 4),
                "bounce_rate": round(data["bounce_count"] / impressions if impressions > 0 else 0, 4)
            }

        winner_id = self._determine_winner(version_results, config.primary_metric)
        significance = self._calc_statistical_significance(version_results, winner_id)
        recommendation = self._generate_recommendation(version_results, winner_id, predictions)

        return ABTestResult(
            test_id=config.test_id,
            version_results=version_results,
            winner_version=winner_id,
            statistical_significance=round(significance, 4),
            recommendation=recommendation
        )

    def _simulate_traffic(self, config: ABTestConfig):
        total_impressions = 10000

        for version_id in config.versions:
            traffic = config.traffic_split.get(version_id, 0.33)
            impressions = int(total_impressions * traffic)

            prediction = next((p for p in self.predictions_buffer if p.version_id == version_id), None)

            base_ctr = 0.05 + random.uniform(-0.01, 0.02)
            base_cvr = 0.03 + random.uniform(-0.005, 0.01)

            if prediction:
                base_ctr = prediction.predicted_ctr * (0.9 + random.uniform(0, 0.2))
                base_cvr = prediction.predicted_cvr * (0.9 + random.uniform(0, 0.2))

            clicks = int(impressions * base_ctr)
            conversions = int(clicks * base_cvr)
            add_to_cart = int(impressions * (base_ctr * 0.5 + random.uniform(0, 0.02)))
            bounce = int(impressions * (0.3 + random.uniform(-0.05, 0.1)))

            self.collected_data[version_id].update({
                "impressions": impressions,
                "clicks": clicks,
                "conversions": conversions,
                "add_to_cart": add_to_cart,
                "bounce_count": bounce
            })

    @property
    def predictions_buffer(self) -> list:
        return getattr(self, "_predictions_buffer", [])

    def _determine_winner(self, version_results: dict, primary_metric: str) -> str:
        metric_map = {"conversion_rate": "cvr", "click_through_rate": "ctr"}
        metric_key = metric_map.get(primary_metric, "cvr")

        winner_id = max(version_results, key=lambda vid: version_results[vid].get(metric_key, 0))
        return winner_id

    def _calc_statistical_significance(self, version_results: dict, winner_id: str) -> float:
        winner_data = version_results[winner_id]
        winner_impressions = winner_data["impressions"]

        if winner_impressions < 1000:
            return 0.75
        elif winner_impressions < 3000:
            return 0.85
        elif winner_impressions < 5000:
            return 0.92
        else:
            return 0.95

    def _generate_recommendation(self, version_results: dict, winner_id: str, predictions: List[PredictionResult]) -> str:
        winner_data = version_results[winner_id]

        recommendation_parts = [
            f"推荐版本：{winner_id}",
            f"CVR: {winner_data['cvr']:.2%}, CTR: {winner_data['ctr']:.2%}",
            ""
        ]

        sorted_versions = sorted(version_results.items(), key=lambda x: x[1]["cvr"], reverse=True)
        if len(sorted_versions) > 1 and sorted_versions[0][1]["cvr"] > sorted_versions[1][1]["cvr"] * 1.1:
            recommendation_parts.append("胜出版本显著优于其他版本，建议全量切换。")
        else:
            recommendation_parts.append("各版本差距较小，建议延长测试周期或优化差异化策略。")

        return "\n".join(recommendation_parts)


import random


class MockStoreAPI:
    """模拟店铺后台 API"""

    def __init__(self):
        self.synced_creatives = {}

    def sync_creative(self, product_id: str, creative_data: dict) -> dict:
        version_id = creative_data["version_id"]
        self.synced_creatives[f"{product_id}_{version_id}"] = creative_data

        return {
            "status": "success",
            "version_id": version_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "message": f"创意 {version_id} 已同步到店铺"
        }

    def get_synced_creatives(self) -> dict:
        return self.synced_creatives
