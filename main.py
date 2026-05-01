import logging
import sys
from src.core.orchestrator import AgentOrchestrator
from src.data.mock_data import (
    generate_mock_orders,
    generate_mock_reviews,
    get_mock_product_info,
    get_mock_historical_data,
)


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def main():
    setup_logging()

    orders = generate_mock_orders(n=500)
    reviews = generate_mock_reviews(n=300)
    product_info = get_mock_product_info()
    historical_data = get_mock_historical_data()

    channels = ["douyin", "taobao", "pinduoduo"]
    platforms = ["douyin", "taobao", "pinduoduo"]

    orchestrator = AgentOrchestrator(historical_data=historical_data)

    result = orchestrator.run(
        orders=orders,
        reviews=reviews,
        channels=channels,
        product_info=product_info,
        platforms=platforms
    )

    orchestrator.export_report("output/report.json")

    return result


if __name__ == "__main__":
    main()
