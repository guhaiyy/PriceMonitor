#!/usr/bin/env python3
"""
价格分析器 - 智能分析价格趋势
"""

import statistics
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class PriceAnalyzer:
    """价格分析器"""

    def __init__(self):
        self.history = {}

    def add_price(self, product_id: str, price: float, timestamp: float = None):
        """添加价格记录"""
        if timestamp is None:
            timestamp = datetime.now().timestamp()

        if product_id not in self.history:
            self.history[product_id] = []

        self.history[product_id].append({
            'price': price,
            'timestamp': timestamp
        })

        # 只保留最近90天
        cutoff = datetime.now().timestamp() - 90 * 24 * 60 * 60
        self.history[product_id] = [
            p for p in self.history[product_id]
            if p['timestamp'] > cutoff
        ]

    def analyze(self, product_id: str) -> Dict:
        """分析价格"""
        if product_id not in self.history or not self.history[product_id]:
            return {
                'product_id': product_id,
                'status': 'no_data'
            }

        prices = self.history[product_id]
        current_price = prices[-1]['price']
        price_values = [p['price'] for p in prices]

        # 统计分析
        analysis = {
            'product_id': product_id,
            'status': 'analyzed',
            'current_price': current_price,
            'price_count': len(prices),
            'min_price': min(price_values),
            'max_price': max(price_values),
            'avg_price': statistics.mean(price_values),
            'median_price': statistics.median(price_values),
            'std_dev': statistics.stdev(price_values) if len(price_values) > 1 else 0,
        }

        # 趋势分析
        if len(prices) >= 3:
            # 最近7天趋势
            week_ago = datetime.now().timestamp() - 7 * 24 * 60 * 60
            recent_prices = [p['price'] for p in prices if p['timestamp'] > week_ago]

            if recent_prices:
                if len(recent_prices) >= 2:
                    first_week = recent_prices[0]
                    last_week = recent_prices[-1]
                    week_change = ((last_week - first_week) / first_week) * 100
                    analysis['week_change'] = round(week_change, 2)

                # 最近30天趋势
                month_ago = datetime.now().timestamp() - 30 * 24 * 60 * 60
                month_prices = [p['price'] for p in prices if p['timestamp'] > month_ago]

                if month_prices:
                    if len(month_prices) >= 2:
                        first_month = month_prices[0]
                        last_month = month_prices[-1]
                        month_change = ((last_month - first_month) / first_month) * 100
                        analysis['month_change'] = round(month_change, 2)

        # 价格位置分析
        if analysis['min_price'] < analysis['max_price']:
            price_position = (current_price - analysis['min_price']) / (analysis['max_price'] - analysis['min_price'])
            analysis['price_position'] = round(price_position, 3)

            # 判断是否是好价
            analysis['is_good_deal'] = price_position < 0.3  # 价格在最低30%
            analysis['is_bad_deal'] = price_position > 0.8  # 价格在最高20%

        # 波动性分析
        if analysis['std_dev']:
            cv = analysis['std_dev'] / analysis['avg_price']  # 变异系数
            analysis['volatility'] = round(cv, 3)

            if cv < 0.05:
                analysis['volatility_level'] = 'stable'
            elif cv < 0.15:
                analysis['volatility_level'] = 'normal'
            else:
                analysis['volatility_level'] = 'high'

        return analysis

    def get_recommendation(self, product_id: str, target_price: float = None) -> Dict:
        """获取购买建议"""
        analysis = self.analyze(product_id)

        if analysis['status'] == 'no_data':
            return {
                'product_id': product_id,
                'recommendation': 'wait',
                'reason': 'no_data',
                'confidence': 0
            }

        current = analysis['current_price']

        # 基于目标价
        if target_price:
            if current <= target_price:
                return {
                    'product_id': product_id,
                    'recommendation': 'buy_now',
                    'reason': 'below_target_price',
                    'confidence': 0.9,
                    'savings': target_price - current
                }
            else:
                gap = current - target_price
                return {
                    'product_id': product_id,
                    'recommendation': 'wait',
                    'reason': 'above_target_price',
                    'confidence': 0.8,
                    'gap': gap,
                    'gap_percent': round((gap / current) * 100, 1)
                }

        # 基于历史价格
        if 'price_position' in analysis:
            position = analysis['price_position']
            volatility = analysis.get('volatility', 0)

            if position < 0.2:
                return {
                    'product_id': product_id,
                    'recommendation': 'buy_now',
                    'reason': 'historic_low',
                    'confidence': 0.85 - volatility * 2,
                    'price_position': position
                }
            elif position < 0.4:
                return {
                    'product_id': product_id,
                    'recommendation': 'consider',
                    'reason': 'good_price',
                    'confidence': 0.7 - volatility,
                    'price_position': position
                }
            elif position > 0.8:
                return {
                    'product_id': product_id,
                    'recommendation': 'avoid',
                    'reason': 'historic_high',
                    'confidence': 0.6,
                    'price_position': position
                }
            else:
                return {
                    'product_id': product_id,
                    'recommendation': 'wait',
                    'reason': 'average_price',
                    'confidence': 0.5,
                    'price_position': position
                }

        return {
            'product_id': product_id,
            'recommendation': 'wait',
            'reason': 'insufficient_data',
            'confidence': 0.3
        }

    def predict_price(self, product_id: str, days_ahead: int = 7) -> Optional[float]:
        """预测未来价格（简单线性趋势）"""
        if product_id not in self.history or len(self.history[product_id]) < 5:
            return None

        prices = self.history[product_id]
        price_values = [p['price'] for p in prices]

        # 简单线性回归
        n = len(price_values)
        sum_x = sum(range(n))
        sum_y = sum(price_values)
        sum_xy = sum(i * price_values[i] for i in range(n))
        sum_x2 = sum(i * i for i in range(n))

        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        intercept = (sum_y - slope * sum_x) / n

        # 预测
        future_x = n + days_ahead
        predicted_price = slope * future_x + intercept

        return max(0, predicted_price)  # 价格不能为负

    def compare_products(self, product_ids: List[str]) -> Dict:
        """对比多个产品"""
        results = []

        for pid in product_ids:
            analysis = self.analyze(pid)
            if analysis['status'] == 'analyzed':
                results.append({
                    'product_id': pid,
                    'price': analysis['current_price'],
                    'price_position': analysis.get('price_position', 0.5),
                    'is_good_deal': analysis.get('is_good_deal', False),
                })

        # 排序
        results.sort(key=lambda x: x['price'])

        return {
            'cheapest': results[0] if results else None,
            'best_deal': max(results, key=lambda x: x['price_position']) if results else None,
            'all': results
        }


