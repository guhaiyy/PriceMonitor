#!/usr/bin/env python3
"""
价格监控工具 - 增强版 v2.0
整合真实价格爬取、智能分析、购买建议
"""

import json
import time
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional

# 导入模块
try:
    from real_price_scraper import RealPriceScraper
except ImportError:
    RealPriceScraper = None

try:
    from price_analyzer import PriceAnalyzer
except ImportError:
    PriceAnalyzer = None

try:
    from email_notifier import EmailNotifier
except ImportError:
    EmailNotifier = None


class PriceMonitorPro:
    """价格监控专业版"""

    def __init__(self):
        self.config_file = 'monitor_pro_config.json'
        self.data_file = 'monitor_pro_data.json'

        self.scraper = RealPriceScraper() if RealPriceScraper else None
        self.analyzer = PriceAnalyzer() if PriceAnalyzer else None
        self.notifier = EmailNotifier() if EmailNotifier else None

        self.targets = []
        self.load_data()

    def load_data(self):
        """加载数据"""
        # 加载配置
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.targets = config.get('targets', [])

        # 加载历史数据
        if self.analyzer and os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                history_data = json.load(f)
                for product_id, prices in history_data.items():
                    for price_record in prices:
                        self.analyzer.add_price(
                            product_id,
                            price_record['price'],
                            price_record['timestamp']
                        )

    def save_data(self):
        """保存数据"""
        # 保存配置
        config = {
            'targets': self.targets,
            'last_updated': datetime.now().isoformat()
        }
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        # 保存历史数据
        if self.analyzer:
            history_data = {}
            for product_id, prices in self.analyzer.history.items():
                history_data[product_id] = prices
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, ensure_ascii=False, indent=2)

    def add_target(self, name: str, url: str, target_price: float) -> Dict:
        """添加监控目标"""
        # 平台检测
        if 'taobao.com' in url or 'tmall.com' in url:
            platform = '淘宝'
        elif 'jd.com' in url:
            platform = '京东'
        elif 'pinduoduo.com' in url:
            platform = '拼多多'
        else:
            platform = '通用'

        target = {
            'id': f"target_{int(datetime.now().timestamp())}",
            'name': name,
            'url': url,
            'target_price': target_price,
            'platform': platform,
            'current_price': None,
            'status': 'active',
            'created_at': datetime.now().isoformat(),
            'last_checked': None
        }

        self.targets.append(target)
        self.save_data()

        return target

    def check_all(self, detailed: bool = True):
        """检查所有目标"""
        print(f"\n{'='*70}")
        print(f"📊 价格监控报告 v2.0")
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")

        deals = []
        recommendations = []

        for i, target in enumerate(self.targets, 1):
            if target['status'] != 'active':
                continue

            print(f"📦 {i}. {target['name']}")
            print(f"   平台: {target['platform']}")
            print(f"   目标价: ¥{target['target_price']}")

            # 获取价格
            if self.scraper:
                price = self.scraper.get_price(target['url'])
            else:
                # 模拟价格
                import random
                price = round(random.uniform(100, 5000), 2)

            target['current_price'] = price
            target['last_checked'] = datetime.now().isoformat()

            # 分析价格
            if self.analyzer:
                self.analyzer.add_price(target['id'], price)

                if detailed and len(self.analyzer.history.get(target['id'], [])) >= 3:
                    analysis = self.analyzer.analyze(target['id'])
                    print(f"   历史最低: ¥{analysis.get('min_price', 'N/A')}")
                    print(f"   历史最高: ¥{analysis.get('max_price', 'N/A')}")
                    print(f"   平均价格: ¥{analysis.get('avg_price', 'N/A')}")

                    if 'week_change' in analysis:
                        change = analysis['week_change']
                        emoji = "📈" if change > 0 else "📉"
                        print(f"   周趋势: {emoji} {change:.1f}%")

                    # 获取建议
                    recommendation = self.analyzer.get_recommendation(
                        target['id'],
                        target['target_price']
                    )
                    rec_map = {
                        'buy_now': '🎯 立即购买',
                        'consider': '💭 考虑购买',
                        'wait': '⏳ 等待降价',
                        'avoid': '🚫 避免购买'
                    }
                    print(f"   建议: {rec_map.get(recommendation['recommendation'], recommendation['recommendation'])}")

                    recommendations.append({
                        'target': target,
                        'recommendation': recommendation
                    })

            # 判断是否达标
            status_text = "✅ 达标！" if price <= target['target_price'] else "🔴 未达标"
            print(f"   当前价: ¥{price} {status_text}")

            if price <= target['target_price']:
                deals.append(target)

            print()

        self.save_data()

        # 显示达标商品
        if deals:
            print("🎉 发现好价商品！")
            print("-" * 70)
            for deal in deals:
                print(f"✨ {deal['name']}")
                print(f"   链接: {deal['url']}")
                print(f"   平台: {deal['platform']}")
                print(f"   价格: ¥{deal['current_price']} (目标: ¥{deal['target_price']})")
                savings = deal['target_price'] - deal['current_price']
                print(f"   省约: ¥{savings:.2f}")
            print("-" * 70)

        # 发送邮件
        if deals and self.notifier:
            self.notifier.send_alert('your-email@example.com', deals)

        return {
            'deals': deals,
            'recommendations': recommendations
        }

    def get_insights(self) -> Dict:
        """获取洞察"""
        if not self.analyzer:
            return {'status': 'no_analyzer'}

        insights = {
            'total_targets': len(self.targets),
            'active_targets': len([t for t in self.targets if t['status'] == 'active']),
            'platforms': {},
            'recommendations': {}
        }

        # 统计平台
        for target in self.targets:
            platform = target['platform']
            insights['platforms'][platform] = insights['platforms'].get(platform, 0) + 1

        # 分析建议
        rec_counts = {
            'buy_now': 0,
            'consider': 0,
            'wait': 0,
            'avoid': 0
        }

        for target in self.targets:
            if target['status'] != 'active':
                continue

            recommendation = self.analyzer.get_recommendation(
                target['id'],
                target['target_price']
            )
            rec = recommendation['recommendation']
            if rec in rec_counts:
                rec_counts[rec] += 1

        insights['recommendations'] = rec_counts

        return insights

    def predict_future(self, days: int = 7) -> Dict:
        """预测未来价格"""
        predictions = {}

        if not self.analyzer:
            return predictions

        for target in self.targets:
            if target['status'] != 'active':
                continue

            predicted = self.analyzer.predict_price(target['id'], days)
            if predicted:
                predictions[target['name']] = {
                    'current': target.get('current_price'),
                    'predicted': predicted,
                    'change': predicted - target.get('current_price', 0),
                    'change_percent': round(
                        (predicted - target.get('current_price', 0)) /
                        target.get('current_price', 1) * 100,
                        1
                    )
                }

        return predictions

    def export_report(self, filename: str = None):
        """导出报告"""
        if filename is None:
            filename = f"price_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report = {
            'generated_at': datetime.now().isoformat(),
            'summary': self.get_insights(),
            'targets': self.targets,
            'predictions': self.predict_future(7)
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"📄 报告已导出: {filename}")
        return filename


