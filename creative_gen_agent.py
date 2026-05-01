import uuid
from typing import Dict, List
from src.core import BaseAgent
from src.models import UserPersona, CreativeVersion, PlatformStyle


class CreativeGenerationAgent(BaseAgent):
    """创意生成 Agent：根据用户画像生成适配不同平台风格的详情页与主图文案"""

    PLATFORM_TEMPLATES = {
        PlatformStyle.DOUYIN.value: {
            "title_style": "情绪驱动+场景化",
            "copy_framework": "痛点-方案-效果-行动",
            "tone": "热情、网感、口语化",
            "max_title_len": 30,
            "max_selling_points": 3,
            "content_focus": "视觉冲击+即时转化"
        },
        PlatformStyle.TAOBAO.value: {
            "title_style": "关键词覆盖+卖点突出",
            "copy_framework": "品牌-功能-场景-保障",
            "tone": "专业、可信、精致",
            "max_title_len": 60,
            "max_selling_points": 5,
            "content_focus": "详情全面+决策辅助"
        },
        PlatformStyle.PINDUODUO.value: {
            "title_style": "价格优势+紧迫感",
            "copy_framework": "低价-品质-限时-拼团",
            "tone": "直接、实惠、紧迫",
            "max_title_len": 40,
            "max_selling_points": 3,
            "content_focus": "性价比+社交裂变"
        }
    }

    def __init__(self):
        super().__init__("创意生成Agent")

    def run(self, personas: Dict[str, UserPersona], product_info: dict, platforms: list) -> List[CreativeVersion]:
        """
        为不同平台生成创意版本

        Args:
            personas: 各渠道用户画像
            product_info: 商品信息
            platforms: 目标平台列表

        Returns:
            创意版本列表
        """
        creatives = []

        for platform in platforms:
            persona = personas.get(platform, list(personas.values())[0] if personas else None)
            if not persona:
                continue

            template = self.PLATFORM_TEMPLATES.get(platform)
            if not template:
                continue

            creative = self._generate_creative(
                platform=platform,
                persona=persona,
                product_info=product_info,
                template=template
            )
            creatives.append(creative)

        return creatives

    def _generate_creative(self, platform: str, persona: UserPersona, product_info: dict, template: dict) -> CreativeVersion:
        version_id = f"{platform}_{uuid.uuid4().hex[:6]}"

        title = self._generate_title(platform, persona, product_info, template)
        selling_points = self._generate_selling_points(platform, persona, product_info, template)
        detail_copy = self._generate_detail_page(platform, persona, product_info, template)
        image_copy = self._generate_image_copy(platform, persona, product_info, template)

        return CreativeVersion(
            version_id=version_id,
            platform=platform,
            title=title,
            main_selling_points=selling_points,
            detail_page_copy=detail_copy,
            image_copy=image_copy,
            target_persona=persona,
            style_tags=[template["title_style"], template["tone"], template["content_focus"]]
        )

    def _generate_title(self, platform: str, persona: UserPersona, product_info: dict, template: dict) -> str:
        product_name = product_info.get("name", "商品")
        price = product_info.get("price", "")
        key_feature = product_info.get("key_feature", "")

        if platform == PlatformStyle.DOUYIN.value:
            emotional_hooks = ["绝了！", "谁懂啊！", "太香了！", "必入！", "闭眼冲！"]
            import random
            hook = random.choice(emotional_hooks)
            return f"{hook}{product_name}{key_feature}，{persona.top_interests[0] if persona.top_interests else ''}天花板！"[:template["max_title_len"]]

        elif platform == PlatformStyle.TAOBAO.value:
            tags = " ".join(persona.top_interests[:3])
            return f"【官方正品】{product_name} {key_feature} {tags} 限时优惠{price}"[:template["max_title_len"]]

        elif platform == PlatformStyle.PINDUODUO.value:
            urgency = ["限时秒杀！", "今日特价！", "爆款直降！", "最后100件！"]
            import random
            urg = random.choice(urgency)
            return f"{urg}{product_name} 仅需{price}！{key_feature} 拼团更划算"[:template["max_title_len"]]

        return f"{product_name} - {key_feature}"

    def _generate_selling_points(self, platform: str, persona: UserPersona, product_info: dict, template: dict) -> list:
        points = []
        max_points = template["max_selling_points"]

        if platform == PlatformStyle.DOUYIN.value:
            point_templates = [
                f"🔥 {product_info.get('key_feature', '核心卖点')}，{persona.top_interests[0]}党的福音",
                f"✨ 3秒{product_info.get('key_feature', '展示效果')}，亲测有效",
                f"💰 不到一杯奶茶钱，{persona.purchase_drivers[0] if persona.purchase_drivers else '超值'}"
            ]

        elif platform == PlatformStyle.TAOBAO.value:
            point_templates = [
                f"【品质保障】{product_info.get('key_feature', '核心功能')}，{product_info.get('brand', '品牌')}官方正品",
                f"【用户口碑】{persona.top_interests[0]}认可度98%，好评如潮",
                f"【专业认证】通过{product_info.get('certification', '国家认证')}，安全可靠",
                f"【售后无忧】7天无理由退换，{product_info.get('warranty', '1年质保')}",
                f"【场景适配】{persona.top_interests[1] if len(persona.top_interests) > 1 else '多场景'}使用，满足你的需求"
            ]

        elif platform == PlatformStyle.PINDUODUO.value:
            point_templates = [
                f"🔴 惊爆价{product_info.get('price', 'XX元')}，比淘宝便宜30%",
                f"🔴 万人拼团，{persona.purchase_drivers[0] if persona.purchase_drivers else '品质'}保证",
                f"🔴 今天下单明天到，不满意包退"
            ]

        else:
            point_templates = [product_info.get("key_feature", "核心卖点")]

        points = point_templates[:max_points]
        return points

    def _generate_detail_page(self, platform: str, persona: UserPersona, product_info: dict, template: dict) -> str:
        product_name = product_info.get("name", "商品")
        key_feature = product_info.get("key_feature", "")
        price = product_info.get("price", "")

        if platform == PlatformStyle.DOUYIN.value:
            return f"""【开篇种草】
{persona.top_interests[0] if persona.top_interests else '爱美'}的姐妹们看过来！今天给大家{product_info.get('key_feature', '推荐')}这款{product_name}！

【痛点共鸣】
你是不是也遇到过：{'、'.join(persona.pain_points[:2]) if persona.pain_points else '选择困难'}？

【解决方案】
{product_name}帮你一站式解决！
✅ {key_feature}
✅ {'、'.join(persona.purchase_drivers[:2]) if persona.purchase_drivers else '品质保障'}
✅ 仅需{price}

【行动引导】
左下角小黄车，限时优惠，赶紧冲！"""

        elif platform == PlatformStyle.TAOBAO.value:
            return f"""【品牌介绍】
{product_info.get('brand', '品牌')}——{product_info.get('brand_desc', '专注品质生活')}

【产品详情】
产品名称：{product_name}
核心功能：{key_feature}
适用场景：{'、'.join(persona.top_interests[:3]) if persona.top_interests else '多种场景'}

【核心优势】
1. {product_info.get('key_feature', '核心功能')}
2. {persona.purchase_drivers[0] if persona.purchase_drivers else '品质保障'}
3. {product_info.get('certification', '权威认证')}

【用户评价】
好评率98%，{'、'.join(persona.top_interests[:2])}用户强烈推荐

【售后保障】
7天无理由退换 | 正品保障 | 全国联保"""

        elif platform == PlatformStyle.PINDUODUO.value:
            return f"""💰 超值推荐 | {product_name}

原价：¥{product_info.get('original_price', 'XXX')}
拼团价：¥{price}
立省：¥{product_info.get('discount', 'XX')}

🔥 为什么选择我们？
→ {key_feature}
→ {persona.purchase_drivers[0] if persona.purchase_drivers else '品质保证'}
→ 万人已拼，好评如潮

⏰ 限时特惠，错过再等一年！
📦 今天下单，明天到家
🔄 不满意？包退！"""

        return f"{product_name}\n{key_feature}\n价格：{price}"

    def _generate_image_copy(self, platform: str, persona: UserPersona, product_info: dict, template: dict) -> list:
        product_name = product_info.get("name", "商品")
        price = product_info.get("price", "")

        if platform == PlatformStyle.DOUYIN.value:
            return [
                f"封面：{persona.top_interests[0]}必入！{product_name}",
                f"卖点图1：3秒{product_info.get('key_feature', '')}效果对比",
                f"卖点图2：{price}不到奶茶钱",
                f"转化图：左下角下单→今日发货"
            ]

        elif platform == PlatformStyle.TAOBAO.value:
            return [
                f"主图：{product_name} 官方正品",
                f"卖点图1：{product_info.get('key_feature', '')}技术解析",
                f"卖点图2：{' + '.join(persona.top_interests[:3])}",
                f"卖点图3：权威认证展示",
                f"转化图：已售10万+ 好评率98%"
            ]

        elif platform == PlatformStyle.PINDUODUO.value:
            return [
                f"主图：¥{price} | 万人拼团",
                f"卖点图1：比淘宝便宜30%",
                f"卖点图2：{product_info.get('key_feature', '')} 品质保证",
                f"转化图：今天下单 明天到家"
            ]

        return [f"{product_name} 主图"]