# 使用示例
if __name__ == "__main__":
    analyzer = PriceAnalyzer()

    print("📊 价格分析器测试")
    print("=" * 60)

    # 模拟价格历史
    product_id = "test_product"

    # 添加30天的价格数据
    import random
    for day in range(30):
        # 价格在 1000-2000 之间波动
        price = 1500 + random.uniform(-300, 300)
        timestamp = datetime.now().timestamp() - (29 - day) * 24 * 60 * 60
        analyzer.add_price(product_id, price, timestamp)

    # 分析
    print("\n📈 价格分析:")
    analysis = analyzer.analyze(product_id)
    for key, value in analysis.items():
        if key != 'product_id':
            print(f"  {key}: {value}")

    # 获取建议
    print("\n💡 购买建议:")
    recommendation = analyzer.get_recommendation(product_id, target_price=1400)
    for key, value in recommendation.items():
        if key != 'product_id':
            print(f"  {key}: {value}")

    # 预测未来价格
    print("\n🔮 价格预测:")
    for days in [1, 3, 7]:
        predicted = analyzer.predict_price(product_id, days)
        if predicted:
            print(f"  {days}天后: ¥{predicted:.2f}")

    print("\n" + "=" * 60)
    print("💡 功能说明:")
    print("1. 趋势分析: 分析价格变化趋势")
    print("2. 购买建议: 基于历史数据给出建议")
    print("3. 价格预测: 预测未来价格")
    print("4. 产品对比: 对比多个产品的性价比")