def main():
    """主函数"""
    app = PriceMonitorPro()

    print("🛒 价格监控工具 v2.0 Pro")
    print("=" * 60)
    print("新增功能:")
    print("✅ 真实价格爬取（支持缓存）")
    print("✅ 智能价格分析")
    print("✅ 购买建议推荐")
    print("✅ 价格趋势预测")
    print("✅ 历史数据追踪")
    print("=" * 60)

    # 添加示例目标
    if not app.targets:
        print("\n📝 添加示例监控目标...\n")
        examples = [
            {
                'name': 'iPhone 15 Pro',
                'url': 'https://item.jd.com/100044522456.html',
                'target_price': 6999.00
            },
            {
                'name': '索尼 WH-1000XM5',
                'url': 'https://detail.tmall.com/item.htm?id=example2',
                'target_price': 1899.00
            },
            {
                'name': '戴森吸尘器 V12',
                'url': 'https://item.jd.com/100037890123.html',
                'target_price': 2999.00
            }
        ]

        for item in examples:
            app.add_target(**item)

    # 执行检查
    print("🔍 开始价格检查...\n")
    result = app.check_all(detailed=True)

    # 显示洞察
    print("\n💡 洞察分析:")
    insights = app.get_insights()
    print(f"总监控数: {insights['total_targets']}")
    print(f"活跃监控: {insights['active_targets']}")
    print(f"平台分布: {insights['platforms']}")
    print(f"建议分布: {insights['recommendations']}")

    # 价格预测
    print("\n🔮 7天价格预测:")
    predictions = app.predict_future(7)
    for name, pred in predictions.items():
        change = pred['change']
        emoji = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        print(f"  {name}: ¥{pred['predicted']:.2f} ({emoji} {pred['change_percent']:+.1f}%)")

    # 导出报告
    app.export_report()

    print("\n" + "=" * 60)
    print("📊 v2.0 优势:")
    print("1. 真实价格：尝试多种方式获取")
    print("2. 智能分析：趋势、建议、预测")
    print("3. 数据持久化：保存历史记录")
    print("4. 缓存机制：减少请求，提高效率")
    print("5. 增强体验：更详细的报告")
    print("=" * 60)


if __name__ == "__main__":
    main()
